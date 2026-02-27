🎫 TICKETS PAYETONKAWA
Dernière mise à jour : 2026-02-23
Total : 25 tickets | Estimation totale : ~12-15h

📋 SOMMAIRE
PHASE 1 - CORRECTIONS BACKEND
PHASE 2 - RABBITMQ
PHASE 3 - TESTS
PHASE 4 - SÉCURITÉ
PHASE 5 - CI/CD
PHASE 6 - MONITORING
PHASE 7 - DOCUMENTATION
PHASE 8 - POSTMAN
PHASE 1 - CORRECTIONS BACKEND
🎫 TICKET #001 — Ajouter endpoint PUT /customers/{id}
Priorité : 🔴 Haute
Estimation : 20 min
Assigné à : Backend

Description
L'API clients ne possède pas d'endpoint pour modifier un client existant. Tous les autres services (produits, commandes) ont cette fonctionnalité.

Fichiers à modifier
api-clients/app/schemas.py    → Ajouter ClientUpdate
api-clients/app/crud.py       → Ajouter update_client()
api-clients/app/routes.py     → Ajouter PUT /customers/{id}
Critères d'acceptation
Schéma ClientUpdate créé avec champs optionnels (nom, email, adresse, telephone)
Fonction update_client(db, client_id, client) dans crud.py
Route PUT /customers/{client_id} retourne 200 + client modifié
Retourne 404 si client inexistant
Validation email unique (si modifié)
Code attendu
schemas.py :

class ClientUpdate(BaseModel):
    nom: Optional[str] = None
    email: Optional[EmailStr] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
crud.py :

def update_client(db: Session, client_id: int, client: schemas.ClientUpdate):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        return None
    update_data = client.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_client, key, value)
    db.commit()
    db.refresh(db_client)
    return db_client
routes.py :

@router.put("/{client_id}", response_model=schemas.ClientResponse)
def update_customer(client_id: int, client: schemas.ClientUpdate, db: Session = Depends(get_db)):
    db_client = crud.update_client(db, client_id=client_id, client=client)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return db_client


🎫 TICKET #002 — Ajouter init.py manquant dans api-clients/app
Priorité : 🟡 Moyenne
Estimation : 2 min

Description
Le dossier api-clients/app/ n'a pas de fichier __init__.py contrairement aux autres APIs. Peut causer des problèmes d'import.

Fichiers à créer
api-clients/app/__init__.py   → Fichier vide
Critères d'acceptation
Fichier __init__.py créé (peut être vide)
🎫 TICKET #003 — Harmoniser les config.py entre APIs
Priorité : 🟢 Basse
Estimation : 15 min

Description
Créer un fichier config.py dans chaque API pour centraliser la configuration (DATABASE_URL, etc.) de manière cohérente.

Fichiers à créer/modifier
api-clients/app/config.py
api-produits/app/config.py
api-commandes/app/config.py
Code attendu
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://faouz:faouz2020@localhost:5432/clients_db")
    rabbitmq_url: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    api_key: str = os.getenv("API_KEY", "dev-key-change-in-prod")
    
    class Config:
        env_file = ".env"

settings = Settings()
Critères d'acceptation
Chaque API a son config.py
Variables d'environnement utilisées
DATABASE_URL, RABBITMQ_URL, API_KEY configurables

PHASE 2 - RABBITMQ
🎫 TICKET #004 — Créer module RabbitMQ pour api-clients
Priorité : 🔴 Haute
Estimation : 45 min

Description
Implémenter la connexion RabbitMQ et la publication de messages quand un client est créé, modifié ou supprimé.

Fichiers à créer
api-clients/app/rabbitmq.py
Dépendances
pika (déjà dans requirements.txt)
Code attendu
import pika
import json
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def get_connection():
    """Établit une connexion à RabbitMQ"""
    parameters = pika.URLParameters(RABBITMQ_URL)
    return pika.BlockingConnection(parameters)

def publish_message(exchange: str, routing_key: str, message: dict):
    """Publie un message sur RabbitMQ"""
    try:
        connection = get_connection()
        channel = connection.channel()
        
        # Déclare l'exchange (type: topic pour flexibilité)
        channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)
        
        # Publie le message
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Message persistant
                content_type='application/json'
            )
        )
        connection.close()
        return True
    except Exception as e:
        print(f"Erreur RabbitMQ: {e}")
        return False

