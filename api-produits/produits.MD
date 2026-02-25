# API PRODUITS - Guide complet

---

## RESUME RAPIDE

On va creer **9 fichiers** pour avoir une API Produits fonctionnelle dans Docker.
C'est la meme structure que l'API Clients, mais adaptee aux **produits (cafes)**.

```
api-produits/
├── app/
│   ├── __init__.py       ← Fichier vide (obligatoire pour Python)
│   ├── main.py           ← Le point d'entree : lance l'API
│   ├── database.py       ← La connexion a PostgreSQL
│   ├── models.py         ← La structure de la table "produits"
│   ├── schemas.py        ← Le format des donnees JSON
│   ├── crud.py           ← Les fonctions creer/lire/modifier/supprimer
│   └── routes.py         ← Les URLs de l'API (les endpoints)
├── requirements.txt      ← La liste des librairies Python
├── Dockerfile            ← La recette pour construire l'image Docker
├── docker-compose.yml    ← Lance l'API + sa base de donnees
└── produits.MD           ← Ce fichier (le guide)
```

---

## FICHIER PAR FICHIER

---

### 1. `requirements.txt`

**C'est quoi ?** La liste de courses des librairies Python dont on a besoin.

```txt
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
python-dotenv==1.0.0
pytest==7.4.4
pytest-cov==4.1.0
httpx==0.26.0
python-multipart==0.0.9
```

