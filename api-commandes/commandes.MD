# API COMMANDES - Guide complet

---

## RESUME RAPIDE

L'API Commandes est la plus complexe des 3 car :
- Elle a **2 tables** (commandes + lignes_commande) au lieu d'une seule
- Une commande contient **plusieurs lignes** (= les produits commandes)
- Elle fait reference aux **clients** (client_id) et aux **produits** (produit_id) des autres APIs

On va creer **9 fichiers** pour avoir une API fonctionnelle dans Docker.

```
api-commandes/
├── app/
│   ├── __init__.py       ← Fichier vide (obligatoire pour Python)
│   ├── main.py           ← Le point d'entree : lance l'API
│   ├── database.py       ← La connexion a PostgreSQL
│   ├── models.py         ← La structure des 2 tables (commandes + lignes)
│   ├── schemas.py        ← Le format des donnees JSON
│   ├── crud.py           ← Les fonctions creer/lire/modifier/supprimer
│   └── routes.py         ← Les URLs de l'API (les endpoints)
├── requirements.txt      ← La liste des librairies Python
├── Dockerfile            ← La recette pour construire l'image Docker
├── docker-compose.yml    ← Lance l'API + sa base de donnees
└── commandes.MD          ← Ce fichier (le guide)
```

---

## COMPRENDRE LA LOGIQUE

```
Commande #1 (Mohamed, total: 53.48€, statut: "en_attente")
│
├── Ligne 1 : 2x Cafe Arabica Bresil a 15.99€ = 31.98€
└── Ligne 2 : 1x Cafe Moka Ethiopie a 22.90€ = 22.90€
                                        TOTAL = 53.48€ ??? Non on calcule pas le total ici
```

