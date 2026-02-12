# 🗺️ PLAN DÉTAILLÉ DU PROJET PAYETONKAWA

---

## 📊 VUE D'ENSEMBLE

On va créer **3 applications** (APIs) qui gèrent :
1. **Les clients** (qui achète le café)
2. **Les produits** (les cafés vendus)
3. **Les commandes** (qui a commandé quoi)

Chaque application :
- A son propre code
- A sa propre base de données
- Peut parler aux autres via RabbitMQ (le facteur)

---

## 🗂️ STRUCTURE COMPLÈTE DU PROJET

```
payetonkawa/
│
├── docker-compose.yml          ← Lance tout (déjà fait ✅)
├── README.md                   ← Explication du projet
│
├── api-clients/                ← SERVICE 1 : CLIENTS
│   ├── app/
│   │   ├── __init__.py        ← Fichier vide (dit à Python "c'est un dossier de code")
│   │   ├── main.py            ← Point d'entrée de l'API
│   │   ├── config.py          ← Configuration (mots de passe, etc.)
│   │   ├── database.py        ← Connexion à PostgreSQL
│   │   ├── models.py          ← Structure de la table "clients"
│   │   ├── schemas.py         ← Format des données JSON
│   │   ├── crud.py            ← Fonctions : créer, lire, modifier, supprimer
│   │   └── rabbitmq.py        ← Envoi/réception de messages
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_main.py       ← Tests de l'API
│   │   └── conftest.py        ← Configuration des tests
│   ├── Dockerfile             ← Recette pour créer l'image Docker
│   └── requirements.txt       ← Liste des librairies Python nécessaires
│
├── api-produits/               ← SERVICE 2 : PRODUITS (même structure)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   └── rabbitmq.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_main.py
│   │   └── conftest.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── api-commandes/              ← SERVICE 3 : COMMANDES (même structure)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   └── rabbitmq.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_main.py
│   │   └── conftest.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── docs/                       ← DOCUMENTATION
│   ├── architecture.md        ← Schéma et explication technique
│   ├── securite.md            ← Comment l'API est sécurisée
│   ├── ci-cd.md               ← Explication du déploiement auto
│   └── conduite-changement.md ← Plan pour accompagner les équipes
│
├── postman/                    ← TESTS MANUELS
│   └── PayeTonKawa.postman_collection.json
│
└── .github/                    ← CI/CD (tests automatiques)
    └── workflows/
        └── ci.yml             ← Lance les tests à chaque push
```

---

## 📝 CE QUE CONTIENT CHAQUE FICHIER

### 🔹 Fichiers de configuration

| Fichier | Rôle | Contenu simplifié |
|---------|------|-------------------|
| `requirements.txt` | Liste des librairies | `fastapi`, `sqlalchemy`, `pytest`, etc. |
| `Dockerfile` | Recette Docker | "Prends Python, installe les librairies, lance l'app" |
| `config.py` | Réglages | Adresse de la BDD, mots de passe |
| `__init__.py` | Fichier vide | Dit à Python "ce dossier contient du code" |

### 🔹 Fichiers de l'application

| Fichier | Rôle | Contenu simplifié |
|---------|------|-------------------|
| `main.py` | Point d'entrée | Crée l'API, définit les routes (URLs) |
| `database.py` | Connexion BDD | Se connecte à PostgreSQL |
| `models.py` | Structure des tables | "Un client a un id, un nom, un email..." |
| `schemas.py` | Format JSON | "Quand on crée un client, il faut nom + email" |
| `crud.py` | Actions BDD | Fonctions : créer, lire, modifier, supprimer |
| `rabbitmq.py` | Messages | Envoyer "client créé" aux autres services |

### 🔹 Fichiers de tests

| Fichier | Rôle | Contenu simplifié |
|---------|------|-------------------|
| `conftest.py` | Préparation tests | Crée une fausse BDD pour tester |
| `test_main.py` | Tests | "Si je crée un client, ça marche ?" |

---

## 🚀 ORDRE DE RÉALISATION (étape par étape)

### **PHASE 1 : API CLIENTS (on fait 1 service complet d'abord)**

| Étape | Quoi | Temps |
|-------|------|-------|
| 1.1 | Créer `requirements.txt` | 5 min |
| 1.2 | Créer `config.py` | 5 min |
| 1.3 | Créer `database.py` | 10 min |
| 1.4 | Créer `models.py` (table Client) | 15 min |
| 1.5 | Créer `schemas.py` (format JSON) | 15 min |
| 1.6 | Créer `crud.py` (créer/lire/modifier/supprimer) | 20 min |
| 1.7 | Créer `main.py` (les routes de l'API) | 30 min |
| 1.8 | Tester avec Postman | 15 min |
| 1.9 | Créer les tests (`test_main.py`) | 30 min |
| 1.10 | Créer le `Dockerfile` | 10 min |

### **PHASE 2 : API PRODUITS**
→ Même chose que Phase 1, mais pour les produits

### **PHASE 3 : API COMMANDES**
→ Même chose, mais pour les commandes

### **PHASE 4 : RABBITMQ (communication entre services)**

| Étape | Quoi | Temps |
|-------|------|-------|
| 4.1 | Créer `rabbitmq.py` dans chaque service | 30 min |
| 4.2 | Quand un client est modifié → prévenir les commandes | 30 min |
| 4.3 | Quand un produit est modifié → prévenir les commandes | 30 min |

### **PHASE 5 : SÉCURITÉ**

| Étape | Quoi | Temps |
|-------|------|-------|
| 5.1 | Ajouter authentification par API Key | 1h |
| 5.2 | Protéger toutes les routes | 30 min |

### **PHASE 6 : CI/CD (tests automatiques)**

| Étape | Quoi | Temps |
|-------|------|-------|
| 6.1 | Créer le fichier GitHub Actions | 30 min |
| 6.2 | Tester que ça marche | 30 min |

### **PHASE 7 : MONITORING (surveillance)**

| Étape | Quoi | Temps |
|-------|------|-------|
| 7.1 | Ajouter des logs dans le code | 30 min |
| 7.2 | Compter les appels API | 30 min |

### **PHASE 8 : DOCUMENTATION**

| Étape | Quoi | Temps |
|-------|------|-------|
| 8.1 | Écrire `architecture.md` | 1h |
| 8.2 | Écrire `securite.md` | 30 min |
| 8.3 | Écrire `ci-cd.md` | 30 min |
| 8.4 | Écrire `conduite-changement.md` | 1h |
| 8.5 | Créer collection Postman | 30 min |

---

## 📅 PLANNING RÉSUMÉ

| Phase | Durée estimée |
|-------|---------------|
| Phase 1 : API Clients | 3h |
| Phase 2 : API Produits | 2h |
| Phase 3 : API Commandes | 2h |
| Phase 4 : RabbitMQ | 1h30 |
| Phase 5 : Sécurité | 1h30 |
| Phase 6 : CI/CD | 1h |
| Phase 7 : Monitoring | 1h |
| Phase 8 : Documentation | 3h |
| **TOTAL** | **~15h** |