# Fonctions spécifiques
def publish_client_created(client_id: int, client_data: dict):
    publish_message("payetonkawa", "client.created", {
        "event": "client_created",
        "client_id": client_id,
        "data": client_data
    })

def publish_client_updated(client_id: int, client_data: dict):
    publish_message("payetonkawa", "client.updated", {
        "event": "client_updated",
        "client_id": client_id,
        "data": client_data
    })

def publish_client_deleted(client_id: int):
    publish_message("payetonkawa", "client.deleted", {
        "event": "client_deleted",
        "client_id": client_id
    })
Critères d'acceptation
Connexion à RabbitMQ fonctionnelle
Exchange "payetonkawa" créé (type: topic)
Messages publiés sur : client.created, client.updated, client.deleted
Gestion des erreurs (ne bloque pas l'API si RabbitMQ down)
🎫 TICKET #005 — Intégrer RabbitMQ dans les routes api-clients
Priorité : 🔴 Haute
Estimation : 20 min
Dépend de : #004

Description
Appeler les fonctions de publication RabbitMQ après chaque opération CRUD.

Fichiers à modifier
api-clients/app/routes.py
Modifications attendues
from . import rabbitmq

@router.post("/", response_model=schemas.ClientResponse, status_code=201)
def create_customer(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    db_client = crud.create_client(db=db, client=client)
    # Publier sur RabbitMQ
    rabbitmq.publish_client_created(db_client.id, {
        "nom": db_client.nom,
        "email": db_client.email
    })
    return db_client

@router.put("/{client_id}", response_model=schemas.ClientResponse)
def update_customer(client_id: int, client: schemas.ClientUpdate, db: Session = Depends(get_db)):
    db_client = crud.update_client(db, client_id=client_id, client=client)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    # Publier sur RabbitMQ
    rabbitmq.publish_client_updated(db_client.id, {
        "nom": db_client.nom,
        "email": db_client.email
    })
    return db_client

@router.delete("/{client_id}", status_code=204)
def delete_customer(client_id: int, db: Session = Depends(get_db)):
    success = crud.delete_client(db, client_id=client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    # Publier sur RabbitMQ
    rabbitmq.publish_client_deleted(client_id)
Critères d'acceptation
POST /customers publie client.created
PUT /customers/{id} publie client.updated
DELETE /customers/{id} publie client.deleted
L'API fonctionne même si RabbitMQ est down
🎫 TICKET #006 — Créer module RabbitMQ pour api-produits
Priorité : 🔴 Haute
Estimation : 30 min

Description
Même logique que #004 mais pour les produits.

Fichiers à créer
api-produits/app/rabbitmq.py
Événements à publier
produit.created — Nouveau produit ajouté
produit.updated — Produit modifié (prix, stock, etc.)
produit.deleted — Produit supprimé
produit.stock_low — Stock < 10 unités (alerte)
Critères d'acceptation
Messages publiés pour CRUD produits
Alerte stock_low quand stock < 10
Routing keys : produit.created, produit.updated, produit.deleted, produit.stock_low
🎫 TICKET #007 — Intégrer RabbitMQ dans les routes api-produits
Priorité : 🔴 Haute
Estimation : 20 min
Dépend de : #006

Fichiers à modifier
api-produits/app/routes.py
Critères d'acceptation
Tous les endpoints CRUD publient sur RabbitMQ
Vérification du stock après update → alerte si < 10
🎫 TICKET #008 — Créer consumer RabbitMQ pour api-commandes
Priorité : 🔴 Haute
Estimation : 1h

Description
api-commandes doit écouter les événements des autres services pour maintenir la cohérence (ex: si un client est supprimé, que faire de ses commandes ?).

Fichiers à créer
api-commandes/app/rabbitmq.py
api-commandes/app/consumer.py
Code attendu (consumer.py)
import pika
import json
import os
from .database import SessionLocal
from . import crud

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def callback_client_deleted(ch, method, properties, body):
    """Quand un client est supprimé, marquer ses commandes comme 'client_supprime'"""
    data = json.loads(body)
    client_id = data.get("client_id")
    
    db = SessionLocal()
    try:
        # Option 1: Supprimer les commandes du client
        # Option 2: Marquer les commandes (recommandé)
        commandes = crud.get_commandes_by_client(db, client_id)
        for commande in commandes:
            crud.update_commande(db, commande.id, {"statut": "client_supprime"})
    finally:
        db.close()
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

def callback_produit_deleted(ch, method, properties, body):
    """Quand un produit est supprimé, notifier les commandes en attente"""
    data = json.loads(body)
    produit_id = data.get("produit_id")
    # Logique métier...
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    """Lance le consumer RabbitMQ"""
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    
    channel.exchange_declare(exchange='payetonkawa', exchange_type='topic', durable=True)
    
    # Queue pour les événements clients
    channel.queue_declare(queue='commandes_client_events', durable=True)
    channel.queue_bind(exchange='payetonkawa', queue='commandes_client_events', routing_key='client.*')
    
    # Queue pour les événements produits
    channel.queue_declare(queue='commandes_produit_events', durable=True)
    channel.queue_bind(exchange='payetonkawa', queue='commandes_produit_events', routing_key='produit.*')
    
    channel.basic_consume(queue='commandes_client_events', on_message_callback=callback_client_deleted)
    channel.basic_consume(queue='commandes_produit_events', on_message_callback=callback_produit_deleted)
    
    print("Consumer démarré, en attente de messages...")
    channel.start_consuming()
Critères d'acceptation
Consumer écoute client.* et produit.*
client.deleted → marque les commandes du client
produit.deleted → gère les commandes avec ce produit
Consumer démarre en parallèle de l'API (thread ou process séparé)
🎫 TICKET #009 — Ajouter démarrage consumer dans docker-compose
Priorité : 🟡 Moyenne
Estimation : 15 min
Dépend de : #008

Description
Ajouter un service séparé pour le consumer RabbitMQ dans docker-compose.

Fichiers à modifier
docker-compose.yml
api-commandes/Dockerfile (optionnel: créer un entrypoint)
Ajout docker-compose.yml
  consumer-commandes:
    build: ./api-commandes
    command: python -m app.consumer
    environment:
      DATABASE_URL: postgresql://faouz:faouz2020@db-commandes:5432/commandes_db
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - db-commandes
      - rabbitmq
    restart: unless-stopped
Critères d'acceptation
Service consumer-commandes ajouté
Démarre après RabbitMQ (depends_on)
Restart automatique si crash
PHASE 3 - TESTS


🎫 TICKET #010 — Créer fixtures de test (conftest.py) pour api-clients
Priorité : 🔴 Haute
Estimation : 30 min

Description
Créer les fixtures pytest pour tester l'API avec une base de données de test (SQLite en mémoire).

Fichiers à créer
api-clients/tests/__init__.py
api-clients/tests/conftest.py
Code attendu (conftest.py)
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Base de données SQLite en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Crée une session de base de données pour chaque test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Crée un client de test avec la DB de test"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_client():
    """Données de test pour un client"""
    return {
        "nom": "Jean Dupont",
        "email": "jean.dupont@example.com",
        "adresse": "123 Rue du Café, Paris",
        "telephone": "0612345678"
    }
Critères d'acceptation
SQLite en mémoire pour isolation des tests
Fixture client pour TestClient
Fixture db_session pour accès direct DB
Fixture sample_client avec données de test
Base reset entre chaque test


🎫 TICKET #011 — Écrire tests unitaires api-clients
Priorité : 🔴 Haute
Estimation : 45 min
Dépend de : #010

Fichiers à créer
api-clients/tests/test_routes.py
Tests à écrire
import pytest

class TestCustomersAPI:
    """Tests pour l'API Clients"""
    
    # === CREATE ===
    def test_create_customer_success(self, client, sample_client):
        """POST /customers - Création réussie"""
        response = client.post("/customers/", json=sample_client)
        assert response.status_code == 201
        data = response.json()
        assert data["nom"] == sample_client["nom"]
        assert data["email"] == sample_client["email"]
        assert "id" in data
    
    def test_create_customer_invalid_email(self, client):
        """POST /customers - Email invalide"""
        response = client.post("/customers/", json={
            "nom": "Test",
            "email": "invalid-email",
            "adresse": "Test",
            "telephone": "0600000000"
        })
        assert response.status_code == 422  # Validation error
    
    def test_create_customer_missing_fields(self, client):
        """POST /customers - Champs manquants"""
        response = client.post("/customers/", json={"nom": "Test"})
        assert response.status_code == 422
    
    # === READ ===
    def test_get_customers_empty(self, client):
        """GET /customers - Liste vide"""
        response = client.get("/customers/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_customers_list(self, client, sample_client):
        """GET /customers - Liste avec données"""
        client.post("/customers/", json=sample_client)
        response = client.get("/customers/")
        assert response.status_code == 200
        assert len(response.json()) == 1
    
    def test_get_customer_by_id(self, client, sample_client):
        """GET /customers/{id} - Client existant"""
        create_response = client.post("/customers/", json=sample_client)
        customer_id = create_response.json()["id"]
        
        response = client.get(f"/customers/{customer_id}")
        assert response.status_code == 200
        assert response.json()["id"] == customer_id
    
    def test_get_customer_not_found(self, client):
        """GET /customers/{id} - Client inexistant"""
        response = client.get("/customers/99999")
        assert response.status_code == 404
    
    # === UPDATE ===
    def test_update_customer_success(self, client, sample_client):
        """PUT /customers/{id} - Modification réussie"""
        create_response = client.post("/customers/", json=sample_client)
        customer_id = create_response.json()["id"]
        
        response = client.put(f"/customers/{customer_id}", json={"nom": "Nouveau Nom"})
        assert response.status_code == 200
        assert response.json()["nom"] == "Nouveau Nom"
        assert response.json()["email"] == sample_client["email"]  # Non modifié
    
    def test_update_customer_not_found(self, client):
        """PUT /customers/{id} - Client inexistant"""
        response = client.put("/customers/99999", json={"nom": "Test"})
        assert response.status_code == 404
    
    # === DELETE ===
    def test_delete_customer_success(self, client, sample_client):
        """DELETE /customers/{id} - Suppression réussie"""
        create_response = client.post("/customers/", json=sample_client)
        customer_id = create_response.json()["id"]
        
        response = client.delete(f"/customers/{customer_id}")
        assert response.status_code == 204
        
        # Vérifier suppression
        get_response = client.get(f"/customers/{customer_id}")
        assert get_response.status_code == 404
    
    def test_delete_customer_not_found(self, client):
        """DELETE /customers/{id} - Client inexistant"""
        response = client.delete("/customers/99999")
        assert response.status_code == 404

class TestRootEndpoint:
    """Tests pour l'endpoint racine"""
    
    def test_root(self, client):
        """GET / - Message de bienvenue"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Bienvenue" in response.json()["message"]
Critères d'acceptation
Test CREATE : succès, email invalide, champs manquants
Test READ : liste vide, liste avec données, par ID, 404
Test UPDATE : succès, 404
Test DELETE : succès, 404
Tous les tests passent avec pytest


🎫 TICKET #012 — Créer tests pour api-produits
Priorité : 🔴 Haute
Estimation : 45 min

Fichiers à créer
api-produits/tests/__init__.py
api-produits/tests/conftest.py
api-produits/tests/test_routes.py
Tests spécifiques produits
Création produit avec prix et stock
Mise à jour du stock
Validation prix > 0
Validation stock >= 0
Filtrage par catégorie (si implémenté)
Critères d'acceptation
Même structure que api-clients
Tests CRUD complets
Validation des contraintes métier (prix, stock)


🎫 TICKET #013 — Créer tests pour api-commandes
Priorité : 🔴 Haute
Estimation : 45 min

Fichiers à créer
api-commandes/tests/__init__.py
api-commandes/tests/conftest.py
api-commandes/tests/test_routes.py
Tests spécifiques commandes
Création commande avec client_id et produits
Récupération commandes par client
Mise à jour statut (en_attente → validee → expediee → livree)
Calcul total automatique
Validation client_id existe (si vérifié)
Critères d'acceptation
Tests CRUD complets
Test filtrage par client
Test transitions de statut

🎫 TICKET #014 — Configurer couverture de code (pytest-cov)
Priorité : 🟡 Moyenne
Estimation : 15 min
Dépend de : #011, #012, #013

Description
Ajouter la configuration pour mesurer la couverture de code.

Fichiers à créer/modifier
pytest.ini (racine du projet)
Contenu pytest.ini
[pytest]
testpaths = api-clients/tests api-produits/tests api-commandes/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=api-clients/app --cov=api-produits/app --cov=api-commandes/app --cov-report=html --cov-report=term-missing
Critères d'acceptation
pytest lance tous les tests des 3 APIs
Rapport de couverture généré (HTML + terminal)
Objectif : > 80% de couverture
PHASE 4 - SÉCURITÉ



🎫 TICKET #015 — Implémenter authentification API Key
Priorité : 🔴 Haute
Estimation : 45 min

Description
Protéger les APIs avec une clé API dans le header X-API-Key.

Fichiers à créer
api-clients/app/auth.py
api-produits/app/auth.py
api-commandes/app/auth.py
Code attendu (auth.py)
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
import os

API_KEY = os.getenv("API_KEY", "dev-key-change-in-prod")
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Vérifie la clé API"""
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key manquante"
        )
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key invalide"
        )
    return api_key
Critères d'acceptation
Header X-API-Key requis sur toutes les routes (sauf / et /docs)
401 si clé manquante
403 si clé invalide
Clé configurable via variable d'environnement


🎫 TICKET #016 — Protéger les routes avec l'API Key
Priorité : 🔴 Haute
Estimation : 20 min
Dépend de : #015

Description
Ajouter la dépendance verify_api_key sur toutes les routes protégées.

Fichiers à modifier
api-clients/app/routes.py
api-produits/app/routes.py
api-commandes/app/routes.py
Modification attendue
from .auth import verify_api_key

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[Depends(verify_api_key)]  # Protège toutes les routes du router
)
Critères d'acceptation
Toutes les routes CRUD protégées
Route / (racine) accessible sans clé
/docs accessible sans clé (pour dev)
🎫 TICKET #017 — Ajouter validation et sanitization des entrées
Priorité : 🟡 Moyenne
Estimation : 30 min

Description
Renforcer la validation des données entrantes pour éviter les injections.

Fichiers à modifier
api-clients/app/schemas.py
api-produits/app/schemas.py
api-commandes/app/schemas.py
Améliorations
from pydantic import BaseModel, EmailStr, Field, validator
import re

class ClientCreate(BaseModel):
    nom: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    adresse: str = Field(..., min_length=5, max_length=200)
    telephone: str = Field(..., pattern=r'^0[1-9][0-9]{8}$')
    
    @validator('nom')
    def nom_must_be_valid(cls, v):
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\-]+$', v):
            raise ValueError('Le nom ne doit contenir que des lettres')
        return v.strip()

