# Sécurité — Ce qui a été ajouté et pourquoi

---

## Sommaire

1. [Vue d'ensemble — Pourquoi sécuriser ?](#1-vue-densemble--pourquoi-sécuriser-)
2. [Ticket #015 — Le fichier auth.py](#2-ticket-015--le-fichier-authpy)
3. [Ticket #016 — Protéger les routes](#3-ticket-016--protéger-les-routes)
4. [Ticket #017 — Valider les données reçues](#4-ticket-017--valider-les-données-reçues)
5. [Ticket #018 — Restreindre le CORS](#5-ticket-018--restreindre-le-cors)
6. [Mise à jour des tests](#6-mise-à-jour-des-tests)
7. [Comment tester la sécurité manuellement](#7-comment-tester-la-sécurité-manuellement)
8. [Résumé visuel](#8-résumé-visuel)

---

## 1. Vue d'ensemble — Pourquoi sécuriser ?

Avant la phase sécurité, les APIs étaient complètement ouvertes :
- N'importe qui pouvait créer, modifier ou supprimer des clients, produits et commandes
- N'importe quel site web pouvait appeler les APIs (pas de restriction d'origine)
- N'importe quelle donnée pouvait être envoyée, même aberrante (prix négatif, téléphone invalide...)

On a ajouté **3 couches de protection** :

```
Requête entrante
      |
      v
[1] CORS ──────── Le site appelant est-il autorisé ?  → Non → Bloqué
      |
      v
[2] API Key ────── La clé est-elle présente et valide ? → Non → 401/403
      |
      v
[3] Validation ─── Les données sont-elles correctes ?  → Non → 422
      |
      v
   Traitement normal (CRUD, BDD...)
```

---

## 2. Ticket #015 — Le fichier `auth.py`

### Fichiers créés
- `api-clients/app/auth.py`
- `api-produits/app/auth.py`
- `api-commandes/app/auth.py`

Les 3 fichiers sont identiques. Voici le code avec des explications :

```python
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
import os

# On lit la clé API depuis les variables d'environnement
# Si elle n'est pas définie, on utilise "dev-key-change-in-prod" par défaut
API_KEY = os.getenv("API_KEY", "dev-key-change-in-prod")

# Le nom du header HTTP dans lequel on attend la clé
API_KEY_NAME = "X-API-Key"

# On dit à FastAPI : "cherche un header nommé X-API-Key dans chaque requête"
# auto_error=False signifie : ne génère pas d'erreur automatique,
# on gère nous-mêmes l'erreur ci-dessous
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Vérifie que le header X-API-Key est présent et valide."""

    # Cas 1 : le header X-API-Key n'est pas du tout envoyé
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # Code 401
            detail="API Key manquante"
        )

    # Cas 2 : le header est présent mais la valeur est mauvaise
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,  # Code 403
            detail="API Key invalide"
        )

    # Cas 3 : tout est bon, on retourne la clé (FastAPI en a besoin)
    return api_key
```

### Ce que ça fait concrètement

Quand quelqu'un appelle l'API, il doit maintenant envoyer un header supplémentaire :

```
GET /customers/
X-API-Key: dev-key-change-in-prod
```

Sans ce header → réponse **401 Unauthorized**
Avec un mauvais header → réponse **403 Forbidden**
Avec le bon header → la requête continue normalement

### La différence entre 401 et 403

| Code | Signification | Analogie |
|------|--------------|----------|
| 401 Unauthorized | Tu n'as pas présenté de clé du tout | Rentrer dans un immeuble sans badge |
| 403 Forbidden | Tu as une clé mais elle n'ouvre pas cette porte | Badge refusé à l'entrée |

### Où est stockée la vraie clé ?

Dans les variables d'environnement. Selon l'endroit :

**En local (fichier .env) :**
```
API_KEY=secret_key_123
```

**Dans Docker Compose :**
```yaml
api-clients:
  environment:
    API_KEY: secret_key_123
```

**En production :** la clé est définie sur le serveur, jamais dans le code.

---

## 3. Ticket #016 — Protéger les routes

### Fichiers modifiés
- `api-clients/app/routes.py`
- `api-produits/app/routes.py`
- `api-commandes/app/routes.py`

### Avant

```python
router = APIRouter(prefix="/customers", tags=["Customers"])
```

### Après

```python
from .auth import verify_api_key

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[Depends(verify_api_key)]  # ← ligne ajoutée
)
```

### Pourquoi une seule ligne suffit ?

En ajoutant `dependencies=[Depends(verify_api_key)]` directement sur le **router** (et non sur chaque route individuelle), FastAPI applique automatiquement la vérification à **toutes** les routes de ce router.

Ça évite de répéter le code sur chaque route :

```python
# Ce qu'on N'a PAS besoin de faire (trop répétitif) :
@router.get("/", dependencies=[Depends(verify_api_key)])
def read_customers(): ...

@router.post("/", dependencies=[Depends(verify_api_key)])
def create_customer(): ...

@router.delete("/{id}", dependencies=[Depends(verify_api_key)])
def delete_customer(): ...

# Ce qu'on fait à la place (une seule fois sur le router) :
router = APIRouter(dependencies=[Depends(verify_api_key)])
```

### Quelle route n'est PAS protégée ?

La route `/` (racine) est définie dans `main.py`, pas dans `routes.py`. Elle reste accessible sans clé :

```python
@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Clients de PayeTonKawa"}
```

La page `/docs` (Swagger) est aussi toujours accessible — indispensable pour tester et documenter l'API.

---

## 4. Ticket #017 — Valider les données reçues

### Fichiers modifiés
- `api-clients/app/schemas.py`
- `api-produits/app/schemas.py`
- `api-commandes/app/schemas.py`

### C'est quoi la validation ?

Avant, on pouvait envoyer n'importe quoi :
- Un client avec un nom d'un seul caractère : `"nom": "X"`
- Un produit avec un prix négatif : `"prix": -50`
- Une commande avec 0 lignes : `"lignes": []`
- Un téléphone invalide : `"telephone": "abc"`

Pydantic (la librairie utilisée par FastAPI) permet de définir des règles directement dans les schémas. Si les données ne respectent pas les règles → réponse **422 Unprocessable Entity** automatique, avec un message d'erreur clair.

### Ce qu'on utilise : `Field`

`Field` est une fonction Pydantic qui permet d'ajouter des contraintes à un champ :

```python
from pydantic import BaseModel, Field

class MonSchema(BaseModel):
    nom: str = Field(..., min_length=2, max_length=100)
    #            ^^^  ↑                 ↑
    #            |    longueur minimum  longueur maximum
    #            "..." signifie "champ obligatoire"
```

### API Clients — Ce qui a changé

**Avant :**
```python
class ClientCreate(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    telephone: Optional[str] = None
    adresse: Optional[str] = None
```

**Après :**
```python
class ClientCreate(BaseModel):
    nom: str = Field(..., min_length=2, max_length=100)
    prenom: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telephone: Optional[str] = Field(None, pattern=r'^0[1-9][0-9]{8}$')
    adresse: Optional[str] = Field(None, max_length=200)
```

**Explication des règles :**

| Champ | Règle | Pourquoi |
|-------|-------|----------|
| `nom` | min 2, max 100 caractères | Évite les noms d'1 lettre ou trop longs |
| `prenom` | min 2, max 100 caractères | Même raison |
| `email` | Format email valide | `EmailStr` vérifie déjà le format |
| `telephone` | Regex `^0[1-9][0-9]{8}$` | Format téléphone français uniquement |
| `adresse` | max 200 caractères | Évite les textes trop longs en BDD |

**Le regex téléphone décrypté :**
```
^           → début de la chaîne
0           → doit commencer par 0
[1-9]       → suivi d'un chiffre de 1 à 9 (pas 00)
[0-9]{8}    → suivi de 8 chiffres quelconques
$           → fin de la chaîne
```
Exemples valides : `0612345678`, `0123456789`
Exemples invalides : `061234567` (trop court), `abc`, `+33612345678`

### API Produits — Ce qui a changé

```python
class ProduitCreate(BaseModel):
    nom: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    prix: float = Field(..., gt=0)       # gt = "greater than" (strictement > 0)
    stock: int = Field(0, ge=0)          # ge = "greater or equal" (>= 0)
    origine: Optional[str] = Field(None, max_length=100)
    poids_kg: float = Field(1.0, gt=0)
```

**Explication des règles :**

| Champ | Règle | Pourquoi |
|-------|-------|----------|
| `prix` | `gt=0` (> 0) | Un prix ne peut pas être nul ou négatif |
| `stock` | `ge=0` (>= 0) | Le stock peut être à 0 (rupture) mais pas négatif |
| `poids_kg` | `gt=0` (> 0) | Un produit a toujours un poids positif |

**Différence entre `gt` et `ge` :**
- `gt=0` → strictement supérieur à 0 (0 interdit)
- `ge=0` → supérieur ou égal à 0 (0 autorisé)

### API Commandes — Ce qui a changé

```python
class LigneCommandeCreate(BaseModel):
    produit_id: int = Field(..., gt=0)        # ID toujours positif
    quantite: int = Field(1, ge=1)            # Au moins 1 article
    prix_unitaire: float = Field(..., gt=0)   # Prix positif

class CommandeCreate(BaseModel):
    client_id: int = Field(..., gt=0)
    lignes: List[LigneCommandeCreate] = Field(..., min_length=1)
    #                                               ↑
    #                              Au moins 1 ligne de commande requise
```

La règle `min_length=1` sur une liste est particulièrement importante : elle empêche de créer une commande vide (sans aucun produit).

---

## 5. Ticket #018 — Restreindre le CORS

### Fichiers modifiés
- `api-clients/app/main.py`
- `api-produits/app/main.py`
- `api-commandes/app/main.py`

### C'est quoi le CORS ?

CORS = Cross-Origin Resource Sharing (Partage de ressources entre origines différentes)

Quand un navigateur visite `http://monsite.com` et que ce site essaie d'appeler `http://localhost:8000`, le navigateur bloque la requête par défaut (protection de sécurité).

Pour autoriser cet appel, l'API doit déclarer les sites autorisés via le middleware CORS.

### Le problème avec `allow_origins=["*"]`

`"*"` veut dire "tout le monde est autorisé". C'est pratique en développement mais dangereux en production : n'importe quel site malveillant pourrait appeler l'API.

### Avant

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # ← Tout le monde autorisé (dangereux)
    allow_credentials=True,
    allow_methods=["*"],        # ← Toutes les méthodes HTTP autorisées
    allow_headers=["*"],
)
```

### Après

```python
import os

# On lit les origines autorisées depuis les variables d'environnement
# Par défaut : les 2 frontends locaux (port 3000 et 4321)
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:4321"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,                      # ← Liste précise
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],     # ← Méthodes limitées
    allow_headers=["*"],
)
```

### Pourquoi ces 2 ports par défaut ?

| Port | Usage |
|------|-------|
| 3000 | Ancien frontend (html/python http.server) |
| 4321 | Frontends Astro (sitepayetonkawa, gestionpayetonkawa) |

### Comment changer les origines autorisées ?

En production, via la variable d'environnement `ALLOWED_ORIGINS` :

```yaml
# Dans docker-compose.yml
api-clients:
  environment:
    ALLOWED_ORIGINS: "https://payetonkawa.fr,https://gestion.payetonkawa.fr"
```

### Pourquoi limiter les méthodes HTTP ?

`allow_methods=["GET", "POST", "PUT", "DELETE"]` au lieu de `["*"]` exclut des méthodes comme `PATCH`, `OPTIONS` (hors preflight), `TRACE`, `CONNECT` qui ne sont pas utilisées et pourraient être exploitées.

---

## 6. Mise à jour des tests

### Pourquoi les tests devaient être mis à jour ?

En ajoutant la protection par API Key, toutes les routes retournent maintenant 401 si la clé est absente. Les anciens tests n'envoyaient pas de clé → tous les tests auraient échoué.

### Ce qui a été modifié dans chaque `conftest.py`

**Ajout de la variable d'environnement :**
```python
os.environ.setdefault("API_KEY", "test-key")
```
Cette ligne définit une clé de test AVANT que `auth.py` soit importé.
`auth.py` lit `API_KEY` à l'import → il verra `"test-key"`.

**Ajout du header dans TestClient :**
```python
# Avant
with TestClient(app) as test_client:

# Après
with TestClient(app, headers={"X-API-Key": "test-key"}) as test_client:
```

Le paramètre `headers={"X-API-Key": "test-key"}` fait que **toutes les requêtes** émises par ce client de test auront automatiquement ce header. Plus besoin de l'ajouter manuellement dans chaque test.

---

## 7. Comment tester la sécurité manuellement

Une fois les conteneurs Docker lancés (`docker compose up -d`), tu peux tester avec `curl` dans le terminal.

### Test 1 — Appel sans clé (doit retourner 401)

```bash
curl http://localhost:8000/customers/
```

Réponse attendue :
```json
{"detail": "API Key manquante"}
```

### Test 2 — Appel avec une mauvaise clé (doit retourner 403)

```bash
curl http://localhost:8000/customers/ -H "X-API-Key: mauvaise-cle"
```

Réponse attendue :
```json
{"detail": "API Key invalide"}
```

### Test 3 — Appel avec la bonne clé (doit fonctionner)

```bash
curl http://localhost:8000/customers/ -H "X-API-Key: secret_key_123"
```

Réponse attendue :
```json
[]
```

### Test 4 — Données invalides (doit retourner 422)

```bash
curl -X POST http://localhost:8000/customers/ \
  -H "X-API-Key: secret_key_123" \
  -H "Content-Type: application/json" \
  -d '{"nom": "X", "prenom": "Don", "email": "don@gmail.com"}'
```

Réponse attendue (nom trop court) :
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "nom"],
      "msg": "String should have at least 2 characters"
    }
  ]
}
```

### Test 5 — Via Swagger (plus simple)

Ouvrir `http://localhost:8000/docs` dans le navigateur.

Cliquer sur le bouton **Authorize** (cadenas en haut à droite) → entrer la clé API → toutes les requêtes Swagger l'enverront automatiquement.

---

## 8. Résumé visuel

### Ce qui existait avant

```
Internet → [API] → Base de données
           Aucune protection
```

### Ce qui existe maintenant

```
Internet
    |
    v
[CORS] ──── Origine non autorisée ? ──── BLOQUÉ (navigateur)
    |
    v
[API Key] ── Clé absente ?    ──────────── 401 Unauthorized
           ── Clé incorrecte ? ──────────── 403 Forbidden
    |
    v
[Validation] ─ Données invalides ? ──────── 422 Unprocessable
    |
    v
[API] → [Base de données] → Réponse 200/201/204
```

### Tableau récapitulatif des fichiers

| Fichier | Ce qui a changé | Ticket |
|---------|----------------|--------|
| `app/auth.py` | Créé — vérification de l'API Key | #015 |
| `app/routes.py` | `dependencies=[Depends(verify_api_key)]` ajouté sur le router | #016 |
| `app/schemas.py` | `Field(...)` avec contraintes sur chaque champ | #017 |
| `app/main.py` | `ALLOWED_ORIGINS` remplace `["*"]`, méthodes HTTP limitées | #018 |
| `tests/conftest.py` | `API_KEY=test-key` + header dans TestClient | (mise à jour tests) |

### Variables d'environnement de sécurité

| Variable | Rôle | Valeur par défaut |
|----------|------|-------------------|
| `API_KEY` | Clé d'authentification | `dev-key-change-in-prod` |
| `ALLOWED_ORIGINS` | Sites autorisés à appeler l'API | `http://localhost:3000,http://localhost:4321` |