- La **commande** = l'en-tete (qui a commande, quand, quel statut)
- Les **lignes** = le detail (quels produits, combien, a quel prix)
- `client_id` = juste le NUMERO du client (les infos sont dans l'API Clients)
- `produit_id` = juste le NUMERO du produit (les infos sont dans l'API Produits)

---

## FICHIER PAR FICHIER

---

### 1. `requirements.txt`

**C'est quoi ?** La liste de courses des librairies Python.

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
```

Meme liste que les autres APIs. Pas besoin de `pika` (RabbitMQ) pour le moment.

---

### 2. `app/__init__.py`

**C'est quoi ?** Un fichier **vide**. Obligatoire pour que Python reconnaisse le dossier.

```python
# Fichier vide
```

---

### 3. `app/database.py`

**C'est quoi ?** La connexion a PostgreSQL. Identique aux autres APIs.

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

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

Rien de nouveau ici, c'est le meme fichier que pour les 2 autres APIs.

---

### 4. `app/models.py`

**C'est quoi ?** La structure des **2 tables** dans PostgreSQL. C'est ici que ca differe des autres APIs.

```python
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Commande(Base):
    __tablename__ = "commandes"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=False, index=True)
    statut = Column(String(50), default="en_attente", nullable=False)
    total = Column(Float, default=0.0)
    date_commande = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    lignes = relationship("LigneCommande", back_populates="commande", cascade="all, delete-orphan")


class LigneCommande(Base):
    __tablename__ = "lignes_commande"

    id = Column(Integer, primary_key=True, index=True)
    commande_id = Column(Integer, ForeignKey("commandes.id", ondelete="CASCADE"), nullable=False)
    produit_id = Column(Integer, nullable=False)
    quantite = Column(Integer, nullable=False, default=1)
    prix_unitaire = Column(Float, nullable=False)

    commande = relationship("Commande", back_populates="lignes")
```

**Table `commandes` :**

| Colonne | Type | Obligatoire ? | Exemple | Explication |
|---------|------|--------------|---------|-------------|
| `id` | Nombre | Auto | 1, 2, 3... | Numero unique de la commande |
| `client_id` | Nombre | Oui | 1 | Le numero du client (de l'API Clients) |
| `statut` | Texte | Oui (defaut "en_attente") | "en_attente", "validee", "expediee", "livree", "annulee" | Ou en est la commande |
| `total` | Decimal | Non (defaut 0.0) | 53.48 | Le montant total en euros |
| `date_commande` | Date | Auto | "2026-02-12 10:30:00" | Quand la commande a ete passee |
| `date_modification` | Date | Auto | "2026-02-12 14:00:00" | Derniere modification |

**Table `lignes_commande` :**

| Colonne | Type | Obligatoire ? | Exemple | Explication |
|---------|------|--------------|---------|-------------|
| `id` | Nombre | Auto | 1, 2, 3... | Numero unique de la ligne |
| `commande_id` | Nombre | Oui | 1 | A quelle commande appartient cette ligne |
| `produit_id` | Nombre | Oui | 1 | Quel produit (de l'API Produits) |
| `quantite` | Nombre | Oui (defaut 1) | 3 | Combien de ce produit |
| `prix_unitaire` | Decimal | Oui | 15.99 | Le prix au moment de la commande |

**Nouveautes par rapport aux autres APIs :**

| Concept | Explication simple |
|---------|-------------------|
| `ForeignKey("commandes.id")` | Lien entre les 2 tables. Une ligne APPARTIENT a une commande |
| `ondelete="CASCADE"` | Si on supprime une commande, ses lignes sont supprimees aussi |
| `relationship(...)` | Permet d'acceder aux lignes depuis la commande (et inversement) |
| `back_populates` | Le lien marche dans les 2 sens : commande → lignes ET ligne → commande |
| `cascade="all, delete-orphan"` | Supprime les lignes orphelines (qui n'ont plus de commande) |

---

### 5. `app/schemas.py`

**C'est quoi ?** Le format JSON des donnees. Plus complexe ici car on a les commandes ET les lignes.

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# --- LIGNES DE COMMANDE ---

# Ce qu'on envoie pour creer une ligne (dans une commande)
class LigneCommandeCreate(BaseModel):
    produit_id: int
    quantite: int = 1
    prix_unitaire: float


# Ce que l'API renvoie pour une ligne
class LigneCommandeResponse(BaseModel):
    id: int
    commande_id: int
    produit_id: int
    quantite: int
    prix_unitaire: float

    class Config:
        from_attributes = True


# --- COMMANDES ---

# Ce qu'on envoie pour CREER une commande (POST)
class CommandeCreate(BaseModel):
    client_id: int
    lignes: List[LigneCommandeCreate]


# Ce qu'on envoie pour MODIFIER le statut (PUT)
class CommandeUpdate(BaseModel):
    statut: Optional[str] = None


# Ce que l'API RENVOIE (la reponse complete)
class CommandeResponse(BaseModel):
    id: int
    client_id: int
    statut: str
    total: float
    date_commande: datetime
    date_modification: datetime
    lignes: List[LigneCommandeResponse]

    class Config:
        from_attributes = True
```

**Les schemas expliques :**

| Schema | Quand ? | Exemple JSON |
|--------|---------|-------------|
| `LigneCommandeCreate` | Dans le body quand on cree une commande | `{"produit_id": 1, "quantite": 2, "prix_unitaire": 15.99}` |
| `LigneCommandeResponse` | Dans la reponse, pour chaque ligne | Toutes les infos de la ligne + son id |
| `CommandeCreate` | Quand on **cree** une commande | `{"client_id": 1, "lignes": [...]}` |
| `CommandeUpdate` | Quand on **modifie** le statut | `{"statut": "validee"}` |
| `CommandeResponse` | Ce que l'API **renvoie** | Toutes les infos + la liste des lignes |

**Point important :** Quand on cree une commande, on envoie le `client_id` + la liste des `lignes` d'un coup. Le total est calcule automatiquement.

---

### 6. `app/crud.py`

**C'est quoi ?** Les fonctions pour manipuler la base de donnees.

```python
from sqlalchemy.orm import Session
from . import models, schemas


# CREATE - Creer une commande avec ses lignes
def create_commande(db: Session, commande: schemas.CommandeCreate):
    # Calculer le total a partir des lignes
    total = sum(ligne.prix_unitaire * ligne.quantite for ligne in commande.lignes)

    # Creer la commande
    db_commande = models.Commande(
        client_id=commande.client_id,
        total=total
    )
    db.add(db_commande)
    db.flush()  # Pour obtenir l'ID de la commande avant de creer les lignes

    # Creer les lignes de commande
    for ligne in commande.lignes:
        db_ligne = models.LigneCommande(
            commande_id=db_commande.id,
            produit_id=ligne.produit_id,
            quantite=ligne.quantite,
            prix_unitaire=ligne.prix_unitaire
        )
        db.add(db_ligne)

    db.commit()
    db.refresh(db_commande)
    return db_commande


# READ - Recuperer une commande par son ID
def get_commande(db: Session, commande_id: int):
    return db.query(models.Commande).filter(models.Commande.id == commande_id).first()


# READ - Recuperer toutes les commandes
def get_commandes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Commande).offset(skip).limit(limit).all()


# READ - Recuperer les commandes d'un client specifique
def get_commandes_by_client(db: Session, client_id: int):
    return db.query(models.Commande).filter(models.Commande.client_id == client_id).all()


# UPDATE - Modifier le statut d'une commande
def update_commande(db: Session, commande_id: int, commande: schemas.CommandeUpdate):
    db_commande = get_commande(db, commande_id)
    if not db_commande:
        return None
    update_data = commande.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_commande, key, value)
    db.commit()
    db.refresh(db_commande)
    return db_commande


# DELETE - Supprimer une commande (et ses lignes grace au CASCADE)
def delete_commande(db: Session, commande_id: int):
    db_commande = get_commande(db, commande_id)
    if db_commande:
        db.delete(db_commande)
        db.commit()
        return True
    return False
```

**Chaque fonction expliquee :**

| Fonction | Ce qu'elle fait | Difference avec les autres APIs |
|----------|----------------|--------------------------------|
| `create_commande` | Cree la commande + toutes ses lignes d'un coup | Calcule le `total` automatiquement. Utilise `flush()` pour avoir l'ID avant de creer les lignes |
| `get_commande` | Cherche une commande par ID | Les lignes sont chargees automatiquement grace au `relationship` |
| `get_commandes` | Liste toutes les commandes | Pareil |
| `get_commandes_by_client` | Liste les commandes d'UN client | **Nouveau** : filtre par `client_id` |
| `update_commande` | Modifie le statut | On ne modifie que le statut, pas les lignes |
| `delete_commande` | Supprime la commande | Les lignes sont supprimees automatiquement (CASCADE) |

**Detail de `create_commande` :**
1. On calcule le total : `somme(prix × quantite)` pour chaque ligne
2. On cree la commande (sans les lignes)
3. `db.flush()` : envoie la commande a la BDD pour obtenir son `id` (sans valider)
4. On cree chaque ligne avec le `commande_id`
5. `db.commit()` : on valide tout d'un coup

---

### 7. `app/routes.py`

**C'est quoi ?** Les URLs (endpoints) de l'API.

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas
from .database import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])


