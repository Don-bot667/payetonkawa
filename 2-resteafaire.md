# 🎫 TICKETS MSPR PayeTonKawa

**Dernière mise à jour :** 2026-02-25  
**Statut actuel :** 67 tests ✅ | 87% couverture | RabbitMQ ❌ | CI/CD ❌  
**Temps total estimé :** ~12h

---

## 📋 SOMMAIRE

| Phase | Tickets | Priorité | Temps |
|-------|---------|----------|-------|
| 1. RabbitMQ | #001-#006 | 🔴 Critique | ~3h30 |
| 2. CI/CD | #007-#009 | 🔴 Critique | ~1h30 |
| 3. Monitoring | #010-#012 | 🟡 Important | ~1h |
| 4. Tests | #013-#014 | 🟡 Important | ~1h |
| 5. Documentation | #015-#019 | 🔴 Critique | ~3h |
| 6. Postman | #020 | 🔴 Critique | ~45min |
| 7. Conduite du changement | #021 | 🔴 Critique | ~1h30 |

---

# PHASE 1 — RABBITMQ (Message Broker)
> **Obligatoire** : synchronisation entre micro-services

---

## 🎫 TICKET #001 — Créer module RabbitMQ pour api-clients

**Priorité :** 🔴 Critique  
**Estimation :** 30 min  
**Fichiers à créer :** `api-clients/app/rabbitmq.py`

### Description
Implémenter la connexion RabbitMQ et la publication de messages quand un client est créé, modifié ou supprimé.

### Code à implémenter

```python
# api-clients/app/rabbitmq.py
import pika
import json
import os
import logging

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = "payetonkawa"

def get_connection():
    """Établit une connexion à RabbitMQ"""
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        return pika.BlockingConnection(parameters)
    except Exception as e:
        logger.error(f"Erreur connexion RabbitMQ: {e}")
        return None

def publish_message(routing_key: str, message: dict):
    """Publie un message sur RabbitMQ"""
    try:
        connection = get_connection()
        if not connection:
            return False
            
        channel = connection.channel()
        
        # Déclare l'exchange (type: topic pour flexibilité)
        channel.exchange_declare(
            exchange=EXCHANGE_NAME, 
            exchange_type='topic', 
            durable=True
        )
        
        # Publie le message
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Message persistant
                content_type='application/json'
            )
        )
        connection.close()
        logger.info(f"Message publié: {routing_key}")
        return True
    except Exception as e:
        logger.error(f"Erreur publication RabbitMQ: {e}")
        return False

# === Fonctions spécifiques clients ===

def publish_client_created(client_id: int, client_data: dict):
    """Publie un événement de création de client"""
    publish_message("client.created", {
        "event": "client_created",
        "client_id": client_id,
        "data": client_data,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    })

def publish_client_updated(client_id: int, client_data: dict):
    """Publie un événement de modification de client"""
    publish_message("client.updated", {
        "event": "client_updated",
        "client_id": client_id,
        "data": client_data,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    })

def publish_client_deleted(client_id: int):
    """Publie un événement de suppression de client"""
    publish_message("client.deleted", {
        "event": "client_deleted",
        "client_id": client_id,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    })
```

### Dépendance à ajouter
```bash
# api-clients/requirements.txt
pika==1.3.2
```

