# CLAUDE.MD - Memoire du projet PayeTonKawa

Fichier de contexte pour Claude Code. Resume le projet, ce qui a ete fait, et ou on en est.

---

## LE PROJET

**PayeTonKawa** est un projet MSPR (projet scolaire) de micro-services pour une entreprise fictive de vente de cafe.

- **Depot GitHub** : https://github.com/Don-bot667/payetonkawa
- **Chemin local** : `/home/david/dev/Mspr/payetonkawa`
- **Proprietaire** : David (david.djinadou@advercity.fr)

Le projet se compose de **3 APIs independantes** (micro-services) + un **frontend de gestion** :
- API Clients (gestion des clients)
- API Produits (gestion du catalogue de cafes)
- API Commandes (gestion des commandes, relie clients et produits)
- Frontend GestionPayeTonKawa (interface web de gestion)

---

## ARCHITECTURE TECHNIQUE

### Stack
- **Backend** : Python 3.12 + FastAPI + SQLAlchemy + PostgreSQL 15
- **Frontend** : HTML + Tailwind CSS (CDN) + JavaScript vanilla
- **Conteneurisation** : Docker + Docker Compose
- **Messagerie** : RabbitMQ (prevu, pas encore implemente)

### Credentials base de donnees
- **User** : `faouz`
- **Mot de passe** : `faouz2020`
- Utilise sur les 3 APIs (clients, produits, commandes)
- L'ancien user `postgres` a ete supprime et remplace partout

### Ports

| Service | Port BDD | Port API |
|---------|----------|----------|
| api-clients | 5436 | 8000 |
| api-produits | 5437 | 8001 |
| api-commandes | 5438 | 8002 |
| rabbitmq | 5672 / 15672 | - |
| frontend | - | 3000 (python3 -m http.server) |

### Endpoints des APIs

**API Clients (port 8000)** - prefix `/customers`
- POST /customers/ - Creer
- GET /customers/ - Lister
- GET /customers/{id} - Voir un client
- DELETE /customers/{id} - Supprimer

**API Produits (port 8001)** - prefix `/products`
- POST /products/ - Creer
- GET /products/ - Lister
- GET /products/{id} - Voir un produit
- PUT /products/{id} - Modifier
- DELETE /products/{id} - Supprimer

**API Commandes (port 8002)** - prefix `/orders`
- POST /orders/ - Creer (avec lignes de commande)
- GET /orders/ - Lister
- GET /orders/{id} - Voir une commande
- GET /orders/client/{client_id} - Commandes d'un client
- PUT /orders/{id} - Modifier le statut
- DELETE /orders/{id} - Supprimer

---

## STRUCTURE DES FICHIERS

```
payetonkawa/
├── docker-compose.yml              <- Docker Compose global (7 services)
├── claude.MD                       <- Ce fichier
├── BASES DE DONNEES.md             <- Schema des tables des 3 BDD
├── Plan Generale.md                <- Plan global du projet par phases
│
├── api-clients/                    <- API CLIENTS (FAIT)
│   ├── app/
│   │   ├── main.py                <- Point d'entree FastAPI
│   │   ├── database.py            <- Connexion PostgreSQL
│   │   ├── models.py              <- Table "clients"
│   │   ├── schemas.py             <- Schemas Pydantic (ClientCreate, ClientResponse)
│   │   ├── crud.py                <- CRUD (create, get, get_all, delete)
│   │   └── routes.py              <- Routes /customers
│   ├── .env                       <- DATABASE_URL locale (faouz:faouz2020@localhost:5436)
│   ├── docker-compose.yml         <- Docker autonome (api + db sur 5436/8000)
│   ├── Dockerfile                 <- Image Python 3.12 slim
│   ├── requirements.txt           <- Dependances Python
│   └── GUIDE.md                   <- Guide explicatif
│
├── api-produits/                   <- API PRODUITS (FAIT)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py              <- Table "produits" (10 colonnes)
│   │   ├── schemas.py             <- ProduitCreate, ProduitUpdate, ProduitResponse
│   │   ├── crud.py                <- CRUD (create, get, get_all, update, delete)
│   │   └── routes.py              <- Routes /products
│   ├── docker-compose.yml         <- Docker autonome (api + db sur 5437/8001)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── produits.MD                <- Guide explicatif
│
├── api-commandes/                  <- API COMMANDES (FAIT)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py              <- 2 tables : "commandes" + "lignes_commande" (ForeignKey + CASCADE)
│   │   ├── schemas.py             <- LigneCommandeCreate/Response, CommandeCreate/Update/Response
│   │   ├── crud.py                <- CRUD + get_by_client, calcul total auto
│   │   └── routes.py              <- Routes /orders + /orders/client/{id}
│   ├── docker-compose.yml         <- Docker autonome (api + db sur 5438/8002)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── commandes.MD               <- Guide explicatif
│
├── gestionpayetonkawa/            <- FRONTEND (GUIDE CREE, CODE PAS ENCORE ECRIT)
│   └── gestion.md                 <- Guide complet avec tout le code a creer
│   (Fichiers a creer : index.html, clients.html, produits.html, commandes.html,
│    css/style.css, js/api.js, js/dashboard.js, js/clients.js, js/produits.js, js/commandes.js)
│
├── frontend/                       <- Ancien dossier frontend (existait avant)
├── docs/                           <- Documentation (a faire)
├── postman/                        <- Collection Postman (a faire)
└── .github/                        <- GitHub Actions CI/CD (a faire)
```