class ProduitCreate(BaseModel):
    nom: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., max_length=500)
    prix: float = Field(..., gt=0, description="Prix doit être > 0")
    stock: int = Field(..., ge=0, description="Stock doit être >= 0")
Critères d'acceptation
Longueurs min/max sur tous les champs texte
Regex téléphone français
Prix > 0, Stock >= 0
Sanitization des espaces (strip)
🎫 TICKET #018 — Configurer CORS restrictif pour production
Priorité : 🟡 Moyenne
Estimation : 15 min

Description
Remplacer allow_origins=["*"] par une liste d'origines autorisées configurable.

Fichiers à modifier
api-clients/app/main.py
api-produits/app/main.py
api-commandes/app/main.py
Code attendu
import os

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:4321").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
Critères d'acceptation
Origines configurables via ALLOWED_ORIGINS
Par défaut : localhost pour dev
Méthodes limitées à celles utilisées
PHASE 5 - CI/CD
🎫 TICKET #019 — Créer workflow GitHub Actions pour tests
Priorité : 🔴 Haute
Estimation : 45 min

Fichiers à créer
.github/workflows/ci.yml
Code attendu
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-api-clients:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          cd api-clients
          pip install -r requirements.txt
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
        run: |
          cd api-clients
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: api-clients/coverage.xml

  test-api-produits:
    runs-on: ubuntu-latest
    # ... même structure ...

  test-api-commandes:
    runs-on: ubuntu-latest
    # ... même structure ...

  build-docker:
    needs: [test-api-clients, test-api-produits, test-api-commandes]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker images
        run: |
          docker build -t payetonkawa/api-clients:latest ./api-clients
          docker build -t payetonkawa/api-produits:latest ./api-produits
          docker build -t payetonkawa/api-commandes:latest ./api-commandes
