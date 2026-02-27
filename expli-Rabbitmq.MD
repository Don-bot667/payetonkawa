# RabbitMQ — Guide complet PayeTonKawa

---

## Table des matières

1. [C'est quoi RabbitMQ et pourquoi on l'utilise ?](#1-cest-quoi-rabbitmq-et-pourquoi-on-lutilise)
2. [Le vocabulaire expliqué simplement](#2-le-vocabulaire-expliqué-simplement)
3. [Comment RabbitMQ est intégré dans le projet](#3-comment-rabbitmq-est-intégré-dans-le-projet)
4. [Les étapes de mise en place](#4-les-étapes-de-mise-en-place)
5. [Lancer le projet et tester](#5-lancer-le-projet-et-tester)
6. [Comprendre l'interface web localhost:15672](#6-comprendre-linterface-web-localhost15672)

---

## 1. C'est quoi RabbitMQ et pourquoi on l'utilise ?

### Le problème de départ

Dans PayeTonKawa, on a **3 APIs complètement séparées**, chacune avec **sa propre base de données** :

```
api-clients   →  base clients_db   (port 5436)
api-produits  →  base produits_db  (port 5437)
api-commandes →  base commandes_db (port 5438)
```

Ces 3 bases ne se voient pas. Elles ne peuvent pas se lire entre elles.

**Exemple concret du problème :**

Imagine ce scénario :

```
1. Jean passe une commande → commandes_db enregistre : commande n°5, client_id = 3
2. Jean supprime son compte → clients_db supprime le client n°3
3. commandes_db ne sait rien de cette suppression
4. La commande n°5 pointe maintenant vers un client qui n'existe plus
   → C'est une commande fantôme, incohérente
```

Sans solution de communication, `api-commandes` ne saura jamais ce qui se passe dans `api-clients`. Les données deviennent incohérentes.

---

### La solution : RabbitMQ

RabbitMQ est un **système de messagerie**. Imagine une boîte aux lettres centrale dans un immeuble :

- Quand quelque chose d'important arrive dans un service, il **dépose un message** dans la boîte aux lettres
- Les autres services qui sont intéressés **viennent lire la boîte** et réagissent

```
SANS RabbitMQ :
  api-clients supprime un client
  → api-commandes ne sait rien
  → commandes fantômes dans la base

AVEC RabbitMQ :
  api-clients supprime le client 3
  → dépose le message "client.deleted : id=3" dans RabbitMQ
  → api-commandes lit le message
  → api-commandes marque les commandes du client 3 comme "client_supprime"
  → plus de données incohérentes
```

**Point clé :** les services ne se parlent pas directement entre eux. Ils communiquent uniquement via RabbitMQ. C'est ce qu'on appelle la **communication asynchrone** : `api-clients` n'attend pas qu'`api-commandes` réponde. Elle publie le message et continue immédiatement son travail.

---

### Pourquoi c'est obligatoire pour ce projet ?

Le sujet MSPR impose une architecture microservices. L'un des critères d'évaluation est que les services **communiquent entre eux**. Sans RabbitMQ, chaque service est une île isolée. Avec RabbitMQ, on prouve que l'architecture est cohérente et que les données restent synchronisées entre les services.

---

## 2. Le vocabulaire expliqué simplement

Avant de continuer, voici les termes importants expliqués avec des analogies simples :

| Terme | Analogie | Rôle dans le projet |
|-------|----------|---------------------|
| **Producer** | L'expéditeur qui envoie une lettre | api-clients, api-produits, api-commandes qui publient des messages |
| **Consumer** | Le destinataire qui reçoit et lit la lettre | consumer-commandes qui traite les messages |
| **Exchange** | Le bureau de tri de La Poste | Reçoit tous les messages et les redirige selon leur étiquette |
| **Queue** | La boîte aux lettres | File d'attente où les messages patientent avant d'être lus |
| **Routing Key** | L'adresse sur l'enveloppe | Etiquette du message : `client.deleted`, `produit.stock_low`, etc. |
| **Binding** | La règle de redirection | "Les lettres avec l'étiquette `client.deleted` vont dans la boîte `commandes_client_events`" |

**Exemple avec une analogie complète :**

```
api-clients (expéditeur)
  → écrit une lettre : { "event": "client_deleted", "client_id": 3 }
  → colle l'étiquette : "client.deleted"
  → la dépose dans la boîte centrale (Exchange "payetonkawa")

Exchange "payetonkawa" (bureau de tri)
  → reçoit la lettre
  → voit l'étiquette "client.deleted"
  → consulte ses règles (Bindings) : client.deleted → queue commandes_client_events
  → dépose la lettre dans la bonne boîte aux lettres

Queue "commandes_client_events" (boîte aux lettres)
  → conserve la lettre jusqu'à ce que quelqu'un la lise

consumer-commandes (destinataire)
  → surveille en permanence la boîte
  → prend la lettre, lit le contenu
  → marque les commandes du client 3 comme "client_supprime"
```

---

## 3. Comment RabbitMQ est intégré dans le projet

### Vue d'ensemble de l'architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   api-clients   │    │  api-produits   │    │  api-commandes  │
│   (port 8000)   │    │  (port 8001)    │    │  (port 8002)    │
│                 │    │                 │    │                 │
│ publie :        │    │ publie :        │    │ publie :        │
│ client.created  │    │ produit.created │    │ commande.created│
│ client.updated  │    │ produit.updated │    │ commande.updated│
│ client.deleted  │    │ produit.deleted │    │ commande.deleted│
│                 │    │ produit.stock_low    │                 │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                     │                       │
         └─────────────────────┼───────────────────────┘
                               │ tous publient ici
                               ▼
              ┌────────────────────────────────┐
              │   RABBITMQ (port 5672)         │
              │   Exchange : "payetonkawa"     │
              │   Type : topic (par étiquette) │
              │                                │
              │   Règles (Bindings) :          │
              │   client.deleted  → queue A    │
              │   produit.deleted → queue B    │
              └──────────────┬─────────────────┘
                             │
              ┌──────────────┴─────────────────┐
              │                                │
              ▼                                ▼
   Queue: commandes_client_events   Queue: commandes_produit_events
   (écoute: client.deleted)         (écoute: produit.deleted)
              │                                │
              └──────────────┬─────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  consumer-commandes  │
                  │                      │
                  │ Si client.deleted    │
                  │ → marque commandes   │
                  │   "client_supprime"  │
                  │                      │
                  │ Si produit.deleted   │
                  │ → log l'information  │
                  └──────────────────────┘
```

### Les fichiers créés ou modifiés

| Fichier | Ce qu'il fait |
|---------|---------------|
| `api-clients/app/rabbitmq.py` | Envoie les messages quand un client change |
| `api-produits/app/rabbitmq.py` | Envoie les messages quand un produit change |
| `api-commandes/app/rabbitmq.py` | Envoie les messages quand une commande change |
| `api-commandes/app/consumer.py` | Ecoute et réagit aux messages reçus |
| `api-clients/app/routes.py` | Appelle rabbitmq.py après chaque action CRUD |
| `api-produits/app/routes.py` | Appelle rabbitmq.py après chaque action CRUD |
| `api-commandes/app/routes.py` | Appelle rabbitmq.py après chaque action CRUD |
| `docker-compose.yml` | Ajoute le service `consumer-commandes` et `rabbitmq` |

---

## 4. Les étapes de mise en place

### Etape 1 — Ajouter la dépendance pika

`pika` est la librairie Python qui permet de parler à RabbitMQ. Sans elle, Python ne saurait pas comment se connecter.

Elle a été ajoutée dans les 3 fichiers `requirements.txt` des APIs :

```
# Dans api-clients/requirements.txt
# Dans api-produits/requirements.txt
# Dans api-commandes/requirements.txt

pika==1.3.2
```

**Pourquoi dans les 3 ?** Parce que chaque API a besoin d'envoyer des messages.

---

### Etape 2 — Créer le fichier rabbitmq.py dans chaque API

Chaque API possède un fichier `app/rabbitmq.py`. Ce fichier a deux responsabilités :

**Responsabilité 1 : Se connecter à RabbitMQ**

```python
def get_connection():
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        return pika.BlockingConnection(parameters)
    except Exception as e:
        logger.error(f"Erreur connexion RabbitMQ: {e}")
        return None  # Retourne None sans faire planter l'API
```

Si RabbitMQ est éteint, la fonction retourne `None` au lieu de faire crasher toute l'API. L'API continue de fonctionner normalement, elle envoie juste moins de messages.

**Responsabilité 2 : Envoyer les messages**

```python
def publish_message(routing_key: str, message: dict):
    connection = get_connection()
    if not connection:
        return False  # RabbitMQ down → on abandonne silencieusement

    channel = connection.channel()
    channel.exchange_declare(exchange="payetonkawa", exchange_type="topic", durable=True)
    channel.basic_publish(
        exchange="payetonkawa",
        routing_key=routing_key,   # ex: "client.deleted"
        body=json.dumps(message),  # le contenu JSON du message
        properties=pika.BasicProperties(delivery_mode=2)  # message persistant
    )
    connection.close()
```

`delivery_mode=2` signifie que le message est **persistant** : même si RabbitMQ redémarre, le message ne sera pas perdu.

**Les fonctions spécifiques à chaque service :**

Pour api-clients (`app/rabbitmq.py`) :
```python
# Appelée quand on crée un client (POST /customers/)
publish_client_created(client_id=3, data={"nom": "Jean", "email": "jean@test.com"})
# → envoie le message avec l'étiquette "client.created"

# Appelée quand on modifie un client (PUT /customers/3)
publish_client_updated(client_id=3, data={"nom": "Jean-Pierre", "email": "jean@test.com"})
# → envoie le message avec l'étiquette "client.updated"

# Appelée quand on supprime un client (DELETE /customers/3)
publish_client_deleted(client_id=3)
# → envoie le message avec l'étiquette "client.deleted"
```

Pour api-produits (`app/rabbitmq.py`) :
```python
publish_produit_created(produit_id=1, data={"nom": "Café Kenya", "prix": 12.50})
publish_produit_updated(produit_id=1, data={"nom": "Café Kenya", "prix": 11.00})
publish_produit_deleted(produit_id=1)

# Cas spécial : alerte si le stock tombe sous 10 unités
publish_produit_stock_low(produit_id=1, produit_nom="Café Kenya", stock=4)
# → envoie le message avec l'étiquette "produit.stock_low"
```

Pour api-commandes (`app/rabbitmq.py`) :
```python
publish_commande_created(commande_id=5, data={"client_id": 3, "total": 25.00})
publish_commande_updated(commande_id=5, statut="expediee")
publish_commande_deleted(commande_id=5)
```

---

### Etape 3 — Brancher RabbitMQ dans les routes

Dans chaque `routes.py`, après chaque opération, on appelle la fonction correspondante du fichier `rabbitmq.py`.

**Règle importante :** on sauvegarde en base D'ABORD, puis on publie le message. Jamais l'inverse.

```python
# DANS api-clients/app/routes.py

from . import rabbitmq  # on importe le module

@router.post("/customers/")
def create_customer(client, db):
    # Etape 1 : on sauvegarde en base PostgreSQL
    db_client = crud.create_client(db, client)

    # Etape 2 : si la sauvegarde a réussi, on envoie le message
    rabbitmq.publish_client_created(db_client.id, {
        "nom": db_client.nom,
        "email": db_client.email
    })

    # Etape 3 : on retourne le client créé au frontend
    return db_client
```

Pourquoi dans cet ordre ? Si la base de données échoue (ex: email déjà utilisé), l'opération s'arrête à l'étape 1 et on ne publie jamais de faux message.

**Exemple pour le DELETE :**

```python
@router.delete("/customers/{client_id}")
def delete_customer(client_id, db):
    # Etape 1 : on supprime de la base
    success = crud.delete_client(db, client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client non trouvé")

    # Etape 2 : la suppression a réussi → on prévient les autres services
    rabbitmq.publish_client_deleted(client_id)
    # api-commandes va recevoir ce message et agir
```

**Exemple spécial pour le stock bas dans api-produits :**

```python
@router.put("/products/{produit_id}")
def update_product(produit_id, produit, db):
    db_produit = crud.update_produit(db, produit_id, produit)

    # On publie la mise à jour du produit
    rabbitmq.publish_produit_updated(db_produit.id, {"stock": db_produit.stock})

    # En plus : si le stock est trop bas, on envoie une alerte séparée
    if db_produit.stock < 10:
        rabbitmq.publish_produit_stock_low(db_produit.id, db_produit.nom, db_produit.stock)

    return db_produit
```

---

### Etape 4 — Créer le Consumer dans api-commandes

Le fichier `api-commandes/app/consumer.py` est le seul qui **écoute** des messages. Les autres fichiers `rabbitmq.py` envoient des messages, lui les reçoit.

Il fonctionne en boucle infinie : il reste connecté à RabbitMQ et attend.

```
consumer-commandes démarre
→ se connecte à RabbitMQ
→ déclare qu'il écoute les queues :
    commandes_client_events (messages : client.deleted)
    commandes_produit_events (messages : produit.deleted)
→ attend...
→ attend...
→ reçoit "client.deleted : client_id=3"
    → ouvre la base commandes_db
    → récupère toutes les commandes du client 3
    → change leur statut en "client_supprime"
    → confirme à RabbitMQ que le message est traité (ack)
→ attend...
→ attend...
```

**Réaction quand un client est supprimé :**

```python
def callback_client_deleted(ch, method, properties, body):
    data = json.loads(body)
    client_id = data.get("client_id")  # ex: 3

    db = SessionLocal()
    commandes = crud.get_commandes_by_client(db, client_id)
    # ex: commandes = [commande n°5, commande n°8]

    for commande in commandes:
        crud.update_commande_statut(db, commande.id, "client_supprime")
    # commande n°5 → statut = "client_supprime"
    # commande n°8 → statut = "client_supprime"

    ch.basic_ack(delivery_tag=method.delivery_tag)
    # confirme à RabbitMQ : "message bien reçu et traité, tu peux l'effacer"
```

Si une erreur se produit, on envoie un `nack` (not acknowledged) et RabbitMQ remet le message en queue pour le retraiter plus tard.

---

### Etape 5 — Ajouter le consumer dans docker-compose.yml

Le consumer est un **processus séparé** de l'API. Il a son propre service dans `docker-compose.yml`.

```yaml
consumer-commandes:
  build: ./api-commandes        # utilise le même code qu'api-commandes
  command: python -m app.consumer  # mais lance consumer.py, pas l'API FastAPI
  environment:
    DATABASE_URL: postgresql://faouz:faouz2020@db-commandes:5432/commandes_db
    RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  depends_on:
    - db-commandes   # attend que la base soit prête
    - rabbitmq       # attend que RabbitMQ soit prêt
  restart: unless-stopped  # redémarre automatiquement si le consumer crash
```

Pourquoi un service séparé et pas intégré dans api-commandes ?

```
Si on intégrait le consumer dans l'API FastAPI :
→ Un seul processus gèrerait à la fois les requêtes HTTP ET les messages RabbitMQ
→ Un message long à traiter bloquerait les requêtes HTTP
→ Un crash du consumer tuerait aussi l'API

Avec un service séparé :
→ L'API répond aux requêtes HTTP sans être bloquée
→ Le consumer traite les messages en parallèle
→ Si le consumer crash, l'API continue de fonctionner
→ restart: unless-stopped redémarre le consumer automatiquement
```

---

## 5. Lancer le projet et tester

### Lancer tout le projet

```bash
# Depuis le dossier payetonkawa/
docker compose up -d
```

Cela démarre les 8 services en même temps :
- `db-clients`, `db-produits`, `db-commandes` (les 3 bases PostgreSQL)
- `api-clients`, `api-produits`, `api-commandes` (les 3 APIs)
- `rabbitmq` (le message broker)
- `consumer-commandes` (le consumer)

**Vérifier que tout est démarré :**

```bash
docker compose ps
```

Tous les services doivent afficher `running`.

---

### Important : reconstruire les images après modification du code

Quand tu modifies du code Python, Docker ne le voit pas automatiquement. Il faut reconstruire les images :

```bash
# Reconstruire les images
docker compose build api-clients api-produits api-commandes

# Puis redémarrer les conteneurs avec le nouveau code
docker compose up -d api-clients api-produits api-commandes consumer-commandes
```

---

### Test 1 — Vérifier que RabbitMQ reçoit les messages

**Etape 1 :** Crée un nouveau client

```bash
curl -X POST http://localhost:8000/customers/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: secret_key_123" \
  -d '{
    "nom": "Dupont",
    "prenom": "Jean",
    "email": "jean.dupont@test.com",
    "telephone": "0612345678"
  }'
```

Réponse attendue :
```json
{
  "id": 1,
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean.dupont@test.com",
  "actif": true
}
```

**Etape 2 :** Va sur `http://localhost:15672` → **Exchanges** → **payetonkawa**

Tu vois un pic sur le graphique **"Publish (In)"** à l'heure exacte de la création. Cela confirme qu'un message `client.created` a bien été envoyé.

---

### Test 2 — Vérifier que le consumer réagit à une suppression

Ce test démontre le scénario complet : créer un client, lui créer une commande, le supprimer, et vérifier que sa commande change automatiquement de statut.

**Etape 1 :** Crée un client (note son `id`, ex: `id = 1`)

```bash
curl -X POST http://localhost:8000/customers/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: secret_key_123" \
  -d '{"nom": "Martin", "prenom": "Sophie", "email": "sophie@test.com", "telephone": "0698765432"}'
```

**Etape 2 :** Crée une commande pour ce client

```bash
curl -X POST http://localhost:8002/orders/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: secret_key_123" \
  -d '{
    "client_id": 1,
    "lignes": [{"produit_id": 1, "quantite": 2, "prix_unitaire": 9.99}]
  }'
```

Réponse : la commande a `"statut": "en_attente"` et un `id`, ex: `id = 5`

**Etape 3 :** Vérifie le statut de la commande (il doit être `en_attente`)

```bash
curl http://localhost:8002/orders/5 -H "X-API-Key: secret_key_123"
```

**Etape 4 :** Supprime le client

```bash
curl -X DELETE http://localhost:8000/customers/1 -H "X-API-Key: secret_key_123"
```

Réponse : code `204` (suppression réussie, sans contenu)

**Etape 5 :** Revérifie la commande

```bash
curl http://localhost:8002/orders/5 -H "X-API-Key: secret_key_123"
```

Résultat attendu :
```json
{
  "id": 5,
  "client_id": 1,
  "statut": "client_supprime",   ← automatiquement mis à jour par le consumer !
  "total": 19.98
}
```

La commande est passée de `en_attente` à `client_supprime` automatiquement, sans qu'on ait rien fait manuellement. C'est RabbitMQ + le consumer qui ont fait le travail.

---

### Test 3 — Vérifier l'alerte stock bas

**Etape 1 :** Met le stock d'un produit à une valeur inférieure à 10

```bash
curl -X PUT http://localhost:8001/products/1 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: secret_key_123" \
  -d '{"stock": 5}'
```

**Etape 2 :** Va sur `http://localhost:15672` → **Exchanges** → **payetonkawa**

Tu vois **deux pics** sur le graphique : un pour `produit.updated` et un pour `produit.stock_low`. L'alerte est bien envoyée quand le stock passe sous 10.

---

### Voir les logs du consumer en temps réel

```bash
docker compose logs consumer-commandes -f
```

Le `-f` signifie "follow" : les logs s'affichent en temps réel. Tu verras des lignes comme :

```
consumer-commandes-1  | INFO: Consumer démarré, en attente de messages...
consumer-commandes-1  | INFO: Client supprimé détecté: 1
consumer-commandes-1  | INFO: 1 commandes marquées comme client_supprime
```

Pour arrêter d'afficher les logs : `Ctrl + C`

---

### Lancer les tests unitaires

Les tests n'ont **pas besoin de RabbitMQ**. Ils utilisent SQLite en mémoire et les appels RabbitMQ échouent silencieusement (retournent `False` sans bloquer). C'est voulu.

```bash
# Tests api-clients
cd /home/david/dev/Mspr/payetonkawa/api-clients
source venv/bin/activate
pytest tests/ -v

# Tests api-produits
cd /home/david/dev/Mspr/payetonkawa/api-produits
source venv/bin/activate
pytest tests/ -v

# Tests api-commandes
cd /home/david/dev/Mspr/payetonkawa/api-commandes
source venv/bin/activate
pytest tests/ -v
```

---

## 6. Comprendre l'interface web localhost:15672

### Se connecter

Ouvre `http://localhost:15672` dans ton navigateur.

- Identifiant : `guest`
- Mot de passe : `guest`

En haut à droite, change le rafraîchissement sur **"Refresh every 5 seconds"** pour voir l'activité en temps réel.

---

### Onglet Overview — Vue d'ensemble

C'est la page d'accueil. Elle montre l'état global de RabbitMQ.

**Section "Queued messages" (graphique du haut) :**

Ce graphique montre le nombre de messages **en attente** dans les queues à chaque instant.

```
Queued messages
 │
 1│     ██
 │    ████
 0│────────────────────────────────→ temps
        ↑
   Un message est arrivé dans une queue
   mais a été traité quasi instantanément
```

- **Ready (jaune)** = messages en attente d'être lus par le consumer
- **Unacked (bleu)** = messages en cours de traitement par le consumer
- **Total (rouge)** = Ready + Unacked

Dans notre projet, ce graphique sera presque toujours à **0** car le consumer traite les messages instantanément. Un pic apparaît brièvement lors d'un événement, puis retombe à 0.

**Section "Message rates" (graphique du bas) :**

Ce graphique montre le **débit** de messages par seconde.

- **Publish (jaune)** = combien de messages sont envoyés par seconde
- **Deliver (vert)** = combien de messages sont livrés aux consumers par seconde

Ces deux courbes montent et descendent ensemble lors d'une action (création, suppression, etc.).

**Section "Global counts" :**

```
Connections: 1 | Channels: 1 | Exchanges: 8 | Queues: 2 | Consumers: 2
```

| Compteur | Ce que ça veut dire | Valeur normale |
|----------|---------------------|----------------|
| Connections | Nombre de services connectés à RabbitMQ | 1 (le consumer) |
| Exchanges | Nombre d'exchanges (bureau de tri) | 8 (7 internes + payetonkawa) |
| Queues | Nombre de files d'attente | 2 (nos 2 queues) |
| Consumers | Nombre de lecteurs actifs | 2 (1 par queue) |

**Section "Nodes" — Santé du serveur :**

```
Memory     : ████████████░░░░░░  159 MiB   → vert = OK
Disk space : ████████████░░░░░░  364 GiB   → vert = OK
Uptime     : 35m 44s                       → temps de fonctionnement
```

Si la barre Memory ou Disk space devient rouge : RabbitMQ manque de ressources.

---

### Onglet Exchanges — Le bureau de tri

Clique sur **"Exchanges"** dans le menu.

Tu vois 8 exchanges. Les 7 premiers commencent par `amq.` : ce sont des exchanges internes à RabbitMQ, **ignore-les**. Le seul qui nous concerne est **`payetonkawa`**.

```
| Name            | Type   | Features |
|-----------------|--------|----------|
| (AMQP default)  | direct | D        |  ← interne, ignorer
| amq.direct      | direct | D        |  ← interne, ignorer
| amq.fanout      | fanout | D        |  ← interne, ignorer
| amq.headers     | headers| D        |  ← interne, ignorer
| amq.match       | headers| D        |  ← interne, ignorer
| amq.rabbitmq... | topic  | D I      |  ← interne, ignorer
| amq.topic       | topic  | D        |  ← interne, ignorer
| payetonkawa     | topic  | D        |  ← LE NÔTRE
```

**Clique sur `payetonkawa` pour voir sa page de détail :**

```
Exchange: payetonkawa
├── Type : topic       → les messages sont triés par étiquette (routing key)
├── Features : durable → survit au redémarrage de RabbitMQ
│
├── Graphique "Message rates"
│     Publish (In)  = courbe jaune : messages reçus des APIs
│     Publish (Out) = courbe bleue : messages redistribués vers les queues
│
├── Bindings → les règles de routage
│     client.deleted   → commandes_client_events
│     produit.deleted  → commandes_produit_events
│
└── Publish message → pour envoyer un message manuellement (debug)
```

**Comment lire le graphique de l'exchange :**

```
Publish (In) jaune  ↑   Si tu supprimes un client :
                    │   → api-clients publie "client.deleted"
                ────┤   → courbe jaune monte
                    │
Publish (Out) bleu  │   → l'exchange redirige vers la queue
                ────┤   → courbe bleue monte aussi
                    │
Rien ne bouge       │   → aucune action CRUD récente = normal au repos
```

**La section Bindings — pourquoi certains messages ne sont pas stockés :**

Seuls `client.deleted` et `produit.deleted` ont une queue branchée.

Les autres messages (`client.created`, `produit.updated`, etc.) passent par l'exchange mais ne vont dans **aucune queue**. Ils traversent et disparaissent car aucun service n'a besoin de les consommer.

```
client.created   → exchange payetonkawa → pas de queue branchée → message perdu
                                                                   (voulu, personne n'en a besoin)

client.deleted   → exchange payetonkawa → commandes_client_events → consumer lit
                                                                   (utile ! consumer doit réagir)
```

---

### Onglet Queues and Streams — Les files d'attente

Clique sur **"Queues and Streams"** dans le menu.

Tu vois les 2 queues du projet :

```
| Name                      | State   | Ready | Unacked | Total |
|---------------------------|---------|-------|---------|-------|
| commandes_client_events   | running |  0    |    0    |   0   |
| commandes_produit_events  | running |  0    |    0    |   0   |
```

**Signification des colonnes :**

| Colonne | Signification |
|---------|---------------|
| `State: running` | La queue est active et écoute les messages |
| `State: idle` | La queue attend, rien à traiter en ce moment |
| `Ready = 0` | Aucun message en attente → normal, tout est traité |
| `Ready > 0` | Des messages attendent → peut indiquer que le consumer est arrêté |
| `Unacked` | Messages pris par le consumer mais pas encore confirmés traités |
| `Total` | Ready + Unacked |

**Clique sur `commandes_client_events`** pour voir sa page de détail :

```
Queue: commandes_client_events
│
├── Graphique "Queued messages"
│     Ready   (jaune) = messages en attente
│     Unacked (bleu)  = en cours de traitement
│     Total   (rouge) = les deux ensemble
│
├── Graphique "Message rates"
│     Publish = messages qui entrent dans la queue
│     Deliver = messages livrés au consumer
│
├── Details
│     State             : idle     → queue en attente, rien à traiter
│     Consumers         : 1        → notre consumer-commandes est connecté
│     Consumer capacity : 100%     → consumer disponible et prêt
│
├── Consumers (1)   → clique pour voir quel service écoute cette queue
├── Bindings  (2)   → clique pour voir depuis quel exchange arrivent les messages
├── Get messages    → lire un message manuellement (utile pour déboguer)
└── Purge           → vider tous les messages de la queue
```

---

### Comment lire un message manuellement dans une queue

Cette fonctionnalité est utile pour **déboguer** et voir exactement ce qu'un message contient.

**Pour voir un message figé dans la queue :**

**Etape 1 :** Arrête le consumer pour qu'il ne consomme pas les messages

```bash
docker compose stop consumer-commandes
```

**Etape 2 :** Supprime un client depuis le terminal

```bash
curl -X DELETE http://localhost:8000/customers/1 -H "X-API-Key: secret_key_123"
```

**Etape 3 :** Va sur la queue dans RabbitMQ

`Queues and Streams` → `commandes_client_events`

Tu vois maintenant **Ready = 1** (le message attend car le consumer est arrêté).

**Etape 4 :** Clique sur **"Get messages"** (en bas de la page)

1. Laisse tous les paramètres par défaut
2. Clique sur le bouton **"Get Message(s)"**
3. Le message apparaît avec son contenu complet :

```
Routing key  : client.deleted
Payload      :
{
  "event": "client_deleted",
  "client_id": 1,
  "timestamp": "2026-02-27T10:18:26Z"
}
```

**Etape 5 :** Redémarre le consumer pour traiter le message

```bash
docker compose start consumer-commandes
```

Le consumer lit le message, met à jour les commandes, et la queue repasse à **Ready = 0**.

---

### Onglet Connections — Les connexions actives

Clique sur **"Connections"** dans le menu.

Tu vois toutes les connexions TCP ouvertes vers RabbitMQ.

```
| Name          | State | From IP     | Description            |
|---------------|-------|-------------|------------------------|
| 172.20.0.x    | open  | (container) | consumer-commandes     |
```

Le `consumer-commandes` maintient une connexion **permanente** car il écoute en continu.

Les APIs (`api-clients`, `api-produits`, `api-commandes`) ouvrent et ferment une connexion à chaque message envoyé. Elles n'apparaissent donc dans cette liste que pendant la fraction de seconde où elles envoient un message.

---

### Tableau de bord — Que regarder selon la situation

| Je veux vérifier... | Où aller | Ce que je dois voir |
|---------------------|----------|---------------------|
| RabbitMQ fonctionne | Overview → Nodes | Barres Memory et Disk en vert |
| Un message a été envoyé | Exchanges → payetonkawa → graphique | Pic sur "Publish (In)" |
| Le consumer tourne | Queues → commandes_client_events → Details | `Consumers: 1` |
| Des messages sont bloqués | Queues → colonnes Ready/Total | `Ready > 0` qui ne diminue pas |
| Contenu d'un message | Queues → Get messages | JSON du message |
| Activité en temps réel | Overview → Message rates | Courbes qui bougent |
| Connexions actives | Connections | Liste des services connectés |

---

### Signaux d'alerte — Quand quelque chose ne va pas

| Ce que tu vois | Problème probable | Solution |
|----------------|-------------------|----------|
| `Consumers: 0` sur une queue | Le consumer est arrêté | `docker compose start consumer-commandes` |
| `Ready` augmente sans diminuer | Le consumer ne traite pas les messages | Vérifie les logs : `docker compose logs consumer-commandes` |
| Exchange `payetonkawa` absent | Les APIs n'ont jamais publié | Vérifie que `RABBITMQ_URL` est dans docker-compose |
| Aucune connexion dans l'onglet Connections | Rien n'est connecté à RabbitMQ | `docker compose up -d` pour redémarrer |
| Barres Memory/Disk rouges | RabbitMQ manque de ressources | Libère de la mémoire ou de l'espace disque |
