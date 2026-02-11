# Guide Complet - API Clients PayeTonKawa

## Table des matieres

1. [C'est quoi une API ?](#1-cest-quoi-une-api-)
2. [Les outils utilises dans ce projet](#2-les-outils-utilises-dans-ce-projet)
3. [L'architecture du projet (les fichiers)](#3-larchitecture-du-projet-les-fichiers)
4. [Explication de chaque fichier](#4-explication-de-chaque-fichier)
5. [Le parcours d'une requete (comment ca marche ensemble)](#5-le-parcours-dune-requete-comment-ca-marche-ensemble)
6. [Comment lancer le projet](#6-comment-lancer-le-projet)
7. [Comment tester avec Postman](#7-comment-tester-avec-postman)
8. [Comment voir la base de donnees](#8-comment-voir-la-base-de-donnees)
9. [Les codes HTTP a connaitre](#9-les-codes-http-a-connaitre)
10. [Glossaire (les mots compliques)](#10-glossaire-les-mots-compliques)

---

## 1. C'est quoi une API ?

### L'analogie du restaurant

Imagine un **restaurant** :

- **Toi** (le client) = l'application frontend ou Postman
- **Le serveur du restaurant** = l'API
- **La cuisine** = la base de donnees

Tu ne vas jamais directement en cuisine chercher ton plat. Tu passes par le **serveur** :

1. Tu demandes la carte (requete `GET`)
2. Tu commandes un plat (requete `POST`)
3. Le serveur va en cuisine (l'API interroge la base de donnees)
4. Il te ramene ton plat (la reponse en JSON)

### En termes techniques

Une **API** (Application Programming Interface) est un programme qui tourne sur un serveur et qui **ecoute des requetes HTTP** (comme quand tu tapes une URL dans ton navigateur) et **renvoie des donnees** (generalement au format JSON).

### C'est quoi une requete HTTP ?

C'est un message envoye a un serveur. Il y a 4 types principaux (les "methodes") :

| Methode  | Ce que ca fait           | Exemple concret                    |
|----------|--------------------------|------------------------------------|
| `GET`    | Lire / recuperer         | "Donne-moi la liste des clients"   |
| `POST`   | Creer quelque chose      | "Ajoute ce nouveau client"         |
| `PUT`    | Modifier quelque chose   | "Change l'email de ce client"      |
| `DELETE` | Supprimer quelque chose  | "Supprime ce client"               |

### C'est quoi le JSON ?

C'est le format dans lequel l'API envoie et recoit des donnees. Ca ressemble a ca :

```json
{
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean@example.com"
}
```

C'est comme un dictionnaire : des **cles** (`"nom"`) associees a des **valeurs** (`"Dupont"`).

---

## 2. Les outils utilises dans ce projet

### Python

Le langage de programmation utilise pour ecrire l'API.

### FastAPI

C'est un **framework** (une boite a outils) Python qui permet de creer des API facilement. C'est lui qui gere :
- L'ecoute des requetes (quand quelqu'un appelle `/customers/`)
- La validation des donnees (verifier que l'email est valide, etc.)
- La generation automatique de documentation (page `/docs`)

### SQLAlchemy

C'est un **ORM** (Object Relational Mapper). Au lieu d'ecrire du SQL brut comme :

```sql
INSERT INTO clients (nom, prenom) VALUES ('Dupont', 'Jean');
```

On ecrit du Python :

```python
client = Client(nom="Dupont", prenom="Jean")
db.add(client)
db.commit()
```

SQLAlchemy traduit automatiquement le Python en SQL. C'est plus simple et plus sur.

### PostgreSQL

C'est la **base de donnees**. C'est la ou les donnees des clients sont stockees de facon permanente (meme si tu eteins le serveur). Pense a un gros tableau Excel, mais beaucoup plus puissant.

### Uvicorn

C'est le **serveur web** qui fait tourner l'API. Il ecoute sur un port (8000) et transmet les requetes a FastAPI.

### Docker

C'est un outil qui permet de lancer des logiciels dans des "conteneurs" isoles. Ici, on l'utilise pour lancer PostgreSQL sans avoir a l'installer directement sur ton PC.

### Pydantic

C'est une librairie qui **valide les donnees**. Par exemple, si tu envoies un email mal forme (`"pasunmail"`), Pydantic le rejettera automatiquement avant meme que ca touche la base de donnees.

---

## 3. L'architecture du projet (les fichiers)

```
api-clients/
|
|-- .env                 # Les variables secretes (mot de passe BDD, etc.)
|-- requirements.txt     # La liste des librairies Python necessaires
|-- Dockerfile           # Instructions pour creer un conteneur Docker
|-- venv/                # L'environnement virtuel Python (les librairies installees)
|
|-- app/                 # LE COEUR DE L'API
|   |-- main.py          # Le point d'entree (la ou tout demarre)
|   |-- database.py      # La connexion a PostgreSQL
|   |-- models.py        # La structure de la table "clients"
|   |-- schemas.py       # La forme des donnees qu'on recoit/envoie
|   |-- routes.py        # Les URLs disponibles (les endpoints)
|   |-- crud.py          # Les operations sur la base de donnees
|
|-- tests/               # Les tests automatises
```

### Pourquoi autant de fichiers ?

C'est le principe de **separation des responsabilites** : chaque fichier a UN role precis. C'est comme dans une entreprise : le comptable ne fait pas le meme travail que le commercial. Ca rend le code plus clair et plus facile a modifier.

---

## 4. Explication de chaque fichier

### 4.1 `.env` - Les variables d'environnement

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/clients_db
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
API_KEY=secret_key_123
```

Ce fichier contient les informations **sensibles** (mots de passe, URLs de connexion). On les met dans un fichier separe pour ne pas les ecrire en dur dans le code.

Decomposition de `DATABASE_URL` :

```
postgresql://postgres:postgres@localhost:5433/clients_db
|            |        |        |         |    |
|            |        |        |         |    +-- nom de la base de donnees
|            |        |        |         +------- port
|            |        |        +----------------- adresse du serveur
|            |        +-------------------------- mot de passe
|            +----------------------------------- nom d'utilisateur
+------------------------------------------------ type de base de donnees
```

> **IMPORTANT** : Ce fichier ne doit JAMAIS etre pousse sur GitHub (il doit etre dans le `.gitignore`). Sinon tout le monde verra tes mots de passe !

---

### 4.2 `requirements.txt` - Les dependances

```
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
python-dotenv==1.0.0
pytest==7.4.4
pytest-cov==4.1.0
httpx==0.26.0
pika==1.3.2
```

C'est la **liste de courses** du projet. Chaque ligne = une librairie Python necessaire.

| Librairie        | Role                                         |
|------------------|----------------------------------------------|
| `fastapi`        | Le framework pour creer l'API                |
| `uvicorn`        | Le serveur web qui fait tourner l'API        |
| `sqlalchemy`     | L'ORM pour parler a la base de donnees       |
| `psycopg2-binary`| Le "traducteur" entre Python et PostgreSQL   |
| `pydantic`       | La validation des donnees                    |
| `python-dotenv`  | Lire le fichier `.env`                       |
| `pytest`         | Lancer les tests automatises                 |
| `pytest-cov`     | Mesurer la couverture des tests              |
| `httpx`          | Faire des requetes HTTP (pour les tests)     |
| `pika`           | Se connecter a RabbitMQ (messagerie)         |

Le `==` suivi d'un numero fixe la version exacte. Ca evite les surprises si une nouvelle version casse quelque chose.

---

### 4.3 `app/main.py` - Le point d'entree

```python
from fastapi import FastAPI
from .database import engine, Base
from .routes import router

# Cree les tables dans PostgreSQL au demarrage
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PayeTonKawa - API Clients",
    version="1.0.0"
)

# Branche les routes (les URLs) sur l'application
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Clients de PayeTonKawa"}
```

**Ligne par ligne :**

1. `from fastapi import FastAPI` : on importe FastAPI
2. `from .database import engine, Base` : on importe la connexion a la BDD (le `.` veut dire "dans le meme dossier")
3. `Base.metadata.create_all(bind=engine)` : ca cree automatiquement la table `clients` dans PostgreSQL si elle n'existe pas encore
4. `app = FastAPI(...)` : on cree l'application API
5. `app.include_router(router)` : on dit a l'app d'utiliser les routes definies dans `routes.py`
6. `@app.get("/")` : quand quelqu'un visite `http://localhost:8000/`, cette fonction est appelee. Le `@` s'appelle un **decorateur** : il "attache" l'URL a la fonction en dessous

---

### 4.4 `app/database.py` - La connexion a la base de donnees

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Explication simplifiee :**

- `load_dotenv()` : charge le fichier `.env` pour pouvoir lire les variables
- `os.getenv("DATABASE_URL")` : recupere l'URL de connexion depuis le `.env`
- `engine` : c'est le "moteur" qui sait comment parler a PostgreSQL
- `SessionLocal` : c'est une "usine" qui cree des sessions (une session = une conversation temporaire avec la BDD)
- `Base` : c'est la classe "parent" dont vont heriter tous nos modeles (tables)
- `get_db()` : cette fonction ouvre une connexion a la BDD, la donne a la route qui en a besoin, puis la ferme proprement. Le mot `yield` fait une pause : il donne la session, attend que la route ait fini, puis execute le `finally` pour fermer

---

### 4.5 `app/models.py` - La structure de la table

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

class Client(Base):
    __tablename__ = "clients"

    id         = Column(Integer, primary_key=True, index=True)
    nom        = Column(String(100), nullable=False)
    prenom     = Column(String(100), nullable=False)
    email      = Column(String(255), unique=True, nullable=False)
    telephone  = Column(String(20))
    adresse    = Column(String(500))
    actif      = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

C'est le **plan de la table** `clients` dans PostgreSQL. Imagine un tableau :

| id | nom    | prenom | email           | telephone  | adresse       | actif | created_at          |
|----|--------|--------|-----------------|------------|---------------|-------|---------------------|
| 1  | Dupont | Jean   | jean@example.com| 0612345678 | 12 rue Paris  | true  | 2025-02-11 12:00:00 |

**Les options des colonnes :**

| Option          | Signification                                              |
|-----------------|------------------------------------------------------------|
| `primary_key`   | Identifiant unique, genere automatiquement (1, 2, 3...)    |
| `nullable=False`| Obligatoire (ne peut pas etre vide)                        |
| `unique=True`   | Pas de doublons (deux clients ne peuvent pas avoir le meme email) |
| `default=True`  | Valeur par defaut si on ne la precise pas                  |
| `server_default=func.now()` | PostgreSQL met automatiquement la date actuelle  |
| `onupdate=func.now()`       | Se met a jour automatiquement quand on modifie   |

---

### 4.6 `app/schemas.py` - La forme des donnees

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ClientCreate(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    telephone: Optional[str] = None
    adresse: Optional[str] = None

class ClientResponse(BaseModel):
    id: int
    nom: str
    prenom: str
    email: str
    actif: bool
    created_at: datetime

    class Config:
        from_attributes = True
```

**Quelle difference avec `models.py` ?**

- `models.py` = la structure **dans la base de donnees** (les colonnes de la table)
- `schemas.py` = la structure **des donnees qu'on envoie/recoit** via l'API

**Pourquoi c'est different ?**

Quand tu **crees** un client (`ClientCreate`), tu n'envoies pas l'`id` (c'est la BDD qui le genere) ni `created_at` (c'est automatique). Mais quand l'API te **repond** (`ClientResponse`), elle te renvoie l'`id` et la date.

- `EmailStr` : verifie automatiquement que c'est un vrai format email
- `Optional[str] = None` : ce champ est **facultatif**, sa valeur par defaut est `None` (vide)
- `from_attributes = True` : permet a Pydantic de lire les objets SQLAlchemy directement

---

### 4.7 `app/routes.py` - Les URLs (endpoints)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas
from .database import get_db

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/", response_model=schemas.ClientResponse, status_code=201)
def create_customer(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    return crud.create_client(db=db, client=client)

@router.get("/", response_model=List[schemas.ClientResponse])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_clients(db, skip=skip, limit=limit)

@router.get("/{client_id}", response_model=schemas.ClientResponse)
def read_customer(client_id: int, db: Session = Depends(get_db)):
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client non trouve")
    return db_client

@router.delete("/{client_id}", status_code=204)
def delete_customer(client_id: int, db: Session = Depends(get_db)):
    success = crud.delete_client(db, client_id=client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client non trouve")
```

**C'est le fichier le plus important a comprendre.** C'est ici qu'on definit les URLs de l'API.

`prefix="/customers"` : toutes les routes commenceront par `/customers`

**Les 4 routes :**

| Decorateur + URL               | Ce que ca fait                    |
|--------------------------------|-----------------------------------|
| `@router.post("/")`           | `POST /customers/` = creer       |
| `@router.get("/")`            | `GET /customers/` = lister tout  |
| `@router.get("/{client_id}")` | `GET /customers/3` = voir le #3  |
| `@router.delete("/{client_id}")` | `DELETE /customers/3` = supprimer le #3 |

**Les parametres des fonctions :**

- `client: schemas.ClientCreate` : FastAPI lit automatiquement le JSON envoye et le transforme en objet `ClientCreate`. Si le JSON est mal forme, il renvoie une erreur 422
- `db: Session = Depends(get_db)` : FastAPI appelle `get_db()` automatiquement pour obtenir une connexion a la BDD. C'est le systeme d'**injection de dependances**
- `{client_id}` : c'est un **parametre dynamique** dans l'URL. Si tu appelles `/customers/5`, alors `client_id = 5`

**Les erreurs :**

- `HTTPException(status_code=404)` : si le client n'existe pas, on renvoie une erreur 404 (Not Found)

---

### 4.8 `app/crud.py` - Les operations en base de donnees

```python
from sqlalchemy.orm import Session
from . import models, schemas

def create_client(db: Session, client: schemas.ClientCreate):
    db_client = models.Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_client(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id).first()

def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Client).offset(skip).limit(limit).all()

def delete_client(db: Session, client_id: int):
    db_client = get_client(db, client_id)
    if db_client:
        db.delete(db_client)
        db.commit()
        return True
    return False
```

**CRUD** = **C**reate, **R**ead, **U**pdate, **D**elete. Ce sont les 4 operations de base sur une base de donnees.

**`create_client` etape par etape :**

1. `client.model_dump()` : transforme l'objet Pydantic en dictionnaire Python (`{"nom": "Dupont", "prenom": "Jean", ...}`)
2. `models.Client(**...)` : cree un objet Client SQLAlchemy avec ces valeurs (le `**` "deballe" le dictionnaire)
3. `db.add(db_client)` : dit a SQLAlchemy "prepare l'ajout de ce client"
4. `db.commit()` : envoie vraiment la commande a PostgreSQL (comme sauvegarder)
5. `db.refresh(db_client)` : relit le client depuis la BDD pour recuperer l'`id` et `created_at` generes automatiquement
6. `return db_client` : renvoie le client complet

**`get_clients` :**

- `db.query(models.Client)` = `SELECT * FROM clients`
- `.filter(models.Client.id == client_id)` = `WHERE id = 5`
- `.first()` = donne le premier resultat (ou `None` si rien)
- `.offset(skip).limit(limit)` = pagination (sauter les X premiers, limiter a Y resultats)
- `.all()` = donne tous les resultats sous forme de liste

---

## 5. Le parcours d'une requete (comment ca marche ensemble)

Quand tu fais `POST /customers/` avec Postman, voici ce qui se passe :

```
Postman                    uvicorn              FastAPI
  |                          |                    |
  |-- POST /customers/ ----->|                    |
  |   Body: {"nom":"Dupont"} |                    |
  |                          |------------------->|
  |                          |                    |
  |                    routes.py             schemas.py
  |                          |                    |
  |                          |  1. FastAPI recoit la requete
  |                          |  2. Il verifie le JSON avec ClientCreate (schemas.py)
  |                          |     -> email valide ? champs obligatoires presents ?
  |                          |  3. Il appelle get_db() pour ouvrir une session BDD
  |                          |  4. Il appelle create_customer() dans routes.py
  |                          |
  |                    crud.py              database.py
  |                          |                    |
  |                          |  5. crud.create_client() cree l'objet
  |                          |  6. db.add() + db.commit() envoie a PostgreSQL
  |                          |  7. PostgreSQL stocke le client et genere l'id
  |                          |
  |                    routes.py             schemas.py
  |                          |                    |
  |                          |  8. Le client est renvoye
  |                          |  9. FastAPI le transforme en JSON via ClientResponse
  |                          |
  |<---- 201 Created --------|
  |  {"id": 1, "nom": ...}  |
```

---

## 6. Comment lancer le projet

### Prerequis

- Python 3.12 installe
- Docker installe et lance

### Etape 1 : Lancer la base de donnees

Depuis le dossier `payetonkawa/` (le parent) :

```bash
docker compose up -d db-clients
```

Verifier qu'elle tourne :

```bash
docker ps
```

Tu dois voir `payetonkawa-db-clients-1` avec le statut `Up`.

### Etape 2 : Verifier le fichier `.env`

Le fichier `api-clients/.env` doit contenir :

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/clients_db
```

> **Attention** : `localhost:5433` c'est pour lancer l'API **en local** (sur ton PC).
> Si tu lances via Docker Compose, il faut remettre `db-clients:5432`.

### Etape 3 : Creer l'environnement virtuel (une seule fois)

```bash
cd api-clients
python3 -m venv venv
```

### Etape 4 : Installer les dependances

```bash
./venv/bin/pip install -r requirements.txt email-validator
```

### Etape 5 : Lancer l'API

```bash
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Decomposition de la commande :**

| Partie               | Signification                                      |
|----------------------|----------------------------------------------------|
| `./venv/bin/uvicorn` | Utilise uvicorn installe dans l'environnement virtuel |
| `app.main:app`       | Dans le dossier `app/`, fichier `main.py`, variable `app` |
| `--host 0.0.0.0`    | Ecoute sur toutes les interfaces reseau            |
| `--port 8000`        | Sur le port 8000                                   |
| `--reload`           | Redemarre automatiquement quand tu modifies le code |

Tu devrais voir :

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Etape 6 : Verifier que ca marche

Ouvre ton navigateur et va sur : `http://localhost:8000/`

Tu dois voir :

```json
{"message": "Bienvenue sur l'API Clients de PayeTonKawa"}
```

### Pour arreter

- L'API : appuie sur `Ctrl + C` dans le terminal
- La base de donnees : `docker compose down` (depuis le dossier `payetonkawa/`)

---

## 7. Comment tester avec Postman

### Installer Postman

Telecharge Postman sur https://www.postman.com/downloads/

### Test 1 : Verifier que l'API tourne

- Methode : **GET**
- URL : `http://localhost:8000/`
- Clique sur **Send**
- Reponse attendue : `{"message": "Bienvenue sur l'API Clients de PayeTonKawa"}`

### Test 2 : Creer un client

- Methode : **POST**
- URL : `http://localhost:8000/customers/`
- Onglet **Body** > selectionne **raw** > selectionne **JSON** dans le menu deroulant
- Colle ce JSON :

```json
{
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean.dupont@example.com",
  "telephone": "0612345678",
  "adresse": "12 rue de Paris, 75001"
}
```

- Clique sur **Send**
- Reponse attendue (status **201 Created**) :

```json
{
  "id": 1,
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean.dupont@example.com",
  "actif": true,
  "created_at": "2025-02-11T12:00:00+00:00"
}
```

### Test 3 : Lister tous les clients

- Methode : **GET**
- URL : `http://localhost:8000/customers/`
- Reponse : un tableau JSON avec tous les clients

### Test 4 : Voir un client precis

- Methode : **GET**
- URL : `http://localhost:8000/customers/1` (remplace 1 par l'id voulu)
- Reponse : les infos du client #1

### Test 5 : Supprimer un client

- Methode : **DELETE**
- URL : `http://localhost:8000/customers/1`
- Reponse : status **204 No Content** (pas de body, c'est normal)

### Cas d'erreur a tester

| Test                                    | Resultat attendu         |
|-----------------------------------------|--------------------------|
| `GET /customers/999` (id inexistant)    | 404 "Client non trouve"  |
| `POST` sans le champ `nom`             | 422 Erreur de validation |
| `POST` avec email invalide `"blabla"`  | 422 Erreur de validation |
| `POST` avec un email deja utilise      | 500 Erreur (doublon)     |

### Alternative : la doc Swagger

FastAPI genere automatiquement une page de test interactive :

`http://localhost:8000/docs`

Tu peux tester toutes les routes directement depuis ton navigateur, sans Postman !

---

## 8. Comment voir la base de donnees

### Via le terminal

```bash
# Voir toutes les tables
docker exec -i payetonkawa-db-clients-1 psql -U postgres -d clients_db -c "\dt"

# Voir la structure de la table clients
docker exec -i payetonkawa-db-clients-1 psql -U postgres -d clients_db -c "\d clients"

# Voir tous les clients
docker exec -i payetonkawa-db-clients-1 psql -U postgres -d clients_db -c "SELECT * FROM clients;"

# Compter les clients
docker exec -i payetonkawa-db-clients-1 psql -U postgres -d clients_db -c "SELECT COUNT(*) FROM clients;"

# Ouvrir un shell interactif (tu peux taper du SQL librement)
docker exec -it payetonkawa-db-clients-1 psql -U postgres -d clients_db
# Pour quitter le shell : taper \q
```

### Via une interface graphique (DBeaver, pgAdmin...)

Parametres de connexion :

| Parametre | Valeur       |
|-----------|-------------|
| Host      | `localhost`  |
| Port      | `5433`       |
| Database  | `clients_db` |
| User      | `postgres`   |
| Password  | `postgres`   |

---

## 9. Les codes HTTP a connaitre

| Code | Nom                  | Signification                               |
|------|----------------------|---------------------------------------------|
| 200  | OK                   | Tout s'est bien passe                       |
| 201  | Created              | La ressource a ete creee avec succes        |
| 204  | No Content           | Succes, mais rien a renvoyer (ex: delete)   |
| 400  | Bad Request          | La requete est mal formee                   |
| 404  | Not Found            | La ressource n'existe pas                   |
| 422  | Unprocessable Entity | Les donnees envoyees ne sont pas valides    |
| 500  | Internal Server Error| Bug cote serveur                            |

---

## 10. Glossaire (les mots compliques)

| Terme                | Definition simple                                                |
|----------------------|------------------------------------------------------------------|
| **API**              | Programme qui recoit des requetes et renvoie des donnees         |
| **Endpoint**         | Une URL precise de l'API (ex: `/customers/`)                     |
| **Route**            | Synonyme d'endpoint                                              |
| **Requete (Request)**| Le message envoye a l'API                                       |
| **Reponse (Response)**| Le message renvoye par l'API                                   |
| **JSON**             | Format de donnees en cle/valeur, lisible par les machines et les humains |
| **ORM**              | Outil qui traduit le Python en SQL automatiquement               |
| **Schema**           | La "forme" attendue des donnees (quels champs, quels types)      |
| **Model**            | La representation d'une table de la BDD en Python                |
| **CRUD**             | Create, Read, Update, Delete - les 4 operations de base          |
| **Middleware**       | Code qui s'execute entre la requete et la reponse                |
| **Migration**        | Modifier la structure de la BDD de facon controlee               |
| **Framework**        | Boite a outils qui fournit une structure pour ton code           |
| **Decorateur (@)**   | En Python, une annotation au-dessus d'une fonction qui lui ajoute un comportement |
| **Dependance**       | Librairie externe dont le projet a besoin pour fonctionner       |
| **Environnement virtuel (venv)** | Un dossier isole contenant les librairies Python du projet |
| **Port**             | Un numero qui identifie un service sur une machine (8000 pour l'API, 5433 pour la BDD) |
| **Session (BDD)**    | Une connexion temporaire a la base de donnees                    |
| **Commit**           | Valider/sauvegarder les changements dans la BDD                  |