Critères d'acceptation
Tests lancés sur push main/develop
Tests lancés sur PR vers main
3 jobs parallèles (1 par API)
Build Docker après succès des tests (main uniquement)
Upload couverture vers Codecov
🎫 TICKET #020 — Ajouter badge de statut CI dans README
Priorité : 🟢 Basse
Estimation : 5 min
Dépend de : #019

Fichiers à modifier
README.md
Ajout
# PayeTonKawa

![CI](https://github.com/Don-bot667/payetonkawa/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/Don-bot667/payetonkawa/branch/main/graph/badge.svg)](https://codecov.io/gh/Don-bot667/payetonkawa)

...
PHASE 6 - MONITORING
🎫 TICKET #021 — Ajouter logging structuré
Priorité : 🟡 Moyenne
Estimation : 30 min

Description
Implémenter des logs structurés (JSON) pour faciliter l'analyse.

Fichiers à créer
api-clients/app/logging_config.py
api-produits/app/logging_config.py
api-commandes/app/logging_config.py
Code attendu
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if hasattr(record, 'request_id'):
            log_obj['request_id'] = record.request_id
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_logging():
    logger = logging.getLogger("payetonkawa")
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    return logger

logger = setup_logging()
Utilisation dans routes.py
from .logging_config import logger

@router.post("/", ...)
def create_customer(...):
    logger.info(f"Création client: {client.email}")
    db_client = crud.create_client(...)
    logger.info(f"Client créé: id={db_client.id}")
    return db_client
Critères d'acceptation
Logs en format JSON
Timestamp, level, message, module inclus
Logs sur CREATE, UPDATE, DELETE
Logs des erreurs avec stack trace
🎫 TICKET #022 — Ajouter endpoint /health pour healthcheck
Priorité : 🟡 Moyenne
Estimation : 20 min

Description
Ajouter un endpoint de healthcheck pour Docker/Kubernetes.

Fichiers à modifier
api-clients/app/main.py
api-produits/app/main.py
api-commandes/app/main.py
Code attendu
from sqlalchemy import text

@app.get("/health")
def health_check():
    """Healthcheck endpoint"""
    try:
        # Vérifier connexion DB
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "ok" else "unhealthy",
        "database": db_status,
        "version": "1.0.0"
    }
