J'ai analysé ton projet. Très bon travail ! 🎉

---

## ✅ Ce qui est FAIT

| API | Routes | Status |
|-----|--------|--------|
| **api-clients** | POST, GET, GET/:id, DELETE | ✅ Complet (manque juste PUT) |
| **api-produits** | POST, GET, GET/:id, PUT, DELETE | ✅ Complet |
| **api-commandes** | POST, GET, GET/:id, GET/client/:id, PUT, DELETE + lignes | ✅ Complet |

**Stack** : FastAPI + SQLAlchemy + PostgreSQL + Docker Compose 👍

---

## 📋 Ce qui RESTE à faire

Selon ton plan et ta demande :

| Étape | Quoi | Priorité |
|-------|------|----------|
| 1 | **Tests unitaires** | Moyenne |
| 2 | **RabbitMQ** (communication entre APIs) | Moyenne |
| 3 | **Sécurité** (API Key) | Haute |
| 4 | **CI/CD** (GitHub Actions) | Moyenne |
| 5 | **Frontend** | **HAUTE** (tu le demandes) |
| 6 | **Documentation** | Basse |

---

# 🚀 GUIDE ÉTAPE PAR ÉTAPE — FRONTEND + TESTS FINAUX

## ÉTAPE 1 : Vérifier que les APIs marchent

Avant le frontend, on s'assure que tout fonctionne.

```bash
# 1. Lance tout avec Docker
cd payetonkawa
docker-compose up -d

# 2. Attends 30 secondes puis teste
curl http://localhost:8000/          # API Clients
curl http://localhost:8001/          # API Produits  
curl http://localhost:8002/          # API Commandes
```

**Si ça marche** → Tu vois les messages "Bienvenue sur l'API..."

---

## ÉTAPE 2 : Créer le dossier Frontend

```bash
# Dans payetonkawa/
mkdir frontend
cd frontend
```

**Stack recommandée** : HTML/CSS/JavaScript vanilla (simple) ou React (plus pro)

Je te recommande **vanilla JS** pour rester simple.

---

## ÉTAPE 3 : Structure du Frontend

```
frontend/
├── index.html          ← Page principale (dashboard)
├── clients.html        ← Gestion des clients
├── produits.html       ← Gestion des produits
├── commandes.html      ← Gestion des commandes
├── css/
│   └── style.css       ← Styles
├── js/
│   ├── api.js          ← Fonctions pour appeler les APIs
│   ├── clients.js      ← Logique page clients
│   ├── produits.js     ← Logique page produits
│   └── commandes.js    ← Logique page commandes
└── Dockerfile          ← Pour servir le frontend
```

---

## ÉTAPE 4 : Créer les fichiers (je te donne le code)

### 4.1 — `frontend/index.html` (Dashboard)

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PayeTonKawa - Dashboard</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <h1>☕ PayeTonKawa</h1>
        <ul>
            <li><a href="index.html">Dashboard</a></li>
            <li><a href="clients.html">Clients</a></li>
            <li><a href="produits.html">Produits</a></li>
            <li><a href="commandes.html">Commandes</a></li>
        </ul>
    </nav>
    
    <main>
        <h2>Tableau de bord</h2>
        <div class="stats">
            <div class="stat-card">
                <h3>Clients</h3>
                <p id="clients-count">-</p>
            </div>
            <div class="stat-card">
                <h3>Produits</h3>
                <p id="produits-count">-</p>
            </div>
            <div class="stat-card">
                <h3>Commandes</h3>
                <p id="commandes-count">-</p>
            </div>
        </div>
    </main>

    <script src="js/api.js"></script>
    <script>
        // Charge les stats au démarrage
        async function loadStats() {
            const clients = await api.clients.getAll();
            const produits = await api.produits.getAll();
            const commandes = await api.commandes.getAll();
            
            document.getElementById('clients-count').textContent = clients.length;
            document.getElementById('produits-count').textContent = produits.length;
            document.getElementById('commandes-count').textContent = commandes.length;
        }
        loadStats();
    </script>