| Librairie | A quoi ca sert |
|-----------|---------------|
| `fastapi` | Le framework pour creer l'API (les routes, les URLs) |
| `uvicorn` | Le serveur web qui fait tourner FastAPI |
| `sqlalchemy` | Parler a la base de donnees sans ecrire de SQL |
| `psycopg2-binary` | Le "cable" entre Python et PostgreSQL |
| `pydantic` | Verifier que les donnees JSON sont au bon format |
| `python-dotenv` | Lire les variables d'environnement (DATABASE_URL, etc.) |
| `pytest` | Lancer les tests automatiques |
| `pytest-cov` | Mesurer combien de code est teste |
| `httpx` | Faire des requetes HTTP dans les tests |
| `python-multipart` | Permet la reception de fichiers (upload d'images) via les formulaires |

---

### 2. `app/__init__.py`

**C'est quoi ?** Un fichier **vide**. Il dit a Python "le dossier `app/` contient du code Python".

```python
# Fichier vide - necessaire pour que Python reconnaisse le dossier comme un package
```

Sans ce fichier, les `from app.xxx import yyy` ne marcheraient pas.

---

### 3. `app/database.py`

**C'est quoi ?** Le fichier qui connecte Python a PostgreSQL. C'est le "cable" entre ton code et ta base de donnees.

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

**Explication ligne par ligne :**

| Ligne | Ce que ca fait |
|-------|---------------|
| `load_dotenv()` | Charge le fichier `.env` (ou les variables Docker) |
| `DATABASE_URL = os.getenv(...)` | Recupere l'adresse de la base de donnees |
| `engine = create_engine(...)` | Cree le moteur de connexion a PostgreSQL |
| `SessionLocal = sessionmaker(...)` | Cree une "usine a sessions" (une session = une conversation avec la BDD) |
| `Base = declarative_base()` | Classe de base pour tous les modeles (tables) |
| `get_db()` | Ouvre une session, la donne au code, puis la ferme proprement |

---

### 4. `app/models.py`

**C'est quoi ?** La structure de la table "produits" dans PostgreSQL. Chaque ligne de code = une colonne dans la table.

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.sql import func
from .database import Base


class Produit(Base):
    __tablename__ = "produits"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    prix = Column(Float, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    origine = Column(String(100), nullable=True)
    poids_kg = Column(Float, default=1.0)
    image_url = Column(String(500), nullable=True)  # Ajout : chemin vers la photo du produit
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

**Chaque colonne expliquee :**

| Colonne | Type | Obligatoire ? | Exemple | Explication |
|---------|------|--------------|---------|-------------|
| `id` | Nombre | Auto | 1, 2, 3... | Numero unique, se remplit tout seul |
| `nom` | Texte (200 car.) | Oui | "Cafe Arabica Bresil" | Le nom du cafe |
| `description` | Texte long | Non | "Cafe doux avec notes de noisette..." | Description detaillee |
| `prix` | Decimal | Oui | 15.99 | Prix en euros |
| `stock` | Nombre | Oui (defaut 0) | 100 | Quantite en reserve |
| `origine` | Texte (100 car.) | Non | "Bresil" | Pays d'origine du cafe |
| `poids_kg` | Decimal | Non (defaut 1.0) | 0.25 | Poids du paquet en kg |
| `image_url` | Texte (500 car.) | Non | "/uploads/produit_1.jpg" | Chemin vers la photo du produit (ajout) |
| `actif` | Vrai/Faux | Non (defaut True) | true | Le produit est-il en vente ? |
| `date_creation` | Date | Auto | "2026-02-12 10:30:00" | Date d'ajout (automatique) |
| `date_modification` | Date | Auto | "2026-02-12 14:00:00" | Derniere modif (automatique) |

---

### 5. `app/schemas.py`

**C'est quoi ?** Le format des donnees JSON qu'on envoie et recoit. C'est comme un "formulaire" : on definit quels champs sont obligatoires et lesquels sont optionnels.

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Ce qu'on envoie pour CREER un produit (POST)
class ProduitCreate(BaseModel):
    nom: str
    description: Optional[str] = None
    prix: float
    stock: int = 0
    origine: Optional[str] = None
    poids_kg: float = 1.0


# Ce qu'on envoie pour MODIFIER un produit (PUT)
class ProduitUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    prix: Optional[float] = None
    stock: Optional[int] = None
    origine: Optional[str] = None
    poids_kg: Optional[float] = None
    actif: Optional[bool] = None


# Ce que l'API RENVOIE (la reponse)
class ProduitResponse(BaseModel):
    id: int
    nom: str
    description: Optional[str]
    prix: float
    stock: int
    origine: Optional[str]
    poids_kg: float
    image_url: Optional[str] = None  # Ajout : URL de la photo
    actif: bool
    date_creation: datetime
    date_modification: datetime

    class Config:
        from_attributes = True
```

**Les 3 schemas expliques :**

| Schema | Quand ? | Exemple |
|--------|---------|---------|
| `ProduitCreate` | Quand on **cree** un produit | `{"nom": "Arabica", "prix": 15.99, "stock": 100}` |
| `ProduitUpdate` | Quand on **modifie** un produit | `{"prix": 12.99}` (on peut ne changer qu'un seul champ) |
| `ProduitResponse` | Ce que l'API **renvoie** | Toutes les infos du produit, y compris l'id, les dates et l'image |

**Pourquoi `Optional` ?**
- Dans `ProduitCreate` : `description` est optionnel a la creation (on peut ajouter un cafe sans description)
- Dans `ProduitUpdate` : **tout** est optionnel, car on ne modifie peut-etre qu'un seul champ (ex: juste le prix)

---

### 6. `app/crud.py`

**C'est quoi ?** Les 4 fonctions de base pour manipuler la base de donnees. CRUD = Create, Read, Update, Delete.

```python
from sqlalchemy.orm import Session
from . import models, schemas


# CREATE - Ajouter un nouveau produit
def create_produit(db: Session, produit: schemas.ProduitCreate):
    db_produit = models.Produit(**produit.model_dump())
    db.add(db_produit)
    db.commit()
    db.refresh(db_produit)
    return db_produit


# READ - Recuperer un produit par son ID
def get_produit(db: Session, produit_id: int):
    return db.query(models.Produit).filter(models.Produit.id == produit_id).first()


# READ - Recuperer la liste de tous les produits
def get_produits(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Produit).offset(skip).limit(limit).all()


# UPDATE - Modifier un produit existant
def update_produit(db: Session, produit_id: int, produit: schemas.ProduitUpdate):
    db_produit = get_produit(db, produit_id)
    if not db_produit:
        return None
    update_data = produit.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_produit, key, value)
    db.commit()
    db.refresh(db_produit)
    return db_produit


# UPDATE IMAGE - Enregistrer l'URL de la photo d'un produit (ajout)
def update_produit_image(db: Session, produit_id: int, image_url: str):
    db_produit = get_produit(db, produit_id)
    if not db_produit:
        return None
    db_produit.image_url = image_url
    db.commit()
    db.refresh(db_produit)
    return db_produit


# DELETE - Supprimer un produit
def delete_produit(db: Session, produit_id: int):
    db_produit = get_produit(db, produit_id)
    if db_produit:
        db.delete(db_produit)
        db.commit()
        return True
    return False
```

**Chaque fonction expliquee :**

| Fonction | Ce qu'elle fait | Exemple d'utilisation |
|----------|----------------|----------------------|
| `create_produit` | Ajoute un produit dans la BDD | POST /products avec les infos du cafe |
| `get_produit` | Cherche UN produit par son ID | GET /products/1 → renvoie le cafe #1 |
| `get_produits` | Renvoie la LISTE des produits | GET /products → tous les cafes |
| `update_produit` | Modifie un produit existant | PUT /products/1 avec les nouvelles infos |
| `update_produit_image` | Enregistre l'URL de la photo | POST /products/1/image → sauvegarde le chemin de l'image |
| `delete_produit` | Supprime un produit | DELETE /products/1 |

**Detail de `update_produit` :**
- `exclude_unset=True` : ignore les champs qu'on n'a pas envoyes. Si on envoie juste `{"prix": 12.99}`, ca ne modifie QUE le prix, pas le reste.
- `setattr(db_produit, key, value)` : met a jour chaque champ un par un.

---

### 7. `app/routes.py`

**C'est quoi ?** Les URLs (endpoints) de l'API. Chaque route = une action possible.

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas
from .database import get_db

router = APIRouter(prefix="/products", tags=["Products"])


# POST /products : Creer un produit
@router.post("/", response_model=schemas.ProduitResponse, status_code=201)
def create_product(produit: schemas.ProduitCreate, db: Session = Depends(get_db)):
    return crud.create_produit(db=db, produit=produit)


# GET /products : Lister tous les produits
@router.get("/", response_model=List[schemas.ProduitResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_produits(db, skip=skip, limit=limit)


# GET /products/{id} : Recuperer un produit par son ID
@router.get("/{produit_id}", response_model=schemas.ProduitResponse)
def read_product(produit_id: int, db: Session = Depends(get_db)):
    db_produit = crud.get_produit(db, produit_id=produit_id)
    if db_produit is None:
        raise HTTPException(status_code=404, detail="Produit non trouve")
    return db_produit


# PUT /products/{id} : Modifier un produit
@router.put("/{produit_id}", response_model=schemas.ProduitResponse)
def update_product(produit_id: int, produit: schemas.ProduitUpdate, db: Session = Depends(get_db)):
    db_produit = crud.update_produit(db, produit_id=produit_id, produit=produit)
    if db_produit is None:
        raise HTTPException(status_code=404, detail="Produit non trouve")
    return db_produit


# DELETE /products/{id} : Supprimer un produit
@router.delete("/{produit_id}", status_code=204)
def delete_product(produit_id: int, db: Session = Depends(get_db)):
    success = crud.delete_produit(db, produit_id=produit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Produit non trouve")
```

**Les routes disponibles :**

| Methode | URL | Ce que ca fait | Exemple |
|---------|-----|---------------|---------|
| `POST` | `/products/` | Creer un produit | Envoyer `{"nom": "Arabica", "prix": 15.99}` |
| `GET` | `/products/` | Lister tous les produits | Reponse : liste de tous les cafes |
| `GET` | `/products/1` | Voir le produit #1 | Reponse : les details du cafe #1 |
| `PUT` | `/products/1` | Modifier le produit #1 | Envoyer `{"prix": 12.99}` pour changer le prix |
| `POST` | `/products/1/image` | Uploader une photo pour le produit #1 | Envoyer un fichier image (jpg, png, webp) en multipart/form-data |
| `DELETE` | `/products/1` | Supprimer le produit #1 | Le cafe est supprime de la BDD |

---

### 8. `app/main.py`

**C'est quoi ?** Le point d'entree de l'API. C'est le fichier qui lance tout.

```python
from fastapi import FastAPI
from .database import engine, Base
from .routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PayeTonKawa - API Produits",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Produits de PayeTonKawa"}
```

**Ligne par ligne :**

| Ligne | Ce que ca fait |
|-------|---------------|
| `Base.metadata.create_all(...)` | Cree la table "produits" dans PostgreSQL si elle n'existe pas |
| `app = FastAPI(...)` | Cree l'application API |
| `app.include_router(router)` | Branche toutes les routes (/products, etc.) |
| `@app.get("/")` | La page d'accueil : juste un message de bienvenue |

---

### 9. `Dockerfile`

**C'est quoi ?** La recette pour construire l'image Docker de l'API.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt email-validator
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Ligne par ligne :**

| Ligne | Ce que ca fait |
|-------|---------------|
| `FROM python:3.12-slim` | Part d'une image Python legere |
| `WORKDIR /app` | Se place dans le dossier /app du conteneur |
| `COPY requirements.txt .` | Copie la liste des librairies |
| `RUN pip install ...` | Installe toutes les librairies |
| `COPY app/ ./app/` | Copie tout le code de l'application |
| `CMD [...]` | Lance le serveur sur le port 8000 |

---

### 10. `docker-compose.yml`

**C'est quoi ?** Lance 2 conteneurs ensemble : la base de donnees + l'API.

```yaml
services:
  db-produits:
    image: postgres:15
    environment:
      POSTGRES_USER: faouz
      POSTGRES_PASSWORD: faouz2020
      POSTGRES_DB: produits_db
    ports:
      - "5437:5432"
    volumes:
      - db_produits_data:/var/lib/postgresql/data

  api-produits:
    build: .
    ports:
      - "8001:8000"
    environment:
      DATABASE_URL: postgresql://faouz:faouz2020@db-produits:5432/produits_db
    depends_on:
      - db-produits

volumes:
  db_produits_data:
```

**Les 2 services :**

| Service | C'est quoi | Port |
|---------|-----------|------|
| `db-produits` | La base de donnees PostgreSQL | 5437 (pour ne pas entrer en conflit avec le 5436 de l'API Clients) |
| `api-produits` | L'API Python/FastAPI | 8001 (pour ne pas entrer en conflit avec le 8000 de l'API Clients) |

**Points importants :**
- Le user est `faouz` avec le mot de passe `faouz2020` (comme pour l'API Clients)
- Le port est `5437` (pas 5436 qui est deja pris par api-clients)
- Le port de l'API est `8001` (pas 8000 qui est deja pris par api-clients)
- `depends_on` : l'API attend que PostgreSQL demarre avant de se lancer
- `db_produits_data` : volume persistant, les donnees ne sont pas perdues quand on arrete Docker

---

## COMMENT LANCER

```bash
cd /home/david/dev/Mspr/payetonkawa/api-produits

# Lancer tout


# Voir les logs
docker compose logs -f

# Arreter tout
docker compose down

# Reconstruire apres modification du code
docker compose up -d --build
```

## COMMENT TESTER

```bash
# Page d'accueil
curl http://localhost:8001/

# Documentation Swagger (ouvrir dans le navigateur)
# http://localhost:8001/docs

# Creer un produit
curl -X POST http://localhost:8001/products/ \
  -H "Content-Type: application/json" \
  -d '{"nom": "Cafe Arabica Bresil", "prix": 15.99, "stock": 100, "origine": "Bresil"}'

# Lister les produits
curl http://localhost:8001/products/

# Voir un produit
curl http://localhost:8001/products/1

# Modifier un produit (changer le prix)
curl -X PUT http://localhost:8001/products/1 \
  -H "Content-Type: application/json" \
  -d '{"prix": 12.99}'

# Supprimer un produit
curl -X DELETE http://localhost:8001/products/1
```

## ACCEDER A LA BASE DE DONNEES

```bash
docker exec -it api-produits-db-produits-1 psql -U faouz -d produits_db
```

Commandes SQL utiles une fois connecte :
```sql
\dt                    -- Voir les tables
SELECT * FROM produits; -- Voir tous les produits
\q                     -- Quitter
```