Modification docker-compose.yml
api-clients:
  ...
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
Critères d'acceptation
Endpoint /health sur chaque API
Vérifie connexion DB
Retourne status healthy/unhealthy
Healthcheck configuré dans docker-compose
PHASE 7 - DOCUMENTATION
🎫 TICKET #023 — Rédiger documentation architecture
Priorité : 🟡 Moyenne
Estimation : 1h

Fichiers à créer
docs/architecture.md
Contenu attendu
Vue d'ensemble — Schéma ASCII ou Mermaid de l'architecture
Services — Description de chaque API
Communication — Comment les services communiquent (RabbitMQ)
Base de données — Schéma de chaque DB
Flux de données — Exemple de création de commande
Déploiement — Comment lancer le projet
Exemple de schéma Mermaid
```mermaid
graph TB
    subgraph Frontend
        A[Site Client<br>Astro] --> |HTTP| B[API Gateway]
        C[Gestion Admin<br>Astro] --> |HTTP| B
    end
    
    subgraph Backend
        B --> D[API Clients<br>:8000]
        B --> E[API Produits<br>:8001]
        B --> F[API Commandes<br>:8002]
    end
    
    subgraph Messaging
        D --> |publish| G[RabbitMQ]
        E --> |publish| G
        G --> |consume| F
    end
    
    subgraph Databases
        D --> H[(PostgreSQL<br>clients_db)]
        E --> I[(PostgreSQL<br>produits_db)]
        F --> J[(PostgreSQL<br>commandes_db)]
    end

#### Critères d'acceptation
- [ ] Schéma visuel de l'architecture
- [ ] Description de chaque composant
- [ ] Explication de la communication RabbitMQ
- [ ] Instructions de déploiement local

---

### 🎫 TICKET #024 — Rédiger documentation sécurité

**Priorité :** 🟡 Moyenne  
**Estimation :** 30 min  

#### Fichiers à créer
docs/securite.md


#### Contenu attendu
1. **Authentification** — API Key, comment l'obtenir
2. **Autorisation** — Qui peut faire quoi
3. **Validation** — Comment les données sont validées
4. **CORS** — Politique d'origine
5. **Secrets** — Comment gérer les secrets (variables d'env)
6. **Bonnes pratiques** — Recommandations

---

### 🎫 TICKET #025 — Compléter le README principal

**Priorité :** 🟡 Moyenne  
**Estimation :** 45 min  

#### Fichiers à modifier
README.md


#### Structure attendue
```markdown
# ☕ PayeTonKawa