</body>
</html>
```

---

### 4.2 — `frontend/js/api.js` (Connexion aux APIs)

```javascript
// Configuration des URLs des APIs
const API_BASE = {
    clients: 'http://localhost:8000',
    produits: 'http://localhost:8001',
    commandes: 'http://localhost:8002'
};

// Objet API avec toutes les fonctions
const api = {
    // ===== CLIENTS =====
    clients: {
        getAll: async () => {
            const res = await fetch(`${API_BASE.clients}/customers`);
            return res.json();
        },
        getOne: async (id) => {
            const res = await fetch(`${API_BASE.clients}/customers/${id}`);
            return res.json();
        },
        create: async (data) => {
            const res = await fetch(`${API_BASE.clients}/customers`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return res.json();
        },
        delete: async (id) => {
            await fetch(`${API_BASE.clients}/customers/${id}`, { method: 'DELETE' });
        }
    },

    // ===== PRODUITS =====
    produits: {
        getAll: async () => {
            const res = await fetch(`${API_BASE.produits}/products`);
            return res.json();
        },
        getOne: async (id) => {
            const res = await fetch(`${API_BASE.produits}/products/${id}`);
            return res.json();
        },
        create: async (data) => {
            const res = await fetch(`${API_BASE.produits}/products`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return res.json();
        },
        update: async (id, data) => {
            const res = await fetch(`${API_BASE.produits}/products/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return res.json();
        },
        delete: async (id) => {
            await fetch(`${API_BASE.produits}/products/${id}`, { method: 'DELETE' });
        }
    },

    // ===== COMMANDES =====
    commandes: {
        getAll: async () => {
            const res = await fetch(`${API_BASE.commandes}/orders`);
            return res.json();
        },
        getOne: async (id) => {
            const res = await fetch(`${API_BASE.commandes}/orders/${id}`);
            return res.json();
        },
        getByClient: async (clientId) => {
            const res = await fetch(`${API_BASE.commandes}/orders/client/${clientId}`);
            return res.json();
        },
        create: async (data) => {
            const res = await fetch(`${API_BASE.commandes}/orders`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return res.json();
        },
        update: async (id, data) => {
            const res = await fetch(`${API_BASE.commandes}/orders/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return res.json();
        },
        delete: async (id) => {
            await fetch(`${API_BASE.commandes}/orders/${id}`, { method: 'DELETE' });
        }
    }
};
```

---

### 4.3 — `frontend/clients.html` (Page Clients)

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PayeTonKawa - Clients</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav>
        <h1>☕ PayeTonKawa</h1>
        <ul>
            <li><a href="index.html">Dashboard</a></li>
            <li><a href="clients.html" class="active">Clients</a></li>
            <li><a href="produits.html">Produits</a></li>
            <li><a href="commandes.html">Commandes</a></li>
        </ul>
    </nav>

    <main>
        <h2>Gestion des Clients</h2>
        
        <!-- Formulaire ajout -->
        <div class="form-card">
            <h3>Ajouter un client</h3>
            <form id="client-form">
                <input type="text" id="nom" placeholder="Nom" required>
                <input type="text" id="prenom" placeholder="Prénom" required>
                <input type="email" id="email" placeholder="Email" required>
                <input type="tel" id="telephone" placeholder="Téléphone">
                <input type="text" id="adresse" placeholder="Adresse">
                <button type="submit">Ajouter</button>
            </form>
        </div>

        <!-- Liste des clients -->
        <div class="list-card">
            <h3>Liste des clients</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nom</th>
                        <th>Prénom</th>
                        <th>Email</th>
                        <th>Téléphone</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="clients-table">
                    <!-- Rempli par JS -->
                </tbody>
            </table>
        </div>
    </main>

    <script src="js/api.js"></script>
    <script src="js/clients.js"></script>
</body>
</html>
```

---

### 4.4 — `frontend/js/clients.js`

```javascript
// Charge et affiche les clients
async function loadClients() {
    const clients = await api.clients.getAll();
    const tbody = document.getElementById('clients-table');
    
    tbody.innerHTML = clients.map(c => `
        <tr>
            <td>${c.id}</td>
            <td>${c.nom}</td>
            <td>${c.prenom}</td>
            <td>${c.email}</td>
            <td>${c.telephone || '-'}</td>
            <td>
                <button onclick="deleteClient(${c.id})" class="btn-delete">🗑️</button>
            </td>
        </tr>
    `).join('');
}

// Ajoute un client
document.getElementById('client-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        nom: document.getElementById('nom').value,
        prenom: document.getElementById('prenom').value,
        email: document.getElementById('email').value,
        telephone: document.getElementById('telephone').value || null,
        adresse: document.getElementById('adresse').value || null
    };
    
    await api.clients.create(data);
    e.target.reset();
    loadClients();
});

// Supprime un client
async function deleteClient(id) {
    if (confirm('Supprimer ce client ?')) {
        await api.clients.delete(id);
        loadClients();
    }
}

// Charge au démarrage
loadClients();
```

---

### 4.5 — `frontend/css/style.css`

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', sans-serif;
    background: #f5f5f5;
    color: #333;
}

nav {
    background: #4a2c2a;
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

nav h1 { font-size: 1.5rem; }

nav ul {
    display: flex;
    list-style: none;
    gap: 1.5rem;
}

nav a {
    color: white;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
}

nav a:hover, nav a.active {
    background: rgba(255,255,255,0.2);
}

main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}

h2 { margin-bottom: 1.5rem; }

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card, .form-card, .list-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.stat-card h3 { color: #666; font-size: 0.9rem; }
.stat-card p { font-size: 2.5rem; font-weight: bold; color: #4a2c2a; }

.form-card { margin-bottom: 2rem; }
.form-card h3, .list-card h3 { margin-bottom: 1rem; }

form {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

input, button {
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1rem;
}

button {
    background: #4a2c2a;
    color: white;
    cursor: pointer;
    border: none;
}

button:hover { background: #6b3d3a; }

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #eee;
}

th { background: #f9f9f9; }

.btn-delete {
    background: #dc3545;
    padding: 0.4rem 0.6rem;
}
```

---

## ÉTAPE 5 : Activer CORS sur les APIs

**IMPORTANT !** Le frontend va appeler les APIs depuis le navigateur. Il faut activer CORS.

Dans chaque `main.py` des 3 APIs, ajoute :

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # AJOUTE CETTE LIGNE
from .database import engine, Base
from .routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PayeTonKawa - API Clients",
    version="1.0.0"
)

# AJOUTE CE BLOC
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod, mettre l'URL du frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Clients de PayeTonKawa"}
```

---

## ÉTAPE 6 : Lancer et tester

```bash
# 1. Rebuild les APIs avec CORS
docker-compose down
docker-compose up -d --build

# 2. Ouvrir le frontend
# Option A : Double-clique sur frontend/index.html
# Option B : Serveur local
cd frontend
python -m http.server 3000
# Puis ouvre http://localhost:3000
```

---

## ÉTAPE 7 : Répéter pour Produits et Commandes

Crée `produits.html` + `js/produits.js` et `commandes.html` + `js/commandes.js` sur le même modèle.

**Je peux te les générer si tu veux !** 👍

---

## ÉTAPE 8 : Tests finaux

Une fois tout en place :

| Test | Comment | Résultat attendu |
|------|---------|------------------|
| Dashboard | Ouvre `index.html` | Affiche le nombre de clients/produits/commandes |
| Créer client | Remplis le formulaire | Client apparaît dans la liste |
| Supprimer client | Clique 🗑️ | Client disparaît |
| Créer produit | Idem | Produit apparaît |
| Créer commande | Sélectionne client + produits | Commande apparaît |

---

## 📦 Résumé des fichiers à créer

```
frontend/
├── index.html         ✅ (code donné)
├── clients.html       ✅ (code donné)
├── produits.html      📝 (à créer, même structure)
├── commandes.html     📝 (à créer, même structure)
├── css/style.css      ✅ (code donné)
├── js/api.js          ✅ (code donné)
├── js/clients.js      ✅ (code donné)
├── js/produits.js     📝 (à créer)
└── js/commandes.js    📝 (à créer)
```

---

**Tu veux que je te génère les fichiers `produits.html`, `commandes.html` et leurs JS ?** Ou tu préfères les faire toi-même en suivant le modèle ?






















































Compris ! 👍

On fait **HTML + Tailwind CSS (via CDN)** + **JS minimal et bien commenté**.

Je te refais le guide simplifié :

---

# 🚀 GUIDE FRONTEND — Tailwind + JS Minimal

## ÉTAPE 1 : Créer la structure

```bash
cd payetonkawa
mkdir frontend
cd frontend
```

Structure finale :
```
frontend/
├── index.html          ← Dashboard
├── clients.html        ← Page clients
├── produits.html       ← Page produits
├── commandes.html      ← Page commandes
└── js/
    └── api.js          ← UN SEUL fichier JS (simple)
```

---

## ÉTAPE 2 : Activer CORS sur tes APIs (OBLIGATOIRE)

Modifie les 3 fichiers `main.py` :

**📁 `api-clients/app/main.py`** :
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PayeTonKawa - API Clients", version="1.0.0")

# Active CORS (permet au navigateur d'appeler l'API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Clients de PayeTonKawa"}
```

**Fais pareil pour `api-produits/app/main.py` et `api-commandes/app/main.py`**

---

## ÉTAPE 3 : Les fichiers (je te donne tout)

### 📁 `frontend/js/api.js`

```javascript
// ============================================
// CONFIGURATION - Les adresses de tes APIs
// ============================================
const URLS = {
    clients: 'http://localhost:8000/customers',
    produits: 'http://localhost:8001/products',
    commandes: 'http://localhost:8002/orders'
};

// ============================================
// FONCTIONS POUR APPELER LES APIs
// Copie-colle, pas besoin de comprendre tout
// ============================================

// Récupérer tous les éléments
async function getTous(url) {
    const reponse = await fetch(url);
    return await reponse.json();
}

// Récupérer un élément par ID
async function getUn(url, id) {
    const reponse = await fetch(url + '/' + id);
    return await reponse.json();
}

// Créer un élément
async function creer(url, donnees) {
    const reponse = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(donnees)
    });
    return await reponse.json();
}

// Modifier un élément
async function modifier(url, id, donnees) {
    const reponse = await fetch(url + '/' + id, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(donnees)
    });
    return await reponse.json();
}

// Supprimer un élément
async function supprimer(url, id) {
    await fetch(url + '/' + id, { method: 'DELETE' });
}
```

---

### 📁 `frontend/index.html` (Dashboard)

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PayeTonKawa - Dashboard</title>
    <!-- Tailwind CSS via CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">

    <!-- NAVIGATION -->
    <nav class="bg-amber-900 text-white p-4">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold">☕ PayeTonKawa</h1>
            <ul class="flex gap-6">
                <li><a href="index.html" class="hover:underline font-semibold">Dashboard</a></li>
                <li><a href="clients.html" class="hover:underline">Clients</a></li>
                <li><a href="produits.html" class="hover:underline">Produits</a></li>
                <li><a href="commandes.html" class="hover:underline">Commandes</a></li>
            </ul>
        </div>
    </nav>

    <!-- CONTENU -->
    <main class="max-w-6xl mx-auto p-6">
        <h2 class="text-3xl font-bold mb-6">Tableau de bord</h2>
        
        <!-- Cartes statistiques -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            <!-- Carte Clients -->
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-gray-500 text-sm uppercase">Clients</h3>
                <p id="nb-clients" class="text-4xl font-bold text-amber-900 mt-2">-</p>
            </div>
            
            <!-- Carte Produits -->
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-gray-500 text-sm uppercase">Produits</h3>
                <p id="nb-produits" class="text-4xl font-bold text-amber-900 mt-2">-</p>
            </div>
            
            <!-- Carte Commandes -->
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-gray-500 text-sm uppercase">Commandes</h3>
                <p id="nb-commandes" class="text-4xl font-bold text-amber-900 mt-2">-</p>
            </div>
            
        </div>
    </main>

    <!-- JAVASCRIPT -->
    <script src="js/api.js"></script>
    <script>
        // Au chargement de la page, on récupère les stats
        async function chargerStats() {
            try {
                const clients = await getTous(URLS.clients);
                const produits = await getTous(URLS.produits);
                const commandes = await getTous(URLS.commandes);
                
                document.getElementById('nb-clients').textContent = clients.length;
                document.getElementById('nb-produits').textContent = produits.length;
                document.getElementById('nb-commandes').textContent = commandes.length;
            } catch (erreur) {
                console.log('Erreur:', erreur);
                alert('Erreur de connexion aux APIs. Vérifie que Docker tourne.');
            }
        }
        
        // Lance au démarrage
        chargerStats();
    </script>
</body>
</html>
```

---

### 📁 `frontend/clients.html`

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PayeTonKawa - Clients</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">

    <!-- NAVIGATION -->
    <nav class="bg-amber-900 text-white p-4">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold">☕ PayeTonKawa</h1>
            <ul class="flex gap-6">
                <li><a href="index.html" class="hover:underline">Dashboard</a></li>
                <li><a href="clients.html" class="hover:underline font-semibold">Clients</a></li>
                <li><a href="produits.html" class="hover:underline">Produits</a></li>
                <li><a href="commandes.html" class="hover:underline">Commandes</a></li>
            </ul>
        </div>
    </nav>

    <!-- CONTENU -->
    <main class="max-w-6xl mx-auto p-6">
        <h2 class="text-3xl font-bold mb-6">Gestion des Clients</h2>
        
        <!-- FORMULAIRE AJOUT -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h3 class="text-xl font-semibold mb-4">➕ Ajouter un client</h3>
            <form id="formulaire" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <input type="text" id="nom" placeholder="Nom *" required
                    class="border rounded p-3 focus:outline-none focus:ring-2 focus:ring-amber-500">
                <input type="text" id="prenom" placeholder="Prénom *" required
                    class="border rounded p-3 focus:outline-none focus:ring-2 focus:ring-amber-500">
                <input type="email" id="email" placeholder="Email *" required
                    class="border rounded p-3 focus:outline-none focus:ring-2 focus:ring-amber-500">
                <input type="tel" id="telephone" placeholder="Téléphone"
                    class="border rounded p-3 focus:outline-none focus:ring-2 focus:ring-amber-500">
                <input type="text" id="adresse" placeholder="Adresse"
                    class="border rounded p-3 focus:outline-none focus:ring-2 focus:ring-amber-500">
                <button type="submit" 
                    class="bg-amber-900 text-white rounded p-3 hover:bg-amber-800 font-semibold">
                    Ajouter
                </button>
            </form>
        </div>
        
        <!-- LISTE DES CLIENTS -->
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-xl font-semibold mb-4">📋 Liste des clients</h3>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="p-3 text-left">ID</th>
                            <th class="p-3 text-left">Nom</th>
                            <th class="p-3 text-left">Prénom</th>
                            <th class="p-3 text-left">Email</th>
                            <th class="p-3 text-left">Téléphone</th>
                            <th class="p-3 text-left">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="tableau">
                        <!-- Rempli par JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>
    </main>

    <!-- JAVASCRIPT -->
    <script src="js/api.js"></script>
    <script>
        // ============================================
        // CHARGER ET AFFICHER LES CLIENTS
        // ============================================
        async function chargerClients() {
            const clients = await getTous(URLS.clients);
            const tableau = document.getElementById('tableau');
            
            // Vide le tableau
            tableau.innerHTML = '';
            
            // Pour chaque client, crée une ligne
            clients.forEach(client => {
                tableau.innerHTML += `
                    <tr class="border-b hover:bg-gray-50">
                        <td class="p-3">${client.id}</td>
                        <td class="p-3">${client.nom}</td>
                        <td class="p-3">${client.prenom}</td>
                        <td class="p-3">${client.email}</td>
                        <td class="p-3">${client.telephone || '-'}</td>
                        <td class="p-3">
                            <button onclick="supprimerClient(${client.id})" 
                                class="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">
                                🗑️ Supprimer
                            </button>
                        </td>
                    </tr>
                `;
            });
        }
        
        // ============================================
        // AJOUTER UN CLIENT (quand on soumet le formulaire)
        // ============================================
        document.getElementById('formulaire').addEventListener('submit', async function(e) {
            e.preventDefault(); // Empêche le rechargement de la page
            
            // Récupère les valeurs des champs
            const nouveauClient = {
                nom: document.getElementById('nom').value,
                prenom: document.getElementById('prenom').value,
                email: document.getElementById('email').value,
                telephone: document.getElementById('telephone').value || null,
                adresse: document.getElementById('adresse').value || null
            };
            
            // Envoie à l'API
            await creer(URLS.clients, nouveauClient);
            
            // Vide le formulaire
            this.reset();
            
            // Recharge la liste
            chargerClients();
        });
        
        // ============================================
        // SUPPRIMER UN CLIENT
        // ============================================
        async function supprimerClient(id) {
            if (confirm('Supprimer ce client ?')) {
                await supprimer(URLS.clients, id);
                chargerClients();
            }
        }
        
        // ============================================
        // AU DÉMARRAGE : charge les clients
        // ============================================
        chargerClients();
    </script>
</body>
</html>
```

---

### 📁 `frontend/produits.html`

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PayeTonKawa - Produits</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">

    <!-- NAVIGATION -->
    <nav class="bg-amber-900 text-white p-4">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold">☕ PayeTonKawa</h1>
            <ul class="flex gap-6">
                <li><a href="index.html" class="hover:underline">Dashboard</a></li>
                <li><a href="clients.html" class="hover:underline">Clients</a></li>
                <li><a href="produits.html" class="hover:underline font-semibold">Produits</a></li>
                <li><a href="commandes.html" class="hover:underline">Commandes</a></li>
            </ul>
        </div>
    </nav>

    <!-- CONTENU -->
    <main class="max-w-6xl mx-auto p-6">
        <h2 class="text-3xl font-bold mb-6">Gestion des Produits</h2>
        
        <!-- FORMULAIRE AJOUT -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h3 class="text-xl font-semibold mb-4">➕ Ajouter un produit</h3>
            <form id="formulaire" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <input type="text" id="nom" placeholder="Nom du café *" required
                    class="border rounded p-3 focus:outline-none focus:ring-2 focus:ring-amber-500">
                <input type="text" id="description" placeholder="Description"
                    class="border rounded p-3 focus:outline-none focus:ring-2 focus:ring-amber-500">
                <input type="number" id="prix" placeholder="Prix (€) *" step="0.01" required
                    class="border rounded p-3 focus:outline-none focus:ring-2 focus:ring-amber-500">
                <input type="number" id="stock" placeholder="Stock *" required
                    class="border rounded p-3 focus:outline-none focus:ring-2 focus:ring-amber-500">
                <button type="submit" 
                    class="bg-amber-900 text-white rounded p-3 hover:bg-amber-800 font-semibold md:col-span-2 lg:col-span-4">
                    Ajouter
                </button>
            </form>
        </div>
        
        <!-- LISTE DES PRODUITS -->
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-xl font-semibold mb-4">☕ Liste des produits</h3>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="p-3 text-left">ID</th>
                            <th class="p-3 text-left">Nom</th>
                            <th class="p-3 text-left">Description</th>
                            <th class="p-3 text-left">Prix</th>
                            <th class="p-3 text-left">Stock</th>
                            <th class="p-3 text-left">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="tableau">
                        <!-- Rempli par JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>
    </main>

    <!-- JAVASCRIPT -->
    <script src="js/api.js"></script>
    <script>
        // ============================================
        // CHARGER ET AFFICHER LES PRODUITS
        // ============================================
        async function chargerProduits() {
            const produits = await getTous(URLS.produits);
            const tableau = document.getElementById('tableau');
            
            tableau.innerHTML = '';
            
            produits.forEach(produit => {
                tableau.innerHTML += `
                    <tr class="border-b hover:bg-gray-50">
                        <td class="p-3">${produit.id}</td>
                        <td class="p-3 font-semibold">${produit.nom}</td>
                        <td class="p-3">${produit.description || '-'}</td>
                        <td class="p-3">${produit.prix.toFixed(2)} €</td>
                        <td class="p-3">${produit.stock}</td>
                        <td class="p-3">
                            <button onclick="supprimerProduit(${produit.id})" 
                                class="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">
                                🗑️
                            </button>
                        </td>
                    </tr>
                `;
            });
        }
        
        // ============================================
        // AJOUTER UN PRODUIT
        // ============================================
        document.getElementById('formulaire').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const nouveauProduit = {
                nom: document.getElementById('nom').value,
                description: document.getElementById('description').value || null,
                prix: parseFloat(document.getElementById('prix').value),
                stock: parseInt(document.getElementById('stock').value)
            };
            
            await creer(URLS.produits, nouveauProduit);
            this.reset();
            chargerProduits();
        });
        
        // ============================================
        // SUPPRIMER UN PRODUIT
        // ============================================
        async function supprimerProduit(id) {
            if (confirm('Supprimer ce produit ?')) {
                await supprimer(URLS.produits, id);
                chargerProduits();
            }
        }
        
        // Au démarrage
        chargerProduits();
    </script>
</body>
</html>
```

---

### 📁 `frontend/commandes.html`

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PayeTonKawa - Commandes</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">

    <!-- NAVIGATION -->
    <nav class="bg-amber-900 text-white p-4">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold">☕ PayeTonKawa</h1>
            <ul class="flex gap-6">
                <li><a href="index.html" class="hover:underline">Dashboard</a></li>
                <li><a href="clients.html" class="hover:underline">Clients</a></li>
                <li><a href="produits.html" class="hover:underline">Produits</a></li>
                <li><a href="commandes.html" class="hover:underline font-semibold">Commandes</a></li>
            </ul>
        </div>
    </nav>

    <!-- CONTENU -->
    <main class="max-w-6xl mx-auto p-6">
        <h2 class="text-3xl font-bold mb-6">Gestion des Commandes</h2>
        
        <!-- FORMULAIRE NOUVELLE COMMANDE -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h3 class="text-xl font-semibold mb-4">➕ Nouvelle commande</h3>
            <form id="formulaire" class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <select id="client_id" required
                    class="border rounded p-3 focus:outline-none focus:ring-2 focus:ring-amber-500">
                    <option value="">-- Choisir un client --</option>
                </select>
                <select id="produit_id" required
                    class="border rounded p-3 focus:outline-none focus:ring-2 focus:ring-amber-500">
                    <option value="">-- Choisir un produit --</option>
                </select>
                <input type="number" id="quantite" placeholder="Quantité *" min="1" value="1" required
                    class="border rounded p-3 focus:outline-none focus:ring-2 focus:ring-amber-500">
                <button type="submit" 
                    class="bg-amber-900 text-white rounded p-3 hover:bg-amber-800 font-semibold md:col-span-3">
                    Créer la commande
                </button>
            </form>
        </div>
        
        <!-- LISTE DES COMMANDES -->
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-xl font-semibold mb-4">📦 Liste des commandes</h3>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="p-3 text-left">ID</th>
                            <th class="p-3 text-left">Client ID</th>
                            <th class="p-3 text-left">Statut</th>
                            <th class="p-3 text-left">Total</th>
                            <th class="p-3 text-left">Date</th>
                            <th class="p-3 text-left">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="tableau">
                        <!-- Rempli par JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>
    </main>

    <!-- JAVASCRIPT -->
    <script src="js/api.js"></script>
    <script>
        // Variable pour stocker les produits (pour calculer le prix)
        let produits = [];
        
        // ============================================
        // CHARGER LES LISTES DÉROULANTES
        // ============================================
        async function chargerSelecteurs() {
            // Charger les clients
            const clients = await getTous(URLS.clients);
            const selectClient = document.getElementById('client_id');
            clients.forEach(c => {
                selectClient.innerHTML += `<option value="${c.id}">${c.nom} ${c.prenom}</option>`;
            });
            
            // Charger les produits
            produits = await getTous(URLS.produits);
            const selectProduit = document.getElementById('produit_id');
            produits.forEach(p => {
                selectProduit.innerHTML += `<option value="${p.id}">${p.nom} - ${p.prix.toFixed(2)}€</option>`;
            });
        }
        
        // ============================================
        // CHARGER LES COMMANDES
        // ============================================
        async function chargerCommandes() {
            const commandes = await getTous(URLS.commandes);
            const tableau = document.getElementById('tableau');
            
            tableau.innerHTML = '';
            
            commandes.forEach(cmd => {
                // Couleur selon statut
                let couleurStatut = 'bg-yellow-100 text-yellow-800';
                if (cmd.statut === 'livree') couleurStatut = 'bg-green-100 text-green-800';
                if (cmd.statut === 'annulee') couleurStatut = 'bg-red-100 text-red-800';
                
                tableau.innerHTML += `
                    <tr class="border-b hover:bg-gray-50">
                        <td class="p-3">${cmd.id}</td>
                        <td class="p-3">${cmd.client_id}</td>
                        <td class="p-3">
                            <span class="px-2 py-1 rounded text-sm ${couleurStatut}">${cmd.statut}</span>
                        </td>
                        <td class="p-3 font-semibold">${cmd.total.toFixed(2)} €</td>
                        <td class="p-3">${new Date(cmd.date_commande).toLocaleDateString('fr-FR')}</td>
                        <td class="p-3">
                            <button onclick="supprimerCommande(${cmd.id})" 
                                class="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">
                                🗑️
                            </button>
                        </td>
                    </tr>
                `;
            });
        }
        
        // ============================================
        // CRÉER UNE COMMANDE
        // ============================================
        document.getElementById('formulaire').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const clientId = parseInt(document.getElementById('client_id').value);
            const produitId = parseInt(document.getElementById('produit_id').value);
            const quantite = parseInt(document.getElementById('quantite').value);
            
            // Trouve le produit pour avoir le prix
            const produit = produits.find(p => p.id === produitId);
            const prixUnitaire = produit ? produit.prix : 0;
            
            const nouvelleCommande = {
                client_id: clientId,
                lignes: [{
                    produit_id: produitId,
                    quantite: quantite,
                    prix_unitaire: prixUnitaire
                }]
            };
            
            await creer(URLS.commandes, nouvelleCommande);
            this.reset();
            chargerCommandes();
        });
        
        // ============================================
        // SUPPRIMER UNE COMMANDE
        // ============================================
        async function supprimerCommande(id) {
            if (confirm('Supprimer cette commande ?')) {
                await supprimer(URLS.commandes, id);
                chargerCommandes();
            }
        }
        
        // Au démarrage
        chargerSelecteurs();
        chargerCommandes();
    </script>
</body>
</html>
```

---

## ÉTAPE 4 : Lancer et tester

```bash
# 1. Rebuild les APIs (avec CORS)
cd payetonkawa
docker-compose down
docker-compose up -d --build

# 2. Attends 30 secondes

# 3. Lance le frontend
cd frontend
python -m http.server 3000

# 4. Ouvre dans ton navigateur :
# http://localhost:3000
```

---

## 📋 RÉSUMÉ — Fichiers à créer

| Fichier | Fait ? |
|---------|--------|
| `frontend/js/api.js` | Copie le code ci-dessus |
| `frontend/index.html` | Copie le code ci-dessus |
| `frontend/clients.html` | Copie le code ci-dessus |
| `frontend/produits.html` | Copie le code ci-dessus |
| `frontend/commandes.html` | Copie le code ci-dessus |
| Modifier les 3 `main.py` (CORS) | Ajoute le middleware |

---

## 🧪 TESTS FINAUX

| Test | Quoi faire | Résultat attendu |
|------|------------|------------------|
| 1 | Ouvre `http://localhost:3000` | Dashboard avec 0/0/0 |
| 2 | Va sur Clients → Ajoute "Jean Dupont" | Apparaît dans la liste |
| 3 | Va sur Produits → Ajoute "Arabica" 8.50€ | Apparaît dans la liste |
| 4 | Va sur Commandes → Crée une commande | Apparaît avec le total |
| 5 | Retourne au Dashboard | Les compteurs sont à jour |

---

C'est bon ? Tu veux que je t'aide à créer les fichiers directement ou tu préfères copier-coller toi-même ?