# POST /orders : Creer une commande
@router.post("/", response_model=schemas.CommandeResponse, status_code=201)
def create_order(commande: schemas.CommandeCreate, db: Session = Depends(get_db)):
    return crud.create_commande(db=db, commande=commande)


# GET /orders : Lister toutes les commandes
@router.get("/", response_model=List[schemas.CommandeResponse])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_commandes(db, skip=skip, limit=limit)


# GET /orders/{id} : Recuperer une commande par son ID
@router.get("/{commande_id}", response_model=schemas.CommandeResponse)
def read_order(commande_id: int, db: Session = Depends(get_db)):
    db_commande = crud.get_commande(db, commande_id=commande_id)
    if db_commande is None:
        raise HTTPException(status_code=404, detail="Commande non trouvee")
    return db_commande


# GET /orders/client/{client_id} : Commandes d'un client
@router.get("/client/{client_id}", response_model=List[schemas.CommandeResponse])
def read_orders_by_client(client_id: int, db: Session = Depends(get_db)):
    return crud.get_commandes_by_client(db, client_id=client_id)


# PUT /orders/{id} : Modifier le statut d'une commande
@router.put("/{commande_id}", response_model=schemas.CommandeResponse)
def update_order(commande_id: int, commande: schemas.CommandeUpdate, db: Session = Depends(get_db)):
    db_commande = crud.update_commande(db, commande_id=commande_id, commande=commande)
    if db_commande is None:
        raise HTTPException(status_code=404, detail="Commande non trouvee")
    return db_commande


# DELETE /orders/{id} : Supprimer une commande
@router.delete("/{commande_id}", status_code=204)
def delete_order(commande_id: int, db: Session = Depends(get_db)):
    success = crud.delete_commande(db, commande_id=commande_id)
    if not success:
        raise HTTPException(status_code=404, detail="Commande non trouvee")