> Application de vente de café en ligne - Architecture Microservices

![CI](badge)
[![codecov](badge)](link)

## 📋 Table des matières
- [Présentation](#présentation)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [API Documentation](#api-documentation)
- [Tests](#tests)
- [Déploiement](#déploiement)
- [Contribution](#contribution)

## 🎯 Présentation
PayeTonKawa est une application e-commerce...

## 🏗️ Architecture
[Schéma]

### Services
| Service | Port | Description |
|---------|------|-------------|
| api-clients | 8000 | Gestion des clients |
| api-produits | 8001 | Catalogue produits |
| api-commandes | 8002 | Gestion des commandes |
| RabbitMQ | 5672/15672 | Message broker |

## 🚀 Installation

### Prérequis
- Docker & Docker Compose
- Git

### Lancement
\`\`\`bash
git clone https://github.com/Don-bot667/payetonkawa.git
cd payetonkawa
docker-compose up -d
\`\`\`

### URLs
- API Clients: http://localhost:8000/docs
- API Produits: http://localhost:8001/docs
- API Commandes: http://localhost:8002/docs
- RabbitMQ Management: http://localhost:15672

## 📖 API Documentation
Chaque API expose une documentation Swagger sur `/docs`.

### Authentification
Ajouter le header `X-API-Key` avec votre clé.

## 🧪 Tests
\`\`\`bash
# Lancer tous les tests
pytest

# Avec couverture
pytest --cov
\`\`\`

## 👨‍💻 Auteur
Don - 2026
Critères d'acceptation
Présentation claire du projet
Instructions d'installation complètes
Documentation des endpoints
Guide de contribution
PHASE 8 - POSTMAN
🎫 TICKET #026 — Créer collection Postman
Priorité : 🟢 Basse
Estimation : 45 min

Fichiers à créer
postman/PayeTonKawa.postman_collection.json
postman/PayeTonKawa.postman_environment.json
Contenu de la collection
📁 PayeTonKawa
├── 📁 Clients
│   ├── GET Liste des clients
│   ├── GET Client par ID
│   ├── POST Créer un client
│   ├── PUT Modifier un client
│   └── DELETE Supprimer un client
├── 📁 Produits
│   ├── GET Liste des produits
│   ├── GET Produit par ID
│   ├── POST Créer un produit
│   ├── PUT Modifier un produit
│   └── DELETE Supprimer un produit
├── 📁 Commandes
│   ├── GET Liste des commandes
│   ├── GET Commande par ID
│   ├── GET Commandes d'un client
│   ├── POST Créer une commande
│   ├── PUT Modifier statut commande
│   └── DELETE Supprimer une commande
└── 📁 Health
    ├── GET Health API Clients
    ├── GET Health API Produits
    └── GET Health API Commandes
Variables d'environnement
{
  "base_url_clients": "http://localhost:8000",
  "base_url_produits": "http://localhost:8001",
  "base_url_commandes": "http://localhost:8002",
  "api_key": "dev-key-change-in-prod"
}
Critères d'acceptation
Toutes les routes documentées
Variables d'environnement utilisées
Exemples de body pour POST/PUT
Tests automatiques dans Postman (status code, JSON schema)
📊 RÉCAPITULATIF
Phase	Tickets	Estimation
1. Corrections Backend	#001-#003	40 min
2. RabbitMQ	#004-#009	3h30
3. Tests	#010-#014	3h
4. Sécurité	#015-#018	1h50
5. CI/CD	#019-#020	50 min
6. Monitoring	#021-#022	50 min
7. Documentation	#023-#025	2h15
8. Postman	#026	45 min
TOTAL	26 tickets	~14h
🎯 ORDRE DE PRIORITÉ RECOMMANDÉ
Sprint 1 (Fondations) — ~4h
#001 — PUT /customers
#002 — init.py
#010 — Fixtures tests
#011 — Tests api-clients
#012 — Tests api-produits
#013 — Tests api-commandes
Sprint 2 (Sécurité + CI) — ~3h
#015 — Auth API Key
#016 — Protéger routes
#017 — Validation inputs
#019 — GitHub Actions
Sprint 3 (RabbitMQ) — ~3h30
#003 — Config.py
#004 — RabbitMQ clients
#005 — Intégrer routes clients
#006 — RabbitMQ produits
#007 — Intégrer routes produits
#008 — Consumer commandes
#009 — Docker consumer
Sprint 4 (Finitions) — ~3h30
#014 — Couverture code
#018 — CORS restrictif
#020 — Badge CI
#021 — Logging
#022 — Healthcheck
#023 — Doc architecture
#024 — Doc sécurité
#025 — README
#026 — Collection Postman