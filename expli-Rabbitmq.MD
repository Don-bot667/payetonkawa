# RabbitMQ — Guide complet PayeTonKawa

---

## Table des matières

1. [Pourquoi RabbitMQ ?](#1-pourquoi-rabbitmq)
2. [Comment ça fonctionne](#2-comment-ça-fonctionne)
3. [Ce qu'on a mis en place dans le projet](#3-ce-quon-a-mis-en-place-dans-le-projet)
4. [Lancer le projet et tester](#4-lancer-le-projet-et-tester)
5. [L'interface web — localhost:15672](#5-linterface-web--localhost15672)
6. [Référence rapide](#6-référence-rapide)

---

## 1. Pourquoi RabbitMQ ?

### Le problème

PayeTonKawa a **3 APIs séparées**, chacune avec **sa propre base de données** :

```
api-clients   →  clients_db    (port 5436 / 8000)
api-produits  →  produits_db   (port 5437 / 8001)
api-commandes →  commandes_db  (port 5438 / 8002)
```

Ces 3 bases **ne se voient pas**. Elles ne peuvent pas se lire entre elles directement.

**Scénario qui pose problème sans RabbitMQ :**

```
1. Jean crée un compte        → clients_db  : client n°3 = Jean
2. Jean passe une commande    → commandes_db : commande n°5, client_id = 3
3. Jean supprime son compte   → clients_db  : client n°3 supprimé
4. commandes_db ne sait rien de cette suppression
   → la commande n°5 pointe vers un client qui n'existe plus
   → donnée incohérente dans la base
```

### La solution

RabbitMQ est un **système de messagerie** placé entre les services. Il joue le rôle d'un **intermédiaire** : quand quelque chose d'important se passe dans un service, ce service dépose un message dans RabbitMQ. Les autres services qui sont concernés lisent ce message et réagissent.

```
AVEC RabbitMQ :

api-clients supprime le client 3
  → dépose dans RabbitMQ : "client.deleted, id=3"

consumer-commandes reçoit le message
  → va dans commandes_db
  → marque la commande n°5 comme "client_supprime"
  → données cohérentes
```

**Point important :** `api-clients` n'attend pas que `api-commandes` ait fini. Elle dépose le message et continue immédiatement. C'est la **communication asynchrone**.

---

## 2. Comment ça fonctionne

### Le trajet d'un message — avec l'exemple "suppression d'un client"

Voici exactement ce qui se passe quand on supprime le client n°1 :

```
ETAPE 1 — api-clients envoie le message
  api-clients publie :
    - contenu  : { "event": "client_deleted", "client_id": 1 }
    - étiquette: "client.deleted"    ← c'est la Routing Key
    - vers     : Exchange "payetonkawa"

ETAPE 2 — L'Exchange redirige le message
  Exchange "payetonkawa" reçoit le message
    → voit l'étiquette "client.deleted"
    → consulte ses règles (Bindings)
    → redirige vers la Queue "commandes_client_events"

ETAPE 3 — La Queue stocke le message
  Queue "commandes_client_events" :
    → garde le message jusqu'à ce qu'un consumer le lise
    → si personne ne lit, il reste là indéfiniment

ETAPE 4 — Le consumer traite le message
  consumer-commandes reçoit le message
    → lit le contenu : client_id = 1
    → ouvre commandes_db
    → trouve toutes les commandes du client 1
    → change leur statut en "client_supprime"
    → confirme à RabbitMQ : "message traité, tu peux le supprimer"
```

### Les 5 concepts clés expliqués dans ce contexte

| Terme | Ce que c'est | Dans notre projet |
|-------|-------------|-------------------|
| **Producer** | Celui qui envoie des messages | api-clients, api-produits, api-commandes |
| **Consumer** | Celui qui reçoit et traite les messages | consumer-commandes |
| **Exchange** | Le bureau de tri qui redirige les messages | Exchange nommé `payetonkawa` (type : topic) |
| **Routing Key** | L'étiquette collée sur le message | `client.deleted`, `produit.stock_low`, `commande.created`, … |
| **Queue** | La file d'attente où les messages attendent | `commandes_client_events`, `commandes_produit_events` |

### Pourquoi le type "topic" ?

Notre exchange est de type `topic`. Cela veut dire que les règles de routage utilisent des **étiquettes à points**, comme `client.deleted` ou `produit.stock_low`.

Avantage : on peut brancher une queue sur `client.*` pour écouter TOUS les événements d'un client (created, updated, deleted). Dans notre projet, on branche uniquement sur les événements qui nous intéressent.

```
Règles actuelles (Bindings) :

"client.deleted"  → queue commandes_client_events  → consumer réagit
"produit.deleted" → queue commandes_produit_events → consumer logue

Les autres messages (client.created, produit.updated, etc.)
passent par l'exchange mais disparaissent : aucune queue n'y est branchée.
C'est voulu. Personne n'en a besoin pour l'instant.
```

---

## 3. Ce qu'on a mis en place dans le projet

### Vue d'ensemble

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   api-clients   │    │  api-produits   │    │  api-commandes  │
│   (port 8000)   │    │   (port 8001)   │    │   (port 8002)   │
│                 │    │                 │    │                 │
│ → rabbitmq.py   │    │ → rabbitmq.py   │    │ → rabbitmq.py   │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                     │                       │
         └─────────────────────┼───────────────────────┘
                               │ publient ici
                               ▼
              ┌────────────────────────────────┐
              │   RabbitMQ  (port 5672)        │
              │   Exchange : "payetonkawa"     │
              │                                │
              │   client.deleted  → Queue A    │
              │   produit.deleted → Queue B    │
              └──────────────┬─────────────────┘
                             │
               ┌─────────────┴──────────────┐
               ▼                            ▼
  commandes_client_events     commandes_produit_events
               │                            │
               └─────────────┬──────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  consumer-commandes  │
                  │                      │
                  │ client.deleted    →  │
                  │  statut = "client_   │
                  │  supprime"           │
                  │                      │
                  │ produit.deleted   →  │
                  │  log uniquement      │
                  └──────────────────────┘
```

### Les fichiers créés ou modifiés

| Fichier | Type de modification | Rôle |
|---------|---------------------|------|
| `api-clients/app/rabbitmq.py` | Créé | Envoie les messages quand un client change |
| `api-produits/app/rabbitmq.py` | Créé | Envoie les messages quand un produit change |
| `api-commandes/app/rabbitmq.py` | Créé | Envoie les messages quand une commande change |
| `api-commandes/app/consumer.py` | Créé | Reçoit et traite les messages |
| `api-clients/app/routes.py` | Modifié | Appelle rabbitmq.py après chaque opération |
| `api-produits/app/routes.py` | Modifié | Appelle rabbitmq.py après chaque opération |
| `api-commandes/app/routes.py` | Modifié | Appelle rabbitmq.py après chaque opération |
| `api-commandes/app/crud.py` | Modifié | Ajout de `update_commande_statut()` |
| `api-clients/requirements.txt` | Déjà présent | `pika==1.3.2` |
| `api-produits/requirements.txt` | Modifié | Ajout de `pika==1.3.2` |
| `api-commandes/requirements.txt` | Modifié | Ajout de `pika==1.3.2` |
| `docker-compose.yml` | Modifié | Ajout du service `consumer-commandes` + variable `RABBITMQ_URL` |

---

### Le fichier rabbitmq.py (même structure dans les 3 APIs)

Ce fichier a deux fonctions principales :

**1 — Se connecter à RabbitMQ**

```python
def get_connection():
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        return pika.BlockingConnection(parameters)
    except Exception as e:
        logger.error(f"Erreur connexion RabbitMQ: {e}")
        return None
```

Si RabbitMQ est éteint, la fonction retourne `None` au lieu de faire crasher l'API. Les requêtes HTTP continuent de fonctionner normalement.

**2 — Envoyer un message**

```python
def publish_message(routing_key: str, message: dict):
    connection = get_connection()
    if not connection:
        return False  # RabbitMQ down → on abandonne sans crasher

    channel = connection.channel()
    channel.exchange_declare(exchange="payetonkawa", exchange_type="topic", durable=True)
    channel.basic_publish(
        exchange="payetonkawa",
        routing_key=routing_key,         # ex : "client.deleted"
        body=json.dumps(message),        # le contenu en JSON
        properties=pika.BasicProperties(delivery_mode=2)  # persistant = survit au redémarrage
    )
    connection.close()
```

**3 — Les fonctions spécifiques à chaque API**

`api-clients/app/rabbitmq.py` expose 3 fonctions :
```python
publish_client_created(client_id, client_data)   # routing key : "client.created"
publish_client_updated(client_id, client_data)   # routing key : "client.updated"
publish_client_deleted(client_id)                # routing key : "client.deleted"
```

`api-produits/app/rabbitmq.py` expose 4 fonctions :
```python
publish_produit_created(produit_id, produit_data)              # routing key : "produit.created"
publish_produit_updated(produit_id, produit_data)              # routing key : "produit.updated"
publish_produit_deleted(produit_id)                            # routing key : "produit.deleted"
publish_produit_stock_low(produit_id, produit_nom, stock)      # routing key : "produit.stock_low"
```

`api-commandes/app/rabbitmq.py` expose 3 fonctions :
```python
publish_commande_created(commande_id, commande_data)   # routing key : "commande.created"
publish_commande_updated(commande_id, statut)          # routing key : "commande.updated"
publish_commande_deleted(commande_id)                  # routing key : "commande.deleted"
```

---

### L'appel dans routes.py — règle : BDD d'abord, message ensuite

La règle est toujours la même dans les 3 APIs : on **sauvegarde en base en premier**, puis on **publie le message**. Si la base échoue, on ne publie rien.

**Exemple — Création d'un client :**

```python
@router.post("/customers/")
def create_customer(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    # 1. On sauvegarde en base PostgreSQL
    db_client = crud.create_client(db, client)

    # 2. La sauvegarde a réussi → on publie le message
    rabbitmq.publish_client_created(db_client.id, {
        "nom": db_client.nom,
        "email": db_client.email
    })

    # 3. On retourne le client créé
    return db_client
```

**Exemple — Suppression d'un client :**

```python
@router.delete("/customers/{client_id}", status_code=204)
def delete_customer(client_id: int, db: Session = Depends(get_db)):
    # 1. On supprime de la base
    success = crud.delete_client(db, client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client non trouvé")

    # 2. Suppression réussie → on prévient les autres services
    rabbitmq.publish_client_deleted(client_id)
    # consumer-commandes va recevoir ce message et mettre à jour les commandes
```

**Exemple spécial — Alerte stock bas dans api-produits :**

```python
@router.put("/products/{produit_id}")
def update_product(produit_id: int, produit: schemas.ProduitUpdate, db: Session = Depends(get_db)):
    db_produit = crud.update_produit(db, produit_id, produit)

    # Message standard : mise à jour du produit
    rabbitmq.publish_produit_updated(db_produit.id, {"stock": db_produit.stock})

    # Message supplémentaire si le stock est trop bas
    if db_produit.stock < 10:
        rabbitmq.publish_produit_stock_low(db_produit.id, db_produit.nom, db_produit.stock)

    return db_produit
```

---

### Le consumer (api-commandes/app/consumer.py)

C'est le seul fichier qui **reçoit** des messages. Il tourne en boucle infinie dans un conteneur Docker séparé.

**Fonctionnement général :**

```
Démarrage → connexion à RabbitMQ
          → déclare qu'il écoute 2 queues :
              commandes_client_events  (messages : client.deleted)
              commandes_produit_events (messages : produit.deleted)
          → boucle infinie d'attente...

Quand "client.deleted" arrive :
  → lit le client_id dans le message
  → récupère toutes les commandes de ce client dans commandes_db
  → change leur statut en "client_supprime"
  → envoie ACK à RabbitMQ (message traité, on peut le supprimer)

Quand "produit.deleted" arrive :
  → logue l'information
  → envoie ACK à RabbitMQ

En cas d'erreur :
  → envoie NACK à RabbitMQ (message non traité)
  → RabbitMQ remet le message en queue pour réessayer
```

**Le code du callback pour client.deleted :**

```python
def callback_client_deleted(ch, method, properties, body):
    data = json.loads(body)
    client_id = data.get("client_id")   # ex: 1

    db = SessionLocal()
    commandes = crud.get_commandes_by_client(db, client_id)
    # ex: commandes = [commande n°5, commande n°8]

    for commande in commandes:
        crud.update_commande_statut(db, commande.id, "client_supprime")
    # commande n°5 → statut = "client_supprime"
    # commande n°8 → statut = "client_supprime"

    db.close()
    ch.basic_ack(delivery_tag=method.delivery_tag)
    # Confirme à RabbitMQ : "message traité, tu peux le supprimer"
```

---

### Le service consumer dans docker-compose.yml

Le consumer est un **processus séparé** de l'API. Il utilise le même code qu'`api-commandes` mais lance `consumer.py` au lieu de FastAPI.

```yaml
consumer-commandes:
  build: ./api-commandes          # même image qu'api-commandes
  command: python -m app.consumer # mais lance consumer.py, pas l'API
  environment:
    DATABASE_URL: postgresql://faouz:faouz2020@db-commandes:5432/commandes_db
    RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  depends_on:
    - db-commandes
    - rabbitmq
  restart: unless-stopped         # redémarre automatiquement si crash
```

**Pourquoi un service séparé et pas intégré dans l'API ?**

```
Si le consumer était dans l'API FastAPI :
  → un message long à traiter bloquerait les requêtes HTTP
  → un crash du consumer tuerait aussi l'API

Avec un service séparé :
  → l'API répond aux requêtes HTTP sans être bloquée
  → le consumer traite les messages en parallèle
  → si le consumer crash, l'API continue de fonctionner
  → restart: unless-stopped redémarre le consumer automatiquement
```

---

## 4. Lancer le projet et tester

### Démarrer tout le projet

```bash
# Depuis le dossier payetonkawa/
docker compose up -d
```

Cela démarre 8 services :
- `db-clients`, `db-produits`, `db-commandes` — les 3 bases PostgreSQL
- `api-clients`, `api-produits`, `api-commandes` — les 3 APIs FastAPI
- `rabbitmq` — le message broker
- `consumer-commandes` — le processus qui écoute les messages

**Vérifier que tout est démarré :**

```bash
docker compose ps
```

Tous les services doivent afficher `running`.

**Note — Reconstruire les images après modification du code Python :**

Docker ne détecte pas automatiquement les changements de code. Il faut reconstruire les images :

```bash
docker compose build api-clients api-produits api-commandes
docker compose up -d api-clients api-produits api-commandes consumer-commandes
```

---

### Test 1 — Un message est bien envoyé quand on crée un client

**Crée un client :**

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

**Vérifie dans RabbitMQ :** va sur `http://localhost:15672` → **Exchanges** → **payetonkawa**

Tu vois un pic sur le graphique **"Publish (In)"** : le message `client.created` a bien été envoyé.

---

### Test 2 — La suppression d'un client met à jour ses commandes automatiquement

Ce test montre le scénario complet : créer un client, lui créer une commande, le supprimer, et voir que sa commande change de statut automatiquement.

**Etape 1 — Crée un client**

```bash
curl -X POST http://localhost:8000/customers/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: secret_key_123" \
  -d '{"nom": "Martin", "prenom": "Sophie", "email": "sophie@test.com", "telephone": "0698765432"}'
```

Note l'`id` retourné (ex: `1`).

**Etape 2 — Crée une commande pour ce client**

```bash
curl -X POST http://localhost:8002/orders/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: secret_key_123" \
  -d '{
    "client_id": 1,
    "lignes": [{"produit_id": 1, "quantite": 2, "prix_unitaire": 9.99}]
  }'
```

Note l'`id` de la commande (ex: `5`). Le statut est `"en_attente"`.

**Etape 3 — Vérifie le statut de la commande**

```bash
curl http://localhost:8002/orders/5 -H "X-API-Key: secret_key_123"
```

Résultat : `"statut": "en_attente"` — normal, le client existe encore.

**Etape 4 — Supprime le client**

```bash
curl -X DELETE http://localhost:8000/customers/1 -H "X-API-Key: secret_key_123"
```

Réponse : code `204` (suppression réussie).

**Etape 5 — Revérifie la commande**

```bash
curl http://localhost:8002/orders/5 -H "X-API-Key: secret_key_123"
```

Résultat attendu :
```json
{
  "id": 5,
  "client_id": 1,
  "statut": "client_supprime",
  "total": 19.98
}
```

La commande est passée de `"en_attente"` à `"client_supprime"` **automatiquement**, sans aucune action manuelle. C'est RabbitMQ + le consumer qui ont fait le travail.

---

### Test 3 — L'alerte stock bas fonctionne

**Met le stock d'un produit sous 10 :**

```bash
curl -X PUT http://localhost:8001/products/1 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: secret_key_123" \
  -d '{"stock": 5}'
```

**Vérifie dans RabbitMQ :** Exchanges → payetonkawa → graphique

Tu vois **deux pics** : un pour `produit.updated` et un pour `produit.stock_low`. Deux messages ont été envoyés par la même action.

---

### Voir les logs du consumer en temps réel

```bash
docker compose logs consumer-commandes -f
```

Le `-f` affiche les logs en direct. Tu verras :

```
consumer-commandes-1  | INFO: Consumer démarré, en attente de messages...
consumer-commandes-1  | INFO: Client supprimé détecté: 1
consumer-commandes-1  | INFO: 1 commandes marquées comme client_supprime
```

Pour arrêter l'affichage : `Ctrl + C`

---

## 5. L'interface web — localhost:15672

### Se connecter

Ouvre `http://localhost:15672` dans le navigateur.

- Identifiant : `guest`
- Mot de passe : `guest`

Change le rafraîchissement en haut à droite sur **"Refresh every 5 seconds"** pour voir l'activité en direct.

---

### Onglet Overview

Page d'accueil. Elle montre l'état global de RabbitMQ.

**"Queued messages" (graphique du haut) :**

Nombre de messages en attente dans toutes les queues.

```
Ready   (jaune)  = messages qui attendent d'être lus
Unacked (bleu)   = messages en cours de traitement par le consumer
Total   (rouge)  = Ready + Unacked
```

Dans notre projet, ce graphique est presque toujours à **0** car le consumer traite les messages immédiatement. Un bref pic apparaît lors d'une action, puis retombe à 0.

**"Message rates" (graphique du bas) :**

Débit de messages par seconde.

```
Publish (jaune) = messages envoyés par les APIs
Deliver (vert)  = messages livrés au consumer
```

Ces deux courbes bougent ensemble lors d'une action CRUD.

**"Global counts" :**

```
Connections: 1  Channels: 1  Exchanges: 8  Queues: 2  Consumers: 2
```

| Compteur | Valeur normale | Si différent |
|----------|----------------|--------------|
| Connections | 1 (le consumer) | 0 = consumer arrêté |
| Queues | 2 | 0 = les APIs n'ont jamais publié |
| Consumers | 2 (1 par queue) | 0 = consumer arrêté |

**"Nodes" — santé du serveur :**

```
Memory     : ████████░░░  159 MiB    → vert = OK
Disk space : ████████░░░  364 GiB    → vert = OK
```

Si une barre devient rouge : RabbitMQ manque de ressources.

---

### Onglet Exchanges

Liste tous les exchanges. **Ignore les 7 exchanges `amq.*`** — ce sont des exchanges internes à RabbitMQ. Le seul qui nous concerne est **`payetonkawa`**.

**Clique sur `payetonkawa` :**

```
Exchange: payetonkawa
Type     : topic    → routage par étiquettes à points (client.deleted, etc.)
Durable  : oui      → survit au redémarrage de RabbitMQ

Graphique :
  Publish (In)  = messages reçus depuis les APIs
  Publish (Out) = messages redistribués vers les queues

Bindings (règles de routage) :
  "client.deleted"   → commandes_client_events
  "produit.deleted"  → commandes_produit_events
```

**Pourquoi certains messages ne sont pas dans les bindings ?**

Les messages `client.created`, `produit.updated`, etc. passent par l'exchange mais ne vont dans aucune queue. Ils disparaissent car aucun service n'a besoin de les consommer actuellement.

```
client.created  → exchange payetonkawa → pas de queue → message perdu (voulu)
client.deleted  → exchange payetonkawa → commandes_client_events → consumer réagit
```

---

### Onglet Queues and Streams

Liste toutes les queues.

```
| Name                      | State   | Ready | Unacked | Total |
|---------------------------|---------|-------|---------|-------|
| commandes_client_events   | running |  0    |    0    |   0   |
| commandes_produit_events  | running |  0    |    0    |   0   |
```

| Colonne | Ce que ça veut dire |
|---------|---------------------|
| `State: running` | Queue active, écoute les messages |
| `State: idle` | Queue en pause, rien à traiter |
| `Ready = 0` | Aucun message en attente — normal |
| `Ready > 0` qui ne diminue pas | Consumer arrêté ou bloqué |
| `Unacked > 0` | Message en cours de traitement |

**Clique sur `commandes_client_events` pour voir le détail :**

```
Consumers : 1       → notre consumer-commandes est connecté
State     : idle    → en attente, rien à traiter en ce moment
```

---

### Comment lire un message manuellement (pour déboguer)

Utile pour voir **exactement** ce que contient un message.

**Etape 1 — Arrête le consumer** pour qu'il ne consomme pas les messages immédiatement

```bash
docker compose stop consumer-commandes
```

**Etape 2 — Supprime un client** pour générer un message

```bash
curl -X DELETE http://localhost:8000/customers/1 -H "X-API-Key: secret_key_123"
```

**Etape 3 — Va dans l'interface**

`Queues and Streams` → `commandes_client_events`

Tu vois **Ready = 1** (le message attend car le consumer est arrêté).

**Etape 4 — Clique sur "Get messages"** (en bas de la page de la queue)

1. Laisse les paramètres par défaut
2. Clique sur **"Get Message(s)"**
3. Le message apparaît :

```
Routing key : client.deleted
Payload     :
{
  "event"     : "client_deleted",
  "client_id" : 1,
  "timestamp" : "2026-02-27T10:18:26Z"
}
```

**Etape 5 — Redémarre le consumer** pour traiter le message

```bash
docker compose start consumer-commandes
```

Le consumer lit le message, met à jour les commandes, la queue repasse à **Ready = 0**.

---

### Signaux d'alerte — que faire si quelque chose ne va pas

| Ce que tu vois dans l'interface | Problème probable | Solution |
|---------------------------------|-------------------|----------|
| `Consumers: 0` sur une queue | Consumer arrêté | `docker compose start consumer-commandes` |
| `Ready` augmente sans diminuer | Consumer bloqué ou crashé | `docker compose logs consumer-commandes` |
| Exchange `payetonkawa` absent | APIs jamais lancées ou `RABBITMQ_URL` manquant | Vérifier docker-compose.yml + rebuild |
| Aucune connexion dans "Connections" | Rien n'est connecté | `docker compose up -d` |
| Memory ou Disk rouge dans "Nodes" | RabbitMQ manque de ressources | Libérer de la mémoire / de l'espace disque |

---

## 6. Référence rapide

### Tous les messages envoyés dans le projet

| Routing Key | Qui l'envoie | Déclencheur | Qui l'écoute |
|-------------|--------------|-------------|--------------|
| `client.created` | api-clients | POST /customers/ | *(personne)* |
| `client.updated` | api-clients | PUT /customers/{id} | *(personne)* |
| `client.deleted` | api-clients | DELETE /customers/{id} | consumer-commandes |
| `produit.created` | api-produits | POST /products/ | *(personne)* |
| `produit.updated` | api-produits | PUT /products/{id} | *(personne)* |
| `produit.deleted` | api-produits | DELETE /products/{id} | consumer-commandes (log) |
| `produit.stock_low` | api-produits | PUT si stock < 10 | *(personne)* |
| `commande.created` | api-commandes | POST /orders/ | *(personne)* |
| `commande.updated` | api-commandes | PUT /orders/{id} | *(personne)* |
| `commande.deleted` | api-commandes | DELETE /orders/{id} | *(personne)* |

---

### Commandes utiles

```bash
# Démarrer tout le projet
docker compose up -d

# Voir l'état de tous les services
docker compose ps

# Logs du consumer en direct
docker compose logs consumer-commandes -f

# Rebuild après modification du code Python
docker compose build api-clients api-produits api-commandes
docker compose up -d api-clients api-produits api-commandes consumer-commandes

# Arrêter sans supprimer les données
docker compose down

# Reset complet (supprime toutes les données)
docker compose down -v
```

---

### Points essentiels à retenir

1. **Les APIs ne se parlent pas directement.** `api-clients` ne sait pas qu'`api-commandes` existe. Elle publie un message et oublie.

2. **Si RabbitMQ est éteint, les APIs continuent de fonctionner.** Elles perdent juste l'envoi des messages — pas de crash.

3. **Toujours sauvegarder en base AVANT de publier le message.** Si la base échoue, on ne publie rien.

4. **Le consumer est séparé de l'API** pour ne pas bloquer les requêtes HTTP. Un crash du consumer n'affecte pas l'API.

5. **`durable=True` et `delivery_mode=2`** = les messages survivent à un redémarrage de RabbitMQ.

6. **ACK / NACK** : le consumer confirme à RabbitMQ que le message est traité (ACK) ou qu'il faut le remettre en queue (NACK en cas d'erreur).