```

**Les routes disponibles :**

| Methode | URL | Ce que ca fait | Exemple |
|---------|-----|---------------|---------|
| `POST` | `/orders/` | Creer une commande avec ses lignes | Envoyer client_id + liste de produits |
| `GET` | `/orders/` | Lister toutes les commandes | Toutes les commandes avec leurs lignes |
| `GET` | `/orders/1` | Voir la commande #1 | Details + lignes de la commande |
| `GET` | `/orders/client/1` | Commandes du client #1 | Toutes les commandes de Mohamed |
| `PUT` | `/orders/1` | Modifier le statut | Passer de "en_attente" a "validee" |
| `DELETE` | `/orders/1` | Supprimer la commande #1 | Supprime aussi ses lignes |

**Route bonus** : `GET /orders/client/{client_id}` permet de voir toutes les commandes d'un client precis. Utile pour afficher l'historique de commandes.

---

### 8. `app/main.py`

**C'est quoi ?** Le point d'entree de l'API.

```python
from fastapi import FastAPI
from .database import engine, Base
from .routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PayeTonKawa - API Commandes",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Commandes de PayeTonKawa"}
```

`Base.metadata.create_all(...)` cree les **2 tables** (commandes + lignes_commande) au demarrage.

---

### 9. `Dockerfile`

**C'est quoi ?** La recette pour construire l'image Docker. Identique aux autres APIs.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt email-validator
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 10. `docker-compose.yml`

**C'est quoi ?** Lance 2 conteneurs : la base de donnees + l'API.

```yaml
services:
  db-commandes:
    image: postgres:15
    environment:
      POSTGRES_USER: faouz
      POSTGRES_PASSWORD: faouz2020
      POSTGRES_DB: commandes_db
    ports:
      - "5438:5432"
    volumes:
      - db_commandes_data:/var/lib/postgresql/data

  api-commandes:
    build: .
    ports:
      - "8002:8000"
    environment:
      DATABASE_URL: postgresql://faouz:faouz2020@db-commandes:5432/commandes_db
    depends_on:
      - db-commandes

volumes:
  db_commandes_data:
```

**Recap des ports pour les 3 APIs :**

| Service | Port BDD (host) | Port API (host) |
|---------|----------------|-----------------|
| api-clients | 5436 | 8000 |
| api-produits | 5437 | 8001 |
| api-commandes | **5438** | **8002** |

Chaque API a ses propres ports pour eviter les conflits.

---

## COMMENT LANCER

```bash
cd /home/david/dev/Mspr/payetonkawa/api-commandes

# Lancer tout
docker compose up -d

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
curl http://localhost:8002/

# Documentation Swagger (ouvrir dans le navigateur)
# http://localhost:8002/docs

# Creer une commande (client #1 commande 2 produits)
curl -X POST http://localhost:8002/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "lignes": [
      {"produit_id": 1, "quantite": 2, "prix_unitaire": 15.99},
      {"produit_id": 3, "quantite": 1, "prix_unitaire": 22.90}
    ]
  }'

# Lister toutes les commandes
curl http://localhost:8002/orders/

# Voir une commande
curl http://localhost:8002/orders/1

# Voir les commandes du client #1
curl http://localhost:8002/orders/client/1

# Changer le statut en "validee"
curl -X PUT http://localhost:8002/orders/1 \
  -H "Content-Type: application/json" \
  -d '{"statut": "validee"}'

# Supprimer une commande
curl -X DELETE http://localhost:8002/orders/1
```

## ACCEDER A LA BASE DE DONNEES

```bash
docker exec -it api-commandes-db-commandes-1 psql -U faouz -d commandes_db
```

Commandes SQL utiles une fois connecte :
```sql
\dt                            -- Voir les tables (commandes + lignes_commande)
SELECT * FROM commandes;       -- Voir toutes les commandes
SELECT * FROM lignes_commande; -- Voir toutes les lignes
\q                             -- Quitter
```

## STATUTS POSSIBLES POUR UNE COMMANDE

| Statut | Signification |
|--------|--------------|
| `en_attente` | La commande vient d'etre passee (defaut) |
| `validee` | La commande a ete confirmee |
| `en_preparation` | Le cafe est en cours de preparation |
| `expediee` | Le colis est parti |
| `livree` | Le client a recu sa commande |
| `annulee` | La commande a ete annulee |