### Critères d'acceptation
- [ ] Connexion à RabbitMQ fonctionnelle
- [ ] Exchange "payetonkawa" créé (type: topic, durable)
- [ ] 3 fonctions : `publish_client_created`, `publish_client_updated`, `publish_client_deleted`
- [ ] Gestion des erreurs (l'API ne crash pas si RabbitMQ down)
- [ ] Logs des publications

---

## 🎫 TICKET #002 — Intégrer RabbitMQ dans les routes api-clients

**Priorité :** 🔴 Critique  
**Estimation :** 15 min  
**Dépend de :** #001  
**Fichiers à modifier :** `api-clients/app/routes.py`

### Modifications à apporter

```python
# api-clients/app/routes.py
from . import rabbitmq  # Ajouter cet import

# Modifier POST /customers/
@router.post("/", response_model=schemas.ClientResponse, status_code=201)
def create_customer(client: schemas.ClientCreate, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    db_client = crud.create_client(db=db, client=client)
    # Publier sur RabbitMQ
    rabbitmq.publish_client_created(db_client.id, {
        "nom": db_client.nom,
        "email": db_client.email,
        "adresse": db_client.adresse,
        "telephone": db_client.telephone
    })
    return db_client

# Modifier PUT /customers/{id}
@router.put("/{client_id}", response_model=schemas.ClientResponse)
def update_customer(client_id: int, client: schemas.ClientUpdate, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    db_client = crud.update_client(db, client_id=client_id, client=client)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    # Publier sur RabbitMQ
    rabbitmq.publish_client_updated(db_client.id, {
        "nom": db_client.nom,
        "email": db_client.email,
        "adresse": db_client.adresse,
        "telephone": db_client.telephone
    })
    return db_client

# Modifier DELETE /customers/{id}
@router.delete("/{client_id}", status_code=204)
def delete_customer(client_id: int, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    success = crud.delete_client(db, client_id=client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    # Publier sur RabbitMQ
    rabbitmq.publish_client_deleted(client_id)
```

### Critères d'acceptation
- [ ] POST /customers publie `client.created`
- [ ] PUT /customers/{id} publie `client.updated`
- [ ] DELETE /customers/{id} publie `client.deleted`
- [ ] L'API fonctionne même si RabbitMQ est down

---

## 🎫 TICKET #003 — Créer module RabbitMQ pour api-produits

**Priorité :** 🔴 Critique  
**Estimation :** 30 min  
**Fichiers à créer :** `api-produits/app/rabbitmq.py`

### Description
Même logique que #001 mais pour les produits, avec une alerte stock bas.

### Événements à publier
| Routing Key | Déclencheur |
|-------------|-------------|
| `produit.created` | Nouveau produit ajouté |
| `produit.updated` | Produit modifié |
| `produit.deleted` | Produit supprimé |
| `produit.stock_low` | Stock < 10 unités |

### Code spécifique
```python
def publish_produit_stock_low(produit_id: int, produit_nom: str, stock: int):
    """Alerte quand le stock est bas"""
    publish_message("produit.stock_low", {
        "event": "produit_stock_low",
        "produit_id": produit_id,
        "produit_nom": produit_nom,
        "stock_actuel": stock,
        "seuil_alerte": 10,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    })
```

### Critères d'acceptation
- [ ] 4 fonctions de publication
- [ ] Alerte `stock_low` déclenchée si stock < 10 après update
- [ ] Dépendance `pika` dans requirements.txt

---

## 🎫 TICKET #004 — Intégrer RabbitMQ dans les routes api-produits

**Priorité :** 🔴 Critique  
**Estimation :** 15 min  
**Dépend de :** #003  
**Fichiers à modifier :** `api-produits/app/routes.py`

### Logique spéciale
Après chaque PUT, vérifier si le stock < 10 :
```python
if db_produit.stock < 10:
    rabbitmq.publish_produit_stock_low(db_produit.id, db_produit.nom, db_produit.stock)
```

### Critères d'acceptation
- [ ] Tous les endpoints CRUD publient sur RabbitMQ
- [ ] Vérification du stock après update → alerte si < 10

---

## 🎫 TICKET #005 — Créer module RabbitMQ pour api-commandes

**Priorité :** 🔴 Critique  
**Estimation :** 30 min  
**Fichiers à créer :** `api-commandes/app/rabbitmq.py`

### Événements à publier
| Routing Key | Déclencheur |
|-------------|-------------|
| `commande.created` | Nouvelle commande |
| `commande.updated` | Statut modifié |
| `commande.deleted` | Commande supprimée |

### Critères d'acceptation
- [ ] Publication sur les 3 événements
- [ ] Intégration dans routes.py

---

## 🎫 TICKET #006 — Créer consumer RabbitMQ pour api-commandes

**Priorité :** 🔴 Critique  
**Estimation :** 45 min  
**Dépend de :** #001, #003, #005  
**Fichiers à créer :** `api-commandes/app/consumer.py`

### Description
L'api-commandes doit écouter les événements des autres services pour maintenir la cohérence.

### Code à implémenter

```python
# api-commandes/app/consumer.py
import pika
import json
import os
import logging
from .database import SessionLocal
from . import crud

logger = logging.getLogger(__name__)
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def callback_client_deleted(ch, method, properties, body):
    """Quand un client est supprimé, marquer ses commandes"""
    try:
        data = json.loads(body)
        client_id = data.get("client_id")
        logger.info(f"Client supprimé détecté: {client_id}")
        
        db = SessionLocal()
        try:
            # Marquer les commandes du client comme "client_supprime"
            commandes = crud.get_commandes_by_client(db, client_id)
            for commande in commandes:
                crud.update_commande_statut(db, commande.id, "client_supprime")
            logger.info(f"{len(commandes)} commandes marquées")
        finally:
            db.close()
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Erreur traitement client.deleted: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def callback_produit_deleted(ch, method, properties, body):
    """Quand un produit est supprimé"""
    try:
        data = json.loads(body)
        produit_id = data.get("produit_id")
        logger.info(f"Produit supprimé détecté: {produit_id}")
        # Logique métier si nécessaire
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Erreur traitement produit.deleted: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_consumer():
    """Lance le consumer RabbitMQ"""
    logger.info("Démarrage du consumer RabbitMQ...")
    
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    
    # Déclarer l'exchange
    channel.exchange_declare(exchange='payetonkawa', exchange_type='topic', durable=True)
    
    # Queue pour les événements clients
    channel.queue_declare(queue='commandes_client_events', durable=True)
    channel.queue_bind(exchange='payetonkawa', queue='commandes_client_events', routing_key='client.deleted')
    
    # Queue pour les événements produits
    channel.queue_declare(queue='commandes_produit_events', durable=True)
    channel.queue_bind(exchange='payetonkawa', queue='commandes_produit_events', routing_key='produit.deleted')
    
    # Consommer les messages
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='commandes_client_events', on_message_callback=callback_client_deleted)
    channel.basic_consume(queue='commandes_produit_events', on_message_callback=callback_produit_deleted)
    
    logger.info("Consumer démarré, en attente de messages...")
    channel.start_consuming()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_consumer()
```

### Ajout docker-compose.yml
```yaml
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
```

### Critères d'acceptation
- [ ] Consumer écoute `client.deleted` et `produit.deleted`
- [ ] Commandes marquées si client supprimé
- [ ] Service ajouté dans docker-compose
- [ ] Logs des messages reçus

---

# PHASE 2 — CI/CD (Intégration Continue)
> **Obligatoire** : automatisation des tests et déploiements

---

## 🎫 TICKET #007 — Créer workflow GitHub Actions pour tests

**Priorité :** 🔴 Critique  
**Estimation :** 45 min  
**Fichiers à créer :** `.github/workflows/ci.yml`

### Code à implémenter

```yaml
# .github/workflows/ci.yml
name: CI Pipeline PayeTonKawa

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.12'

jobs:
  # === Tests API Clients ===
  test-api-clients:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: api-clients
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_clients
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
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
          cache-dependency-path: api-clients/requirements.txt
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_clients
          API_KEY: test-key
        run: pytest --cov=app --cov-report=xml --cov-report=term-missing -v
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: api-clients/coverage.xml
          flags: api-clients
          fail_ci_if_error: false

  # === Tests API Produits ===
  test-api-produits:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: api-produits
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_produits
        ports:
          - 5433:5432
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
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
          cache-dependency-path: api-produits/requirements.txt
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql://test:test@localhost:5433/test_produits
          API_KEY: test-key
        run: pytest --cov=app --cov-report=xml --cov-report=term-missing -v
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: api-produits/coverage.xml
          flags: api-produits

  # === Tests API Commandes ===
  test-api-commandes:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: api-commandes
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_commandes
        ports:
          - 5434:5432
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
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
          cache-dependency-path: api-commandes/requirements.txt
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql://test:test@localhost:5434/test_commandes
          API_KEY: test-key
        run: pytest --cov=app --cov-report=xml --cov-report=term-missing -v
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: api-commandes/coverage.xml
          flags: api-commandes

  # === Build Docker Images ===
  build-docker:
    needs: [test-api-clients, test-api-produits, test-api-commandes]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build API Clients
        uses: docker/build-push-action@v5
        with:
          context: ./api-clients
          push: false
          tags: payetonkawa/api-clients:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Build API Produits
        uses: docker/build-push-action@v5
        with:
          context: ./api-produits
          push: false
          tags: payetonkawa/api-produits:${{ github.sha }}
      
      - name: Build API Commandes
        uses: docker/build-push-action@v5
        with:
          context: ./api-commandes
          push: false
          tags: payetonkawa/api-commandes:${{ github.sha }}
      
      - name: Summary
        run: |
          echo "### ✅ Build successful!" >> $GITHUB_STEP_SUMMARY
          echo "Images built:" >> $GITHUB_STEP_SUMMARY
          echo "- payetonkawa/api-clients:${{ github.sha }}" >> $GITHUB_STEP_SUMMARY
          echo "- payetonkawa/api-produits:${{ github.sha }}" >> $GITHUB_STEP_SUMMARY
          echo "- payetonkawa/api-commandes:${{ github.sha }}" >> $GITHUB_STEP_SUMMARY
```

### Critères d'acceptation
- [ ] Tests lancés sur push main/develop
- [ ] Tests lancés sur PR vers main
- [ ] 3 jobs parallèles (1 par API)
- [ ] Build Docker après succès des tests (main uniquement)
- [ ] Upload couverture vers Codecov

---

## 🎫 TICKET #008 — Ajouter badges CI dans README

**Priorité :** 🟢 Basse  
**Estimation :** 5 min  
**Dépend de :** #007  
**Fichiers à modifier :** `README.md`

### Ajout en haut du README
```markdown
# ☕ PayeTonKawa

![CI](https://github.com/Don-bot667/payetonkawa/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/Don-bot667/payetonkawa/branch/main/graph/badge.svg)](https://codecov.io/gh/Don-bot667/payetonkawa)
```

---

## 🎫 TICKET #009 — Documenter la stratégie GitFlow

**Priorité :** 🟡 Important  
**Estimation :** 20 min  
**Fichiers à créer :** `docs/GITFLOW.md`

### Contenu attendu
```markdown
# Stratégie de Branches - GitFlow

## Branches principales
- `main` : Production, code stable
- `develop` : Développement, intégration

## Branches de travail
- `feature/xxx` : Nouvelles fonctionnalités
- `bugfix/xxx` : Corrections de bugs
- `hotfix/xxx` : Corrections urgentes en production

## Workflow
1. Créer une branche depuis `develop`
2. Développer et commiter
3. Créer une PR vers `develop`
4. Review + merge
5. Release : merge `develop` → `main`

## Convention de commits
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `test:` ajout de tests
- `refactor:` refactoring
```

---

# PHASE 3 — MONITORING
> **Obligatoire** : suivi des APIs et logs

---

## 🎫 TICKET #010 — Ajouter endpoint /health

**Priorité :** 🟡 Important  
**Estimation :** 20 min  
**Fichiers à modifier :** `api-*/app/main.py`

### Code à ajouter (dans chaque main.py)

```python
from sqlalchemy import text
from datetime import datetime

@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint de healthcheck pour Docker/Kubernetes"""
    # Vérifier connexion DB
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "service": "api-clients",  # Adapter selon l'API
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
```

### Ajout docker-compose.yml (pour chaque API)
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Critères d'acceptation
- [ ] Endpoint `/health` sur chaque API
- [ ] Vérifie connexion DB
- [ ] Retourne status healthy/unhealthy
- [ ] Healthcheck configuré dans docker-compose

---

## 🎫 TICKET #011 — Ajouter logging structuré (JSON)

**Priorité :** 🟡 Important  
**Estimation :** 30 min  
**Fichiers à créer :** `api-*/app/logging_config.py`

### Code à implémenter

```python
# api-clients/app/logging_config.py
import logging
import json
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formateur de logs en JSON pour faciliter l'analyse"""
    
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Ajouter request_id si présent
        if hasattr(record, 'request_id'):
            log_obj['request_id'] = record.request_id
        
        # Ajouter exception si présente
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj)

def setup_logging(service_name: str = "api"):
    """Configure le logging pour l'application"""
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    
    # Handler console avec format JSON
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    return logger

# Logger global
logger = setup_logging("payetonkawa")
```

### Utilisation dans routes.py
```python
from .logging_config import logger

@router.post("/", ...)
def create_customer(...):
    logger.info(f"Création client: {client.email}")
    db_client = crud.create_client(...)
    logger.info(f"Client créé avec succès", extra={"client_id": db_client.id})
    return db_client
```

### Critères d'acceptation
- [ ] Logs en format JSON
- [ ] Timestamp ISO 8601
- [ ] Niveau, module, fonction, ligne inclus
- [ ] Logs sur CREATE, UPDATE, DELETE

---

## 🎫 TICKET #012 — Ajouter middleware de logging des requêtes

**Priorité :** 🟡 Important  
**Estimation :** 20 min  
**Fichiers à modifier :** `api-*/app/main.py`

### Code à ajouter

```python
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from .logging_config import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Log de la requête entrante
        logger.info(f"Request started", extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown"
        })
        
        response = await call_next(request)
        
        # Log de la réponse
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Request completed", extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2)
        })
        
        # Ajouter request_id dans le header de réponse
        response.headers["X-Request-ID"] = request_id
        return response

# Dans main.py
app.add_middleware(LoggingMiddleware)
```

### Critères d'acceptation
- [ ] Chaque requête loggée avec : method, path, status_code, duration_ms
- [ ] Request ID unique par requête
- [ ] Header X-Request-ID dans la réponse

---

# PHASE 4 — TESTS
> **Objectif** : atteindre 95% de couverture

---

## 🎫 TICKET #013 — Augmenter couverture tests à 95%

**Priorité :** 🟡 Important  
**Estimation :** 45 min  
**Fichiers à modifier :** `api-*/tests/test_routes.py`

### Tests manquants à ajouter

#### api-clients
```python
# Test email en double
def test_create_customer_duplicate_email(self, client, sample_client):
    """POST /customers - Email déjà existant"""
    client.post("/customers/", json=sample_client, headers={"X-API-Key": "test-key"})
    response = client.post("/customers/", json=sample_client, headers={"X-API-Key": "test-key"})
    assert response.status_code == 400

# Test pagination
def test_get_customers_pagination(self, client, sample_client):
    """GET /customers - Pagination skip/limit"""
    # Créer 5 clients
    for i in range(5):
        data = sample_client.copy()
        data["email"] = f"test{i}@example.com"
        client.post("/customers/", json=data, headers={"X-API-Key": "test-key"})
    
    response = client.get("/customers/?skip=2&limit=2", headers={"X-API-Key": "test-key"})
    assert response.status_code == 200
    assert len(response.json()) == 2
```

#### api-produits
```python
# Test stock négatif
def test_create_product_negative_stock(self, client):
    """POST /products - Stock négatif refusé"""
    response = client.post("/products/", json={
        "nom": "Test",
        "description": "Test",
        "prix": 10.0,
        "stock": -5
    }, headers={"X-API-Key": "test-key"})
    assert response.status_code == 422

# Test prix zéro
def test_create_product_zero_price(self, client):
    """POST /products - Prix zéro refusé"""
    response = client.post("/products/", json={
        "nom": "Test",
        "description": "Test",
        "prix": 0,
        "stock": 10
    }, headers={"X-API-Key": "test-key"})
    assert response.status_code == 422
```

### Critères d'acceptation
- [ ] Couverture ≥ 95% sur chaque API
- [ ] Tests des cas d'erreur (validation, duplicates)
- [ ] Tests de pagination

---

## 🎫 TICKET #014 — Ajouter tests d'intégration RabbitMQ

**Priorité :** 🟡 Important  
**Estimation :** 30 min  
**Dépend de :** #001-#006  
**Fichiers à créer :** `api-*/tests/test_rabbitmq.py`

### Code à implémenter

```python
# api-clients/tests/test_rabbitmq.py
import pytest
from unittest.mock import patch, MagicMock
from app import rabbitmq

class TestRabbitMQ:
    """Tests pour le module RabbitMQ"""
    
    @patch('app.rabbitmq.get_connection')
    def test_publish_message_success(self, mock_conn):
        """Test publication message réussie"""
        mock_channel = MagicMock()
        mock_conn.return_value.channel.return_value = mock_channel
        
        result = rabbitmq.publish_message("test.event", {"data": "test"})
        
        assert result == True
        mock_channel.basic_publish.assert_called_once()
    
    @patch('app.rabbitmq.get_connection')
    def test_publish_message_connection_failed(self, mock_conn):
        """Test publication quand RabbitMQ down"""
        mock_conn.return_value = None
        
        result = rabbitmq.publish_message("test.event", {"data": "test"})
        
        assert result == False
    
    @patch('app.rabbitmq.publish_message')
    def test_publish_client_created(self, mock_publish):
        """Test publication événement client créé"""
        rabbitmq.publish_client_created(1, {"nom": "Test"})
        
        mock_publish.assert_called_once()
        args = mock_publish.call_args
        assert args[0][0] == "client.created"
        assert args[0][1]["client_id"] == 1
```

### Critères d'acceptation
- [ ] Tests avec mock (pas besoin de RabbitMQ réel)
- [ ] Test succès publication
- [ ] Test échec connexion
- [ ] Test pour chaque événement

---

# PHASE 5 — DOCUMENTATION
> **Obligatoire** : documentation technique complète

---

## 🎫 TICKET #015 — Créer documentation architecture

**Priorité :** 🔴 Critique  
**Estimation :** 1h  
**Fichiers à créer :** `docs/ARCHITECTURE.md`

### Contenu attendu

```markdown
# Architecture PayeTonKawa

## Vue d'ensemble

PayeTonKawa utilise une architecture **micro-services** composée de 3 APIs indépendantes communicant via un message broker (RabbitMQ).

## Schéma d'architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  Site Web    │    │   Gestion    │    │  Revendeurs  │       │
│  │   (Astro)    │    │   (Astro)    │    │    (API)     │       │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘       │
└─────────┼───────────────────┼───────────────────┼───────────────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API GATEWAY (CORS + Auth)                    │
└─────────────────────────────────────────────────────────────────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  API Clients    │ │  API Produits   │ │  API Commandes  │
│    :8000        │ │     :8001       │ │     :8002       │
│  ┌───────────┐  │ │  ┌───────────┐  │ │  ┌───────────┐  │
│  │  FastAPI  │  │ │  │  FastAPI  │  │ │  │  FastAPI  │  │
│  └─────┬─────┘  │ │  └─────┬─────┘  │ │  └─────┬─────┘  │
│        │        │ │        │        │ │        │        │
│  ┌─────▼─────┐  │ │  ┌─────▼─────┐  │ │  ┌─────▼─────┐  │
│  │PostgreSQL │  │ │  │PostgreSQL │  │ │  │PostgreSQL │  │
│  │clients_db │  │ │  │produits_db│  │ │  │commandes_db│ │
│  └───────────┘  │ │  └───────────┘  │ │  └───────────┘  │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         │    publish        │    publish        │    consume
         ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                        RABBITMQ                                  │
│  Exchange: payetonkawa (topic)                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                │
│  │client.*     │ │produit.*    │ │commande.*   │                │
│  └─────────────┘ └─────────────┘ └─────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

## Services

| Service | Port | Base de données | Description |
|---------|------|-----------------|-------------|
| api-clients | 8000 | clients_db | Gestion des clients (CRUD) |
| api-produits | 8001 | produits_db | Catalogue produits (CRUD + stock) |
| api-commandes | 8002 | commandes_db | Gestion des commandes |
| RabbitMQ | 5672/15672 | - | Message broker |

## Communication inter-services

### Événements publiés

| Service | Événement | Description |
|---------|-----------|-------------|
| api-clients | `client.created` | Nouveau client créé |
| api-clients | `client.updated` | Client modifié |
| api-clients | `client.deleted` | Client supprimé |
| api-produits | `produit.created` | Nouveau produit |
| api-produits | `produit.updated` | Produit modifié |
| api-produits | `produit.deleted` | Produit supprimé |
| api-produits | `produit.stock_low` | Stock < 10 |
| api-commandes | `commande.created` | Nouvelle commande |
| api-commandes | `commande.updated` | Statut modifié |

### Abonnements

| Service | Écoute | Action |
|---------|--------|--------|
| api-commandes | `client.deleted` | Marque les commandes du client |
| api-commandes | `produit.deleted` | Notifie les commandes concernées |

## Justifications techniques

### Langage : Python + FastAPI
- **Performance** : FastAPI est un des frameworks Python les plus rapides (basé sur Starlette)
- **Productivité** : Validation automatique, documentation OpenAPI auto-générée
- **Typage** : Support natif des type hints Python
- **Async** : Support natif de l'asynchrone

### Base de données : PostgreSQL
- **Fiabilité** : ACID compliant, intégrité référentielle
- **Performance** : Indexation avancée, requêtes optimisées
- **Scalabilité** : Support du partitioning, réplication
- **Écosystème** : Large communauté, outils matures

### Message Broker : RabbitMQ
- **Fiabilité** : Persistance des messages, acknowledgments
- **Flexibilité** : Routing via exchanges (topic, direct, fanout)
- **Monitoring** : Interface web de management
- **Standards** : Support AMQP 0.9.1
```

### Critères d'acceptation
- [ ] Schéma ASCII ou Mermaid de l'architecture
- [ ] Description de chaque service
- [ ] Justification du langage (Python/FastAPI)
- [ ] Justification de la BDD (PostgreSQL)
- [ ] Justification du message broker (RabbitMQ)

---

## 🎫 TICKET #016 — Créer documentation sécurité

**Priorité :** 🔴 Critique  
**Estimation :** 30 min  
**Fichiers à créer :** `docs/SECURITE.md`

### Contenu attendu

```markdown
# Sécurité PayeTonKawa

## Authentification

### API Key
Toutes les APIs sont protégées par une clé API transmise dans le header `X-API-Key`.

```bash
curl -H "X-API-Key: votre-cle-api" https://api.payetonkawa.fr/customers/
```

### Endpoints publics
- `GET /` : Message de bienvenue
- `GET /health` : Healthcheck
- `GET /docs` : Documentation Swagger

## OWASP TOP 10 - Mesures appliquées

| Risque | Mesure |
|--------|--------|
| A01 - Broken Access Control | API Key obligatoire, validation des permissions |
| A02 - Cryptographic Failures | HTTPS en production, mots de passe hashés |
| A03 - Injection | ORM SQLAlchemy (requêtes paramétrées), validation Pydantic |
| A04 - Insecure Design | Architecture micro-services, principe du moindre privilège |
| A05 - Security Misconfiguration | CORS restrictif, headers sécurisés |
| A06 - Vulnerable Components | Dépendances à jour, scan de sécurité CI |
| A07 - Auth Failures | Rate limiting, API Key rotation |
| A08 - Data Integrity Failures | Validation stricte des entrées |
| A09 - Security Logging | Logs structurés, alertes |
| A10 - SSRF | Pas d'appels externes non contrôlés |

## Validation des entrées

Toutes les données sont validées via Pydantic :

```python
class ClientCreate(BaseModel):
    nom: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telephone: str = Field(..., pattern=r'^0[1-9][0-9]{8}$')
```

## CORS

Configuration restrictive des origines autorisées :

```python
ALLOWED_ORIGINS = ["https://payetonkawa.fr", "https://gestion.payetonkawa.fr"]
```

## Gestion des secrets

| Secret | Stockage |
|--------|----------|
| API_KEY | Variable d'environnement |
| DATABASE_URL | Variable d'environnement |
| RABBITMQ_URL | Variable d'environnement |

**Ne jamais commiter de secrets dans le code !**

## Recommandations production

1. Utiliser HTTPS uniquement
2. Activer le rate limiting
3. Rotation régulière des API Keys
4. Monitoring des accès suspects
5. Backup régulier des bases de données
```

---

## 🎫 TICKET #017 — Créer documentation hébergement/scaling

**Priorité :** 🔴 Critique  
**Estimation :** 30 min  
**Fichiers à créer :** `docs/HEBERGEMENT.md`

### Contenu attendu

```markdown
# Hébergement & Scaling PayeTonKawa

## Déploiement local (développement)

```bash
git clone https://github.com/Don-bot667/payetonkawa.git
cd payetonkawa
docker-compose up -d
```

## Déploiement production

### Option 1 : VPS (Recommandé pour démarrer)
- **Provider** : OVH, Scaleway, DigitalOcean
- **Config minimale** : 4 vCPU, 8 Go RAM, 50 Go SSD
- **Coût** : ~30-50€/mois

### Option 2 : Kubernetes (Scalabilité)
- **Provider** : AWS EKS, Google GKE, Azure AKS
- **Avantages** : Auto-scaling, haute disponibilité
- **Coût** : Variable selon usage

### Option 3 : PaaS (Simplicité)
- **Provider** : Heroku, Railway, Render
- **Avantages** : Déploiement simplifié
- **Coût** : ~50-100€/mois

## Scaling horizontal

Chaque API peut être répliquée indépendamment :

```yaml
# docker-compose.prod.yml
services:
  api-produits:
    deploy:
      replicas: 3  # 3 instances
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

### Load Balancing
Utiliser un reverse proxy (Nginx, Traefik) pour distribuer le trafic :

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    │     (Nginx)     │
                    └────────┬────────┘
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │ API Produits│   │ API Produits│   │ API Produits│
    │  Instance 1 │   │  Instance 2 │   │  Instance 3 │
    └─────────────┘   └─────────────┘   └─────────────┘
```

## Base de données

### Scaling vertical
Augmenter les ressources du serveur PostgreSQL.

### Scaling horizontal
- Read replicas pour les requêtes de lecture
- Connection pooling (PgBouncer)

## Monitoring production

- **Métriques** : Prometheus + Grafana
- **Logs** : ELK Stack ou Loki
- **Alertes** : AlertManager, PagerDuty
```

---

## 🎫 TICKET #018 — Compléter le README principal

**Priorité :** 🔴 Critique  
**Estimation :** 45 min  
**Fichiers à modifier :** `README.md`

### Structure complète

```markdown
# ☕ PayeTonKawa

> Application e-commerce de vente de café - Architecture Micro-services

![CI](https://github.com/Don-bot667/payetonkawa/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/Don-bot667/payetonkawa/branch/main/graph/badge.svg)](https://codecov.io/gh/Don-bot667/payetonkawa)

## 📋 Table des matières

- [Présentation](#-présentation)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [API Documentation](#-api-documentation)
- [Tests](#-tests)
- [Déploiement](#-déploiement)
- [Documentation](#-documentation)

## 🎯 Présentation

PayeTonKawa est une application e-commerce spécialisée dans la vente de café, construite avec une architecture micro-services moderne.

### Fonctionnalités
- 🧑‍💼 Gestion des clients
- ☕ Catalogue de produits avec gestion des stocks
- 📦 Gestion des commandes
- 🔄 Synchronisation temps réel via RabbitMQ
- 🔐 API sécurisée par API Key

## 🏗️ Architecture

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ API Clients │  │API Produits │  │API Commandes│
│    :8000    │  │    :8001    │  │    :8002    │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
                 ┌──────▼──────┐
                 │  RabbitMQ   │
                 │  :5672      │
                 └─────────────┘
```

| Service | Port | Description |
|---------|------|-------------|
| api-clients | 8000 | Gestion des clients |
| api-produits | 8001 | Catalogue produits |
| api-commandes | 8002 | Gestion commandes |
| RabbitMQ | 5672 / 15672 | Message broker |

## 🚀 Installation

### Prérequis
- Docker & Docker Compose
- Git

### Lancement rapide

```bash
# Cloner le projet
git clone https://github.com/Don-bot667/payetonkawa.git
cd payetonkawa

# Lancer tous les services
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

### URLs locales
| Service | URL |
|---------|-----|
| API Clients | http://localhost:8000/docs |
| API Produits | http://localhost:8001/docs |
| API Commandes | http://localhost:8002/docs |
| RabbitMQ Management | http://localhost:15672 |

## 📖 API Documentation

Chaque API expose une documentation Swagger interactive sur `/docs`.

### Authentification

Ajouter le header `X-API-Key` à chaque requête :

```bash
curl -H "X-API-Key: secret_key_123" http://localhost:8000/customers/
```

### Exemples

```bash
# Créer un client
curl -X POST http://localhost:8000/customers/ \
  -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{"nom": "Jean Dupont", "email": "jean@example.com", "adresse": "Paris", "telephone": "0612345678"}'

# Lister les produits
curl -H "X-API-Key: secret_key_123" http://localhost:8001/products/
```

## 🧪 Tests

```bash
# Installer les dépendances de test
pip install pytest pytest-cov

# Lancer tous les tests
pytest

# Avec couverture
pytest --cov=api-clients/app --cov=api-produits/app --cov=api-commandes/app

# Tests d'une seule API
cd api-clients && pytest
```

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Sécurité](docs/SECURITE.md)
- [Hébergement & Scaling](docs/HEBERGEMENT.md)
- [GitFlow](docs/GITFLOW.md)
- [Conduite du changement](docs/CONDUITE_CHANGEMENT.md)

## 👨‍💻 Auteur

**Don** - 2026

---

*Projet réalisé dans le cadre du MSPR TPRE814 - EISI*
```

---

## 🎫 TICKET #019 — Créer documentation API (endpoints)

**Priorité :** 🟡 Important  
**Estimation :** 30 min  
**Fichiers à créer :** `docs/API.md`

### Contenu : documenter tous les endpoints de chaque API avec exemples

---

# PHASE 6 — POSTMAN
> **Obligatoire** : collection de tests manuels

---

## 🎫 TICKET #020 — Créer collection Postman complète

**Priorité :** 🔴 Critique  
**Estimation :** 45 min  
**Fichiers à créer :**
- `postman/PayeTonKawa.postman_collection.json`
- `postman/PayeTonKawa_local.postman_environment.json`

### Structure de la collection

```
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
│   ├── PUT Modifier statut
│   └── DELETE Supprimer une commande
└── 📁 Health
    ├── GET Health API Clients
    ├── GET Health API Produits
    └── GET Health API Commandes
```

### Variables d'environnement

```json
{
  "id": "payetonkawa-local",
  "name": "PayeTonKawa - Local",
  "values": [
    {"key": "base_url_clients", "value": "http://localhost:8000"},
    {"key": "base_url_produits", "value": "http://localhost:8001"},
    {"key": "base_url_commandes", "value": "http://localhost:8002"},
    {"key": "api_key", "value": "secret_key_123"}
  ]
}
```

### Critères d'acceptation
- [ ] Toutes les routes documentées
- [ ] Variables d'environnement utilisées
- [ ] Exemples de body pour POST/PUT
- [ ] Tests automatiques dans Postman (status code)

---

# PHASE 7 — CONDUITE DU CHANGEMENT
> **Obligatoire** : accompagnement de la transition

---

## 🎫 TICKET #021 — Rédiger plan de conduite du changement

**Priorité :** 🔴 Critique  
**Estimation :** 1h30  
**Fichiers à créer :** `docs/CONDUITE_CHANGEMENT.md`

### Contenu attendu

```markdown
# Plan de Conduite du Changement

## Contexte

PayeTonKawa passe d'une architecture monolithique à une architecture micro-services, et d'un cycle en V à une méthodologie Agile.

## Changements identifiés

### 1. Changements techniques
| Avant | Après |
|-------|-------|
| Application monolithique | 3 micro-services indépendants |
| Base de données unique | 1 BDD par service |
| Déploiement manuel | CI/CD automatisé |
| Communication synchrone | Communication asynchrone (RabbitMQ) |

### 2. Changements organisationnels
| Avant | Après |
|-------|-------|
| Cycle en V | Méthodologie Agile (Scrum) |
| 1 équipe de 3 personnes | 3 équipes dédiées (1 par service) |
| Sollicitation directe des devs | Backlog géré par Product Owner |
| Déploiements rares | Déploiements fréquents |

## Plan d'action - Les 4 axes

### 1. INFORMER 📢
| Action | Cible | Timing |
|--------|-------|--------|
| Présentation de la nouvelle architecture | Toute l'équipe | J-30 |
| Documentation technique | Développeurs | J-20 |
| FAQ changements | Tous | Continu |

### 2. COMMUNIQUER 💬
| Action | Cible | Fréquence |
|--------|-------|-----------|
| Réunion de lancement | Direction + Équipes | 1 fois |
| Stand-up daily | Équipes dev | Quotidien |
| Sprint review | Tous stakeholders | Bi-hebdo |
| Newsletter projet | Toute l'entreprise | Mensuel |

### 3. FORMER 📚
| Formation | Durée | Cible |
|-----------|-------|-------|
| Architecture micro-services | 1 jour | Développeurs |
| Docker & conteneurisation | 1 jour | Développeurs + Ops |
| RabbitMQ | 0.5 jour | Développeurs |
| Méthodologie Agile/Scrum | 1 jour | Toute l'équipe |
| CI/CD avec GitHub Actions | 0.5 jour | Développeurs |

### 4. FAIRE PARTICIPER 🤝
| Action | Participants |
|--------|--------------|
| Choix des technologies | Développeurs seniors |
| Définition des standards de code | Équipe dev |
| Tests utilisateurs | Équipe commerciale |
| Retours sprint review | Tous |

## Modèle de transition de Bridges

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  PHASE 1          PHASE 2              PHASE 3              │
│  Fin              Zone neutre          Nouveau départ       │
│                                                             │
│  ████████         ████████████         ████████████████     │
│                                                             │
│  Accepter         Adaptation           Engagement           │
│  le changement    Apprentissage        Innovation           │
│                                                             │
│  Semaine 1-2      Semaine 3-6          Semaine 7+           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Résistances anticipées et solutions

| Résistance | Solution |
|------------|----------|
| "Ça marchait bien avant" | Montrer les limites de l'ancien système |
| "C'est trop compliqué" | Formation + accompagnement |
| "On n'a pas le temps" | Démontrer les gains de productivité |
| "Qui va gérer tout ça ?" | Définir clairement les rôles |

## Planning de transition

```
Mois 1: Préparation
├── Semaine 1-2: Formation architecture
├── Semaine 3-4: Formation Agile

Mois 2: Mise en place
├── Semaine 1-2: Déploiement environnement
├── Semaine 3-4: Premier sprint

Mois 3: Optimisation
├── Rétrospectives
├── Ajustements process
└── Autonomie des équipes
```

## KPIs de succès

| Indicateur | Objectif |
|------------|----------|
| Satisfaction équipe | > 7/10 |
| Temps de déploiement | < 30 min |
| Fréquence de déploiement | > 1/semaine |
| Couverture de tests | > 90% |
| Bugs en production | < 2/mois |

## Outils recommandés

- **Gestion de projet** : Jira, Trello
- **Communication** : Slack, Teams
- **Documentation** : Confluence, Notion
- **CI/CD** : GitHub Actions
- **Monitoring** : Grafana
```

### Critères d'acceptation
- [ ] 4 axes couverts (Informer, Communiquer, Former, Participer)

