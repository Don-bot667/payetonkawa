# Guide complet des tests — PayeTonKawa

---

## Sommaire

1. [C'est quoi un test ?](#1-cest-quoi-un-test)
2. [Les outils utilisés](#2-les-outils-utilisés)
3. [La structure des fichiers de test](#3-la-structure-des-fichiers-de-test)
4. [Le fichier conftest.py expliqué ligne par ligne](#4-le-fichier-conftestpy-expliqué-ligne-par-ligne)
5. [Le fichier test_routes.py expliqué](#5-le-fichier-test_routespy-expliqué)
6. [Le fichier pytest.ini expliqué](#6-le-fichier-pytestini-expliqué)
7. [Comment lancer les tests par API](#7-comment-lancer-les-tests-par-api)
8. [Comment lancer tous les tests d'un coup](#8-comment-lancer-tous-les-tests-dun-coup)
9. [Lire le rapport de couverture](#9-lire-le-rapport-de-couverture)
10. [Résumé des commandes](#10-résumé-des-commandes)

---

## 1. C'est quoi un test ?

Un test, c'est un petit programme qui vérifie que ton code fait bien ce qu'il est censé faire.

Exemple concret : tu as une route `POST /customers/` qui crée un client. Le test va :
1. Envoyer une requête fictive avec des données (nom, email, etc.)
2. Vérifier que la réponse est bien `201`
3. Vérifier que les données retournées sont correctes

Si quelqu'un modifie le code plus tard et casse quelque chose, le test échoue immédiatement — comme une alarme.

### Pourquoi on n'utilise pas la vraie base de données pour les tests ?

Parce que :
- La vraie BDD PostgreSQL doit tourner (Docker allumé)
- Les données de test pollueraient la vraie BDD
- Les tests seraient lents et dépendants de l'environnement

On utilise à la place **SQLite en mémoire** : une base de données ultra-légère qui s'installe en RAM, existe le temps d'un test, puis disparaît. Pas de Docker, pas de réseau, pas de données parasites.

---

## 2. Les outils utilisés

| Outil | Rôle | Installation |
|-------|------|-------------|
| **pytest** | Le lanceur de tests — il trouve et exécute les tests | Déjà dans `requirements.txt` |
| **pytest-cov** | Mesure la couverture de code (quelles lignes sont testées) | Déjà dans `requirements.txt` |
| **httpx** | Permet à `TestClient` de faire des requêtes HTTP fictives | Déjà dans `requirements.txt` |
| **SQLite** | Base de données légère en mémoire pour les tests | Intégré à Python (rien à installer) |
| **TestClient** | Simule un vrai navigateur/client HTTP sans serveur | Fourni par FastAPI |

### Où sont déclarées ces dépendances ?

Dans chaque fichier `requirements.txt` (api-clients, api-produits, api-commandes) :

```
pytest==7.4.4
pytest-cov==4.1.0
httpx==0.26.0
```

---

## 3. La structure des fichiers de test

Chaque API a exactement la même organisation :

```
api-clients/
├── app/                    <- Le code de l'API
│   ├── main.py
│   ├── routes.py
│   ├── crud.py
│   └── ...
└── tests/                  <- Les tests
    ├── __init__.py         <- Fichier vide (dit à Python "c'est un dossier")
    ├── conftest.py         <- Configuration des tests (fixtures)
    └── test_routes.py      <- Les tests eux-mêmes
```

Et à la racine du projet :
```
payetonkawa/
├── pytest.ini              <- Configuration globale de pytest
└── coverage_html/          <- Rapport de couverture HTML (généré automatiquement)
```

---

## 4. Le fichier conftest.py expliqué ligne par ligne

Le `conftest.py` est le fichier de **préparation des tests**. Il ne contient pas de tests, mais tout ce qui est nécessaire pour que les tests fonctionnent : la base de données de test, le client HTTP, les données d'exemple.

Voici une explication de chaque bloc (exemple avec api-clients) :

### Bloc 1 — Corriger le chemin Python

```python
import sys
import os

_API_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _API_DIR)
```

**Pourquoi ?**
Quand on lance pytest depuis la racine du projet, Python ne sait pas où trouver le dossier `app/` de chaque API. Ces lignes disent à Python : "cherche d'abord dans `api-clients/`".

`__file__` = chemin de conftest.py → `api-clients/tests/conftest.py`
`dirname()` une fois → `api-clients/tests/`
`dirname()` deux fois → `api-clients/` ← c'est ce qu'on veut ajouter

### Bloc 2 — Éviter les conflits entre les 3 APIs

```python
for _key in list(sys.modules.keys()):
    if _key == "app" or _key.startswith("app."):
        del sys.modules[_key]
```

**Pourquoi ?**
Les 3 APIs s'appellent toutes `app` en interne. Python garde les modules chargés en mémoire dans `sys.modules`. Sans ce nettoyage, quand pytest charge api-produits après api-clients, Python réutiliserait le module `app` d'api-clients (le mauvais). Ce nettoyage force Python à recharger le bon `app` pour chaque API.

### Bloc 3 — Simuler la variable d'environnement

```python
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
```

**Pourquoi ?**
Le fichier `database.py` lit `DATABASE_URL` dès son import. Si cette variable n'est pas définie, le programme plante. On lui donne une valeur SQLite qui ne sera pas utilisée en production mais évite le crash au chargement.

`setdefault` signifie : "définis cette valeur SEULEMENT si elle n'existe pas déjà". Donc si une vraie DATABASE_URL est déjà définie dans l'environnement, on ne l'écrase pas.

### Bloc 4 — Créer le moteur SQLite

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
```

**Pourquoi SQLite ?**
- `sqlite:///:memory:` = base de données en RAM, détruite à la fin du programme
- `check_same_thread=False` = SQLite n'est normalement utilisable que par un thread, ce paramètre lève cette restriction pour les tests
- `StaticPool` = tous les tests partagent la même connexion SQLite (sinon chaque connexion créerait une BDD séparée et les tables disparaîtraient)

### Bloc 5 — La fixture `db_session`

```python
@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)   # Crée les tables
    db = TestingSessionLocal()              # Ouvre une session
    try:
        yield db                            # Donne la session au test
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine) # Supprime les tables
```

**C'est quoi une fixture ?**
Une fixture est une fonction qui prépare quelque chose avant un test et nettoie après. Le mot-clé `yield` sépare le "avant" du "après".

`scope="function"` signifie : recréer les tables à chaque test. Ainsi chaque test repart d'une base vide et propre.

### Bloc 6 — La fixture `client`

```python
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

**Que se passe-t-il ici ?**

FastAPI utilise `get_db` pour ouvrir une session PostgreSQL à chaque requête. On "remplace" (`override`) cette fonction par `override_get_db` qui donne la session SQLite de test à la place.

`TestClient(app)` crée un faux navigateur qui peut faire des requêtes HTTP directement à l'API sans démarrer de vrai serveur.

Après le test, `app.dependency_overrides.clear()` supprime le remplacement pour ne pas affecter les autres tests.

### Bloc 7 — La fixture de données d'exemple

```python
@pytest.fixture
def sample_client():
    return {
        "nom": "Faouz",
        "prenom": "Don",
        "email": "don@gmail.com",
        "telephone": "0612345678",
        "adresse": "lyon , 69000"
    }
```

Un simple dictionnaire avec des données valides. Les tests qui en ont besoin le demandent en paramètre.

---

## 5. Le fichier test_routes.py expliqué

C'est ici que sont écrits les vrais tests. Ils sont organisés en classes, une par groupe de routes.

### Structure d'un test

```python
class TestCreateCustomer:

    def test_create_customer_success(self, client, sample_client):
        response = client.post("/customers/", json=sample_client)
        assert response.status_code == 201
        assert response.json()["nom"] == sample_client["nom"]
        assert "id" in response.json()
```

Décortiquons :

- `class TestCreateCustomer` → groupe tous les tests liés à la création d'un client
- `def test_create_customer_success` → le nom commence par `test_` (obligatoire pour que pytest le détecte)
- `self, client, sample_client` → `client` et `sample_client` sont des fixtures demandées en paramètre, pytest les fournit automatiquement
- `client.post(...)` → envoie une requête POST fictive à l'API
- `assert` → vérifie une condition. Si faux → le test échoue

### Ce qu'on teste dans chaque API

**API Clients** (20 tests) :
- Création : succès, email invalide, champs manquants, sans optionnels
- Lecture : liste vide, liste avec données, par ID, 404
- Modification : nom, email, plusieurs champs, 404, email invalide
- Suppression : succès, vérification 404 après, 404 direct

**API Produits** (21 tests) :
- Création : succès, champs manquants, sans optionnels, stock par défaut, prix invalide
- Lecture : liste vide, liste avec données, par ID, 404
- Modification : prix, stock, stock à 0, désactivation, plusieurs champs, 404
- Suppression : succès, vérification 404 après, 404 direct

**API Commandes** (26 tests) :
- Création : succès, calcul du total automatique, lignes incluses, ligne seule, champs manquants
- Lecture : liste vide, par ID avec lignes, par client, 404
- Modification : changement de statut, progression complète, 404
- Suppression : succès, cascade des lignes vérifié en BDD, 404

---

## 6. Le fichier pytest.ini expliqué

Ce fichier est à la racine du projet. Il configure le comportement global de pytest.

```ini
[pytest]
testpaths = api-clients/tests api-produits/tests api-commandes/tests
```
Dit à pytest où chercher les tests. Sans ça, il chercherait dans tout le projet.

```ini
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```
Dit à pytest comment reconnaître les fichiers, classes et fonctions de test.

```ini
addopts =
    --import-mode=importlib
```
Résout un problème technique : les 3 APIs ont toutes un dossier `app/` avec le même nom. Sans cette option, pytest confondrait les modules entre eux. `importlib` force un import par chemin complet, sans confusion.

```ini
    --cov=api-clients/app
    --cov=api-produits/app
    --cov=api-commandes/app
```
Demande à pytest-cov de mesurer la couverture du code des 3 APIs.

```ini
    --cov-report=term-missing
```
Affiche dans le terminal le tableau de couverture avec les numéros de lignes non testées.

```ini
    --cov-report=html:coverage_html
```
Génère un rapport HTML dans le dossier `coverage_html/` (rapport visuel et navigable).

---

## 7. Comment lancer les tests par API

Tu dois d'abord activer l'environnement virtuel :

```bash
source .venv/bin/activate
```

### Lancer les tests de api-clients uniquement

```bash
cd /home/david/dev/Mspr/payetonkawa/api-clients
python -m pytest tests/ -v
```

### Lancer les tests de api-produits uniquement

```bash
cd /home/david/dev/Mspr/payetonkawa/api-produits
python -m pytest tests/ -v
```

### Lancer les tests de api-commandes uniquement

```bash
cd /home/david/dev/Mspr/payetonkawa/api-commandes
python -m pytest tests/ -v
```

### Ce que signifie l'option `-v`

`-v` = verbose (bavard). Affiche le nom de chaque test avec PASSED ou FAILED au lieu d'un simple point.

Sans `-v` :
```
.....................   [100%]
```

Avec `-v` :
```
tests/test_routes.py::TestCreateCustomer::test_create_customer_success PASSED
tests/test_routes.py::TestCreateCustomer::test_create_customer_invalid_email PASSED
...
```

### Lancer un seul test précis

```bash
python -m pytest tests/test_routes.py::TestCreateCustomer::test_create_customer_success -v
```

### Lancer tous les tests d'une classe

```bash
python -m pytest tests/test_routes.py::TestCreateCustomer -v
```

---

## 8. Comment lancer tous les tests d'un coup

Depuis la racine du projet, une seule commande suffit :

```bash
cd /home/david/dev/Mspr/payetonkawa
source .venv/bin/activate
python -m pytest
```

pytest lit automatiquement `pytest.ini` et :
1. Cherche les tests dans les 3 dossiers définis
2. Lance les 67 tests
3. Affiche le rapport de couverture dans le terminal
4. Génère le rapport HTML dans `coverage_html/`

### Résultat attendu

```
collected 67 items

api-clients/tests/test_routes.py ....................   [ 29%]
api-produits/tests/test_routes.py .....................  [ 61%]
api-commandes/tests/test_routes.py ....................  [100%]

---------- coverage -----------
Name                         Stmts   Miss  Cover
-------------------------------------------------
api-clients/app/crud.py         29      0   100%
api-clients/app/routes.py       29      0   100%
...
TOTAL                          424     39    91%

67 passed in 0.93s
```

### Options utiles en mode global

```bash
# Voir le détail de chaque test (avec noms)
python -m pytest -v

# Arrêter au premier test qui échoue
python -m pytest -x

# Afficher les print() dans les tests (désactivés par défaut)
python -m pytest -s

# Combiner les options
python -m pytest -v -x
```

---

## 9. Lire le rapport de couverture

### Dans le terminal

Le rapport affiché ressemble à ceci :

```
Name                            Stmts   Miss  Cover   Missing
-------------------------------------------------------------
api-clients/app/crud.py            29      0   100%
api-clients/app/routes.py          29      0   100%
api-clients/app/config.py           9      9     0%   1-14
api-clients/app/database.py        15      4    73%   24-28
```

- **Stmts** = nombre total de lignes de code
- **Miss** = nombre de lignes jamais exécutées par les tests
- **Cover** = pourcentage de couverture
- **Missing** = numéros des lignes non testées

### Dans le navigateur (rapport HTML)

```bash
# Ouvrir le rapport HTML
xdg-open /home/david/dev/Mspr/payetonkawa/coverage_html/index.html
```

Tu verras chaque fichier avec ses lignes colorées :
- Vert = ligne testée
- Rouge = ligne non testée

### Pourquoi certains fichiers ont 0% ?

`config.py` a 0% de couverture car il est créé mais pas encore utilisé dans le code principal (sera câblé lors de l'implémentation de RabbitMQ et de la sécurité).

`database.py` a 73% car les lignes non couvertes (24-28) correspondent à la fermeture de session en production — ce chemin n'est pas emprunté dans les tests SQLite en mémoire.

### Objectif de couverture

L'objectif fixé dans le projet est **> 80%**. Actuellement : **91%** — objectif dépassé.

---

## 10. Résumé des commandes

```bash
# Aller à la racine du projet
cd /home/david/dev/Mspr/payetonkawa

# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer TOUS les tests (67 tests, 3 APIs)
python -m pytest

# Lancer TOUS les tests avec noms détaillés
python -m pytest -v

# Lancer les tests d'une seule API
python -m pytest api-clients/tests/ -v
python -m pytest api-produits/tests/ -v
python -m pytest api-commandes/tests/ -v

# Lancer un seul test
python -m pytest api-clients/tests/test_routes.py::TestCreateCustomer::test_create_customer_success -v

# Arrêter au premier échec
python -m pytest -x

# Ouvrir le rapport HTML de couverture
xdg-open coverage_html/index.html
```

---

## Schéma de fonctionnement résumé

```
pytest
  |
  |-- lit pytest.ini
  |     -> cherche dans api-clients/tests, api-produits/tests, api-commandes/tests
  |
  |-- charge conftest.py (pour chaque API)
  |     -> ajoute le bon dossier API dans sys.path
  |     -> crée un moteur SQLite en mémoire
  |     -> prépare les fixtures (db_session, client, sample_*)
  |
  |-- exécute chaque test_*.py
  |     -> Pour chaque test :
  |          1. db_session crée les tables (BDD vide)
  |          2. client remplace get_db par la session SQLite
  |          3. le test envoie des requêtes HTTP fictives
  |          4. assert vérifie les réponses
  |          5. db_session supprime les tables (nettoyage)
  |
  |-- mesure la couverture (pytest-cov)
  |     -> affiche le tableau dans le terminal
  |     -> génère coverage_html/
  |
  -> Résultat final : 67 passed / 0 failed
```