---

## CE QUI A ETE FAIT

### Session du 12/02/2026

1. **Conteneurisation api-clients** : Dockerfile + docker-compose.yml autonome
2. **Changement superuser** : postgres -> faouz / faouz2020 dans tous les fichiers (api-clients .env, docker-compose)
3. **Guide api-produits** : Creation de `produits.MD` avec explication detaillee de chaque fichier
4. **Verification api-produits** : Les 9 fichiers crees par l'utilisateur sont corrects
5. **Guide api-commandes** : Creation de `commandes.MD` avec explication detaillee (2 tables, ForeignKey, CASCADE)
6. **Verification api-commandes** : Les 9 fichiers crees par l'utilisateur sont corrects
7. **Docker Compose global** : Mis a jour avec les 3 APIs + 3 BDD + RabbitMQ (7 services, user faouz)
8. **Fix volumes** : L'ancien volume db-clients gardait le user postgres, resolu avec `docker compose down -v`
9. **Verification** : 7/7 conteneurs UP, les 3 APIs repondent correctement
10. **Push GitHub** : Tout pousse sur https://github.com/Don-bot667/payetonkawa
11. **Guide frontend** : Creation de `gestion.md` avec le code complet de 10 fichiers (HTML/Tailwind/JS)

---

## CE QUI RESTE A FAIRE

### Prioritaire (prochaines etapes)
- [ ] **Frontend** : Creer les 10 fichiers decrits dans `gestionpayetonkawa/gestion.md`
- [ ] **CORS** : Ajouter `CORSMiddleware` dans les 3 `main.py` (obligatoire pour que le frontend fonctionne)
- [ ] **Securite** : Proteger les APIs avec une API Key (Phase 5 du plan)

### Secondaire
- [ ] **RabbitMQ** : Communication entre APIs (Phase 4 du plan)
- [ ] **CI/CD** : GitHub Actions pour tests automatiques (Phase 6)
- [ ] **Monitoring** : Logs et compteurs (Phase 7)
- [ ] **Documentation** : architecture.md, securite.md, ci-cd.md, conduite-changement.md (Phase 8)
- [ ] **Tests** : test_main.py + conftest.py dans chaque API
- [ ] **Collection Postman** : Exporter les requetes

---

## NOTES IMPORTANTES

- Les docker-compose individuels (dans chaque api) et le docker-compose global partagent les memes ports. Ne pas lancer les deux en meme temps.
- Pour repartir a zero sur les BDD : `docker compose down -v` (supprime les volumes)
- L'utilisateur prefere des explications simples et detaillees, en francais
- L'utilisateur ne maitrise pas trop JavaScript, il prefere HTML/CSS avec JS minimal
- Pas d'emojis dans le code sauf si demande
- Le token GitHub a ete expose dans une conversation precedente -> l'utilisateur doit le supprimer/regenerer
