# GestionPayeTonKawa - Guide complet du Frontend

---

## RESUME RAPIDE

Un site web de gestion pour PayeTonKawa. Il permet de gerer les clients, les produits et les commandes depuis le navigateur. Il appelle les 3 APIs qu'on a deja creees.

Technos : **HTML + Tailwind CSS + JavaScript vanilla** (pas de framework).

```
gestionpayetonkawa/
├── index.html            ← Dashboard (page d'accueil)
├── clients.html          ← Page de gestion des clients
├── produits.html         ← Page de gestion des produits
├── commandes.html        ← Page de gestion des commandes
├── css/
│   └── style.css         ← Styles personnalises (en plus de Tailwind)
├── js/
│   ├── api.js            ← Fonctions centrales pour appeler les 3 APIs
│   ├── dashboard.js      ← Logique du dashboard (charger les stats)
│   ├── clients.js        ← Logique CRUD clients
│   ├── produits.js       ← Logique CRUD produits
│   └── commandes.js      ← Logique CRUD commandes
└── gestion.md            ← Ce fichier (le guide)
```

---

## AVANT DE COMMENCER : ACTIVER LE CORS

Les APIs tournent sur les ports 8000, 8001, 8002. Le frontend tourne sur un autre port. Par defaut, le navigateur **bloque** les requetes entre ports differents (c'est une securite). Il faut activer le CORS (Cross-Origin Resource Sharing) dans chaque API.

Il faut modifier le fichier `main.py` de chaque API en ajoutant ces lignes :

```python
from fastapi.middleware.cors import CORSMiddleware

# Apres la ligne app = FastAPI(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Cela doit etre fait dans :
- `api-clients/app/main.py`
- `api-produits/app/main.py`
- `api-commandes/app/main.py`

---

## FICHIER PAR FICHIER

---

### 1. `css/style.css`

**C'est quoi ?** Les styles personnalises en plus de Tailwind. On y met ce que Tailwind ne couvre pas directement.

```css
/* Police de caracteres */
body {
    font-family: 'Inter', sans-serif;
}

/* Sidebar : lien actif */
.nav-link.active {
    background-color: rgba(255, 255, 255, 0.1);
    border-right: 3px solid #818cf8;
}

/* Transition douce sur les lignes du tableau */
tbody tr {
    transition: background-color 0.15s ease;
}

/* Animation d'apparition pour les modales */
.modal-backdrop {
    transition: opacity 0.2s ease;
}

/* Badge de statut des commandes */
.badge {
    padding: 2px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-en_attente { background-color: #fef3c7; color: #92400e; }
.badge-validee { background-color: #d1fae5; color: #065f46; }
.badge-en_preparation { background-color: #dbeafe; color: #1e40af; }
.badge-expediee { background-color: #e0e7ff; color: #3730a3; }
.badge-livree { background-color: #d1fae5; color: #065f46; }
.badge-annulee { background-color: #fee2e2; color: #991b1b; }
```

**Explication :**

| Style | A quoi ca sert |
|-------|---------------|
| `nav-link.active` | Met en surbrillance le lien de la page actuelle dans la sidebar |
| `tbody tr transition` | Animation douce quand on survole une ligne du tableau |
| `modal-backdrop` | Animation d'ouverture/fermeture des modales (pop-ups) |
| `.badge-*` | Couleurs differentes selon le statut de la commande |

---

### 2. `js/api.js`

**C'est quoi ?** Le fichier central qui contient toutes les fonctions pour appeler les 3 APIs. Tous les autres fichiers JS utilisent celui-ci.

```javascript
// Adresses des 3 APIs
const API_CLIENTS = "http://localhost:8000";
const API_PRODUITS = "http://localhost:8001";
const API_COMMANDES = "http://localhost:8002";

// --- CLIENTS ---

async function getClients() {
    const response = await fetch(API_CLIENTS + "/customers/");
    return await response.json();
}

async function getClient(id) {
    const response = await fetch(API_CLIENTS + "/customers/" + id);
    return await response.json();
}

async function createClient(data) {
    const response = await fetch(API_CLIENTS + "/customers/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return await response.json();
}

async function deleteClient(id) {
    await fetch(API_CLIENTS + "/customers/" + id, {
        method: "DELETE"
    });
}

// --- PRODUITS ---

async function getProduits() {
    const response = await fetch(API_PRODUITS + "/products/");
    return await response.json();
}

async function getProduit(id) {
    const response = await fetch(API_PRODUITS + "/products/" + id);
    return await response.json();
}

async function createProduit(data) {
    const response = await fetch(API_PRODUITS + "/products/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return await response.json();
}

async function updateProduit(id, data) {
    const response = await fetch(API_PRODUITS + "/products/" + id, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return await response.json();
}

async function deleteProduit(id) {
    await fetch(API_PRODUITS + "/products/" + id, {
        method: "DELETE"
    });
}

// --- COMMANDES ---

async function getCommandes() {
    const response = await fetch(API_COMMANDES + "/orders/");
    return await response.json();
}

async function getCommande(id) {
    const response = await fetch(API_COMMANDES + "/orders/" + id);
    return await response.json();
}

async function createCommande(data) {
    const response = await fetch(API_COMMANDES + "/orders/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return await response.json();
}

async function updateCommande(id, data) {
    const response = await fetch(API_COMMANDES + "/orders/" + id, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return await response.json();
}

async function deleteCommande(id) {
    await fetch(API_COMMANDES + "/orders/" + id, {
        method: "DELETE"
    });
}
```

**Explication des concepts :**

| Concept | Explication simple |
|---------|-------------------|
| `async / await` | Permet d'attendre la reponse de l'API avant de continuer |
| `fetch(url)` | Envoie une requete HTTP a l'API (comme Postman mais en code) |
| `response.json()` | Transforme la reponse en objet JavaScript utilisable |
| `JSON.stringify(data)` | Transforme un objet JS en texte JSON pour l'envoyer |
| `method: "POST"` | Cree quelque chose. "PUT" = modifier. "DELETE" = supprimer |
| `headers: { "Content-Type": "application/json" }` | Dit a l'API qu'on envoie du JSON |

---

### 3. `index.html` (Dashboard)

**C'est quoi ?** La page d'accueil. Elle affiche 3 cartes avec les statistiques (nombre de clients, produits, commandes) et un tableau des dernieres commandes.

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GestionPayeTonKawa - Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/style.css">
</head>
<body class="bg-gray-50 text-gray-800">
    <div class="flex h-screen">

        <!-- SIDEBAR -->
        <aside class="w-64 bg-gray-900 text-white flex flex-col">
            <div class="p-6 border-b border-gray-700">
                <h1 class="text-xl font-bold">PayeTonKawa</h1>
                <p class="text-gray-400 text-sm">Gestion</p>
            </div>
            <nav class="flex-1 p-4 space-y-1">
                <a href="index.html" class="nav-link active flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Dashboard</span>
                </a>
                <a href="clients.html" class="nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Clients</span>
                </a>
                <a href="produits.html" class="nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Produits</span>
                </a>
                <a href="commandes.html" class="nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Commandes</span>
                </a>
            </nav>
            <div class="p-4 border-t border-gray-700 text-gray-500 text-xs">
                v1.0.0
            </div>
        </aside>

        <!-- CONTENU PRINCIPAL -->
        <main class="flex-1 overflow-y-auto">
            <header class="bg-white border-b px-8 py-5">
                <h2 class="text-2xl font-semibold">Dashboard</h2>
                <p class="text-gray-500 text-sm mt-1">Vue d'ensemble de l'activite</p>
            </header>

            <div class="p-8">
                <!-- 3 CARTES DE STATISTIQUES -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <!-- Carte Clients -->
                    <div class="bg-white rounded-xl shadow-sm border p-6">
                        <p class="text-sm text-gray-500 uppercase tracking-wide">Clients</p>
                        <p id="stat-clients" class="text-3xl font-bold mt-2">--</p>
                        <p class="text-sm text-gray-400 mt-1">clients enregistres</p>
                    </div>
                    <!-- Carte Produits -->
                    <div class="bg-white rounded-xl shadow-sm border p-6">
                        <p class="text-sm text-gray-500 uppercase tracking-wide">Produits</p>
                        <p id="stat-produits" class="text-3xl font-bold mt-2">--</p>
                        <p class="text-sm text-gray-400 mt-1">produits en catalogue</p>
                    </div>
                    <!-- Carte Commandes -->
                    <div class="bg-white rounded-xl shadow-sm border p-6">
                        <p class="text-sm text-gray-500 uppercase tracking-wide">Commandes</p>
                        <p id="stat-commandes" class="text-3xl font-bold mt-2">--</p>
                        <p class="text-sm text-gray-400 mt-1">commandes passees</p>
                    </div>
                </div>

                <!-- TABLEAU DES DERNIERES COMMANDES -->
                <div class="bg-white rounded-xl shadow-sm border">
                    <div class="px-6 py-4 border-b">
                        <h3 class="text-lg font-semibold">Dernieres commandes</h3>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead class="bg-gray-50 text-left text-sm text-gray-500">
                                <tr>
                                    <th class="px-6 py-3">ID</th>
                                    <th class="px-6 py-3">Client ID</th>
                                    <th class="px-6 py-3">Total</th>
                                    <th class="px-6 py-3">Statut</th>
                                    <th class="px-6 py-3">Date</th>
                                </tr>
                            </thead>
                            <tbody id="table-commandes" class="divide-y text-sm">
                                <!-- Rempli par JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script src="js/api.js"></script>
    <script src="js/dashboard.js"></script>
</body>
</html>
```

**Structure de la page :**

| Zone | Ce qu'elle contient |
|------|-------------------|
| Sidebar (a gauche) | Logo + liens de navigation (Dashboard, Clients, Produits, Commandes) |
| Header (en haut) | Titre de la page |
| 3 cartes | Nombre de clients, produits, commandes (charges depuis les APIs) |
| Tableau | Les dernieres commandes |

**Concepts Tailwind utilises :**

| Classe | Ce que ca fait |
|--------|---------------|
| `flex h-screen` | Disposition en colonnes, hauteur 100% de l'ecran |
| `w-64` | Largeur fixe pour la sidebar (256px) |
| `grid grid-cols-3 gap-6` | Grille de 3 colonnes avec espacement |
| `rounded-xl shadow-sm` | Coins arrondis + ombre legere |
| `bg-gray-50` | Fond gris tres clair |
| `text-2xl font-semibold` | Texte grand et semi-gras |
| `overflow-y-auto` | Scroll vertical si le contenu depasse |

---

### 4. `js/dashboard.js`

**C'est quoi ?** Le code JavaScript qui charge les statistiques et les commandes au chargement de la page.

```javascript
// Se lance quand la page est chargee
document.addEventListener("DOMContentLoaded", async function () {
    // Charger les stats
    try {
        const clients = await getClients();
        document.getElementById("stat-clients").textContent = clients.length;
    } catch (e) {
        document.getElementById("stat-clients").textContent = "Err";
    }

    try {
        const produits = await getProduits();
        document.getElementById("stat-produits").textContent = produits.length;
    } catch (e) {
        document.getElementById("stat-produits").textContent = "Err";
    }

    try {
        const commandes = await getCommandes();
        document.getElementById("stat-commandes").textContent = commandes.length;

        // Afficher les 5 dernieres commandes dans le tableau
        const tbody = document.getElementById("table-commandes");
        const dernieres = commandes.slice(-5).reverse();

        if (dernieres.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-gray-400">Aucune commande</td></tr>';
            return;
        }

        tbody.innerHTML = dernieres.map(function (c) {
            const date = new Date(c.date_commande).toLocaleDateString("fr-FR");
            return '<tr class="hover:bg-gray-50">'
                + '<td class="px-6 py-3 font-medium">#' + c.id + '</td>'
                + '<td class="px-6 py-3">' + c.client_id + '</td>'
                + '<td class="px-6 py-3 font-medium">' + c.total.toFixed(2) + ' EUR</td>'
                + '<td class="px-6 py-3"><span class="badge badge-' + c.statut + '">' + c.statut + '</span></td>'
                + '<td class="px-6 py-3 text-gray-500">' + date + '</td>'
                + '</tr>';
        }).join("");

    } catch (e) {
        document.getElementById("stat-commandes").textContent = "Err";
    }
});
```

**Explication :**

| Partie | Ce que ca fait |
|--------|---------------|
| `document.addEventListener("DOMContentLoaded", ...)` | Attend que la page soit chargee avant de lancer le code |
| `await getClients()` | Appelle l'API Clients et attend la reponse |
| `.length` | Compte le nombre d'elements dans la liste |
| `try / catch` | Si l'API ne repond pas, affiche "Err" au lieu de planter |
| `.slice(-5).reverse()` | Prend les 5 dernieres commandes et les met dans l'ordre du plus recent |
| `.toFixed(2)` | Affiche le prix avec 2 decimales (15.90 au lieu de 15.9) |
| `.toLocaleDateString("fr-FR")` | Affiche la date en format francais (12/02/2026) |

---

### 5. `clients.html`

**C'est quoi ?** La page de gestion des clients. Affiche un tableau avec tous les clients et permet d'en ajouter ou supprimer.

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GestionPayeTonKawa - Clients</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/style.css">
</head>
<body class="bg-gray-50 text-gray-800">
    <div class="flex h-screen">

        <!-- SIDEBAR -->
        <aside class="w-64 bg-gray-900 text-white flex flex-col">
            <div class="p-6 border-b border-gray-700">
                <h1 class="text-xl font-bold">PayeTonKawa</h1>
                <p class="text-gray-400 text-sm">Gestion</p>
            </div>
            <nav class="flex-1 p-4 space-y-1">
                <a href="index.html" class="nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Dashboard</span>
                </a>
                <a href="clients.html" class="nav-link active flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Clients</span>
                </a>
                <a href="produits.html" class="nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Produits</span>
                </a>
                <a href="commandes.html" class="nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Commandes</span>
                </a>
            </nav>
            <div class="p-4 border-t border-gray-700 text-gray-500 text-xs">
                v1.0.0
            </div>
        </aside>

        <!-- CONTENU PRINCIPAL -->
        <main class="flex-1 overflow-y-auto">
            <header class="bg-white border-b px-8 py-5 flex items-center justify-between">
                <div>
                    <h2 class="text-2xl font-semibold">Clients</h2>
                    <p class="text-gray-500 text-sm mt-1">Gestion des clients</p>
                </div>
                <button onclick="openModal()" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition">
                    + Ajouter un client
                </button>
            </header>

            <div class="p-8">
                <div class="bg-white rounded-xl shadow-sm border">
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead class="bg-gray-50 text-left text-sm text-gray-500">
                                <tr>
                                    <th class="px-6 py-3">ID</th>
                                    <th class="px-6 py-3">Nom</th>
                                    <th class="px-6 py-3">Prenom</th>
                                    <th class="px-6 py-3">Email</th>
                                    <th class="px-6 py-3">Telephone</th>
                                    <th class="px-6 py-3">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="table-clients" class="divide-y text-sm">
                                <!-- Rempli par JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- MODALE : Formulaire d'ajout -->
    <div id="modal" class="modal-backdrop fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 p-6">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-semibold">Nouveau client</h3>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
            </div>
            <form id="form-client" class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Nom</label>
                        <input type="text" id="input-nom" required class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Prenom</label>
                        <input type="text" id="input-prenom" required class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none">
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input type="email" id="input-email" required class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Telephone</label>
                        <input type="text" id="input-telephone" class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Adresse</label>
                        <input type="text" id="input-adresse" class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none">
                    </div>
                </div>
                <div class="flex justify-end gap-3 pt-4">
                    <button type="button" onclick="closeModal()" class="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50 transition">Annuler</button>
                    <button type="submit" class="px-4 py-2 text-sm text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition">Enregistrer</button>
                </div>
            </form>
        </div>
    </div>

    <script src="js/api.js"></script>
    <script src="js/clients.js"></script>
</body>
</html>
```

**Elements de la page :**

| Element | Ce que c'est |
|---------|-------------|
| Bouton "Ajouter" | En haut a droite, ouvre la modale |
| Tableau | Liste tous les clients avec ID, Nom, Prenom, Email, Telephone |
| Actions | Bouton "Supprimer" sur chaque ligne |
| Modale | Formulaire pop-up pour ajouter un client (nom, prenom, email, telephone, adresse) |

**Concepts HTML/Tailwind :**

| Element | Explication |
|---------|-------------|
| `onclick="openModal()"` | Appelle la fonction JS quand on clique |
| `fixed inset-0` | La modale couvre tout l'ecran |
| `hidden` | Cache la modale par defaut |
| `z-50` | La modale passe au-dessus de tout |
| `focus:ring-2 focus:ring-indigo-500` | Bordure violette quand on clique sur un champ |

---

### 6. `js/clients.js`

**C'est quoi ?** Le code JavaScript de la page clients. Il charge la liste, gere l'ajout et la suppression.

```javascript
// Charger la liste des clients au demarrage
document.addEventListener("DOMContentLoaded", function () {
    loadClients();
});

// Charger et afficher les clients
async function loadClients() {
    var tbody = document.getElementById("table-clients");

    try {
        var clients = await getClients();

        if (clients.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-gray-400">Aucun client enregistre</td></tr>';
            return;
        }

        tbody.innerHTML = clients.map(function (c) {
            return '<tr class="hover:bg-gray-50">'
                + '<td class="px-6 py-3 font-medium">#' + c.id + '</td>'
                + '<td class="px-6 py-3">' + c.nom + '</td>'
                + '<td class="px-6 py-3">' + c.prenom + '</td>'
                + '<td class="px-6 py-3">' + c.email + '</td>'
                + '<td class="px-6 py-3">' + (c.telephone || '-') + '</td>'
                + '<td class="px-6 py-3">'
                + '  <button onclick="supprimerClient(' + c.id + ')" class="text-red-600 hover:text-red-800 text-sm font-medium">Supprimer</button>'
                + '</td>'
                + '</tr>';
        }).join("");

    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-red-500">Erreur de connexion a l\'API</td></tr>';
    }
}

// Ouvrir la modale
function openModal() {
    document.getElementById("modal").classList.remove("hidden");
    document.getElementById("modal").classList.add("flex");
}

// Fermer la modale
function closeModal() {
    document.getElementById("modal").classList.add("hidden");
    document.getElementById("modal").classList.remove("flex");
    document.getElementById("form-client").reset();
}

// Envoyer le formulaire
document.getElementById("form-client").addEventListener("submit", async function (e) {
    e.preventDefault();

    var data = {
        nom: document.getElementById("input-nom").value,
        prenom: document.getElementById("input-prenom").value,
        email: document.getElementById("input-email").value,
        telephone: document.getElementById("input-telephone").value || null,
        adresse: document.getElementById("input-adresse").value || null
    };

    try {
        await createClient(data);
        closeModal();
        loadClients();
    } catch (e) {
        alert("Erreur lors de la creation du client");
    }
});

// Supprimer un client
async function supprimerClient(id) {
    if (confirm("Voulez-vous vraiment supprimer ce client ?")) {
        try {
            await deleteClient(id);
            loadClients();
        } catch (e) {
            alert("Erreur lors de la suppression");
        }
    }
}
```

**Chaque fonction expliquee :**

| Fonction | Ce qu'elle fait |
|----------|----------------|
| `loadClients()` | Appelle l'API, recupere les clients, les affiche dans le tableau |
| `openModal()` | Affiche le formulaire pop-up |
| `closeModal()` | Cache le formulaire et vide les champs |
| `submit (formulaire)` | Recupere les valeurs du formulaire, appelle `createClient`, recharge la liste |
| `supprimerClient(id)` | Demande confirmation, appelle `deleteClient`, recharge la liste |

**Concepts JS :**

| Concept | Explication |
|---------|-------------|
| `e.preventDefault()` | Empeche le formulaire de recharger la page |
| `confirm(...)` | Affiche une boite de dialogue Oui/Non |
| `.classList.add("hidden")` | Ajoute la classe "hidden" pour cacher un element |
| `.classList.remove("hidden")` | Retire la classe "hidden" pour montrer un element |
| `\|\| null` | Si le champ est vide, envoie null a l'API |
| `.map(function(c) {...}).join("")` | Transforme chaque client en ligne HTML et les assemble |

---

### 7. `produits.html`

**C'est quoi ?** La page de gestion des produits. Meme structure que la page clients mais adaptee aux produits.

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GestionPayeTonKawa - Produits</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/style.css">
</head>
<body class="bg-gray-50 text-gray-800">
    <div class="flex h-screen">

        <!-- SIDEBAR -->
        <aside class="w-64 bg-gray-900 text-white flex flex-col">
            <div class="p-6 border-b border-gray-700">
                <h1 class="text-xl font-bold">PayeTonKawa</h1>
                <p class="text-gray-400 text-sm">Gestion</p>
            </div>
            <nav class="flex-1 p-4 space-y-1">
                <a href="index.html" class="nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Dashboard</span>
                </a>
                <a href="clients.html" class="nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Clients</span>
                </a>
                <a href="produits.html" class="nav-link active flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Produits</span>
                </a>
                <a href="commandes.html" class="nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Commandes</span>
                </a>
            </nav>
            <div class="p-4 border-t border-gray-700 text-gray-500 text-xs">
                v1.0.0
            </div>
        </aside>

        <!-- CONTENU PRINCIPAL -->
        <main class="flex-1 overflow-y-auto">
            <header class="bg-white border-b px-8 py-5 flex items-center justify-between">
                <div>
                    <h2 class="text-2xl font-semibold">Produits</h2>
                    <p class="text-gray-500 text-sm mt-1">Catalogue des cafes</p>
                </div>
                <button onclick="openModal()" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition">
                    + Ajouter un produit
                </button>
            </header>

            <div class="p-8">
                <div class="bg-white rounded-xl shadow-sm border">
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead class="bg-gray-50 text-left text-sm text-gray-500">
                                <tr>
                                    <th class="px-6 py-3">ID</th>
                                    <th class="px-6 py-3">Nom</th>
                                    <th class="px-6 py-3">Prix</th>
                                    <th class="px-6 py-3">Stock</th>
                                    <th class="px-6 py-3">Origine</th>
                                    <th class="px-6 py-3">Poids</th>
                                    <th class="px-6 py-3">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="table-produits" class="divide-y text-sm">
                                <!-- Rempli par JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- MODALE : Formulaire d'ajout -->
    <div id="modal" class="modal-backdrop fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 p-6">
            <div class="flex items-center justify-between mb-6">
                <h3 id="modal-title" class="text-lg font-semibold">Nouveau produit</h3>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
            </div>
            <form id="form-produit" class="space-y-4">
                <input type="hidden" id="input-id">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Nom du cafe</label>
                    <input type="text" id="input-nom" required class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    <textarea id="input-description" rows="2" class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"></textarea>
                </div>
                <div class="grid grid-cols-3 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Prix (EUR)</label>
                        <input type="number" step="0.01" id="input-prix" required class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Stock</label>
                        <input type="number" id="input-stock" value="0" class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Poids (kg)</label>
                        <input type="number" step="0.01" id="input-poids" value="1.0" class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none">
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Origine</label>
                    <input type="text" id="input-origine" class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" placeholder="Bresil, Colombie, Ethiopie...">
                </div>
                <div class="flex justify-end gap-3 pt-4">
                    <button type="button" onclick="closeModal()" class="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50 transition">Annuler</button>
                    <button type="submit" class="px-4 py-2 text-sm text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition">Enregistrer</button>
                </div>
            </form>
        </div>
    </div>

    <script src="js/api.js"></script>
    <script src="js/produits.js"></script>
</body>
</html>
```

**Colonnes du tableau :**

| Colonne | Donnee |
|---------|--------|
| ID | Numero du produit |
| Nom | Nom du cafe |
| Prix | Prix en euros |
| Stock | Quantite en reserve |
| Origine | Pays d'origine |
| Poids | Poids en kg |
| Actions | Boutons Modifier et Supprimer |

---

### 8. `js/produits.js`

**C'est quoi ?** Le code JavaScript de la page produits. Gere la liste, l'ajout, la modification et la suppression.

```javascript
var editMode = false;

document.addEventListener("DOMContentLoaded", function () {
    loadProduits();
});

// Charger et afficher les produits
async function loadProduits() {
    var tbody = document.getElementById("table-produits");

    try {
        var produits = await getProduits();

        if (produits.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-gray-400">Aucun produit en catalogue</td></tr>';
            return;
        }

        tbody.innerHTML = produits.map(function (p) {
            return '<tr class="hover:bg-gray-50">'
                + '<td class="px-6 py-3 font-medium">#' + p.id + '</td>'
                + '<td class="px-6 py-3">' + p.nom + '</td>'
                + '<td class="px-6 py-3 font-medium">' + p.prix.toFixed(2) + ' EUR</td>'
                + '<td class="px-6 py-3">' + p.stock + '</td>'
                + '<td class="px-6 py-3">' + (p.origine || '-') + '</td>'
                + '<td class="px-6 py-3">' + p.poids_kg + ' kg</td>'
                + '<td class="px-6 py-3 space-x-2">'
                + '  <button onclick="modifierProduit(' + p.id + ')" class="text-indigo-600 hover:text-indigo-800 text-sm font-medium">Modifier</button>'
                + '  <button onclick="supprimerProduit(' + p.id + ')" class="text-red-600 hover:text-red-800 text-sm font-medium">Supprimer</button>'
                + '</td>'
                + '</tr>';
        }).join("");

    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-red-500">Erreur de connexion a l\'API</td></tr>';
    }
}

// Ouvrir la modale (mode ajout)
function openModal() {
    editMode = false;
    document.getElementById("modal-title").textContent = "Nouveau produit";
    document.getElementById("input-id").value = "";
    document.getElementById("form-produit").reset();
    document.getElementById("input-stock").value = "0";
    document.getElementById("input-poids").value = "1.0";
    document.getElementById("modal").classList.remove("hidden");
    document.getElementById("modal").classList.add("flex");
}

// Fermer la modale
function closeModal() {
    document.getElementById("modal").classList.add("hidden");
    document.getElementById("modal").classList.remove("flex");
}

// Ouvrir la modale en mode modification
async function modifierProduit(id) {
    editMode = true;
    var p = await getProduit(id);

    document.getElementById("modal-title").textContent = "Modifier le produit";
    document.getElementById("input-id").value = p.id;
    document.getElementById("input-nom").value = p.nom;
    document.getElementById("input-description").value = p.description || "";
    document.getElementById("input-prix").value = p.prix;
    document.getElementById("input-stock").value = p.stock;
    document.getElementById("input-poids").value = p.poids_kg;
    document.getElementById("input-origine").value = p.origine || "";

    document.getElementById("modal").classList.remove("hidden");
    document.getElementById("modal").classList.add("flex");
}

// Envoyer le formulaire (ajout ou modification)
document.getElementById("form-produit").addEventListener("submit", async function (e) {
    e.preventDefault();

    var data = {
        nom: document.getElementById("input-nom").value,
        description: document.getElementById("input-description").value || null,
        prix: parseFloat(document.getElementById("input-prix").value),
        stock: parseInt(document.getElementById("input-stock").value),
        poids_kg: parseFloat(document.getElementById("input-poids").value),
        origine: document.getElementById("input-origine").value || null
    };

    try {
        if (editMode) {
            var id = document.getElementById("input-id").value;
            await updateProduit(id, data);
        } else {
            await createProduit(data);
        }
        closeModal();
        loadProduits();
    } catch (e) {
        alert("Erreur lors de l'enregistrement");
    }
});

// Supprimer un produit
async function supprimerProduit(id) {
    if (confirm("Voulez-vous vraiment supprimer ce produit ?")) {
        try {
            await deleteProduit(id);
            loadProduits();
        } catch (e) {
            alert("Erreur lors de la suppression");
        }
    }
}
```

**Difference avec clients.js :** Ici on a un mode **modification** en plus. La meme modale sert pour l'ajout et la modification. La variable `editMode` permet de savoir si on cree ou si on modifie.

| Concept | Explication |
|---------|-------------|
| `editMode` | `false` = on ajoute, `true` = on modifie |
| `parseFloat(...)` | Convertit le texte du champ en nombre decimal |
| `parseInt(...)` | Convertit le texte du champ en nombre entier |
| `input-id` (hidden) | Champ cache qui stocke l'ID du produit en cours de modification |

---

### 9. `commandes.html`

**C'est quoi ?** La page la plus complexe. Elle affiche les commandes et permet d'en creer (en choisissant un client et des produits).

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GestionPayeTonKawa - Commandes</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/style.css">
</head>
<body class="bg-gray-50 text-gray-800">
    <div class="flex h-screen">

        <!-- SIDEBAR -->
        <aside class="w-64 bg-gray-900 text-white flex flex-col">
            <div class="p-6 border-b border-gray-700">
                <h1 class="text-xl font-bold">PayeTonKawa</h1>
                <p class="text-gray-400 text-sm">Gestion</p>
            </div>
            <nav class="flex-1 p-4 space-y-1">
                <a href="index.html" class="nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Dashboard</span>
                </a>
                <a href="clients.html" class="nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Clients</span>
                </a>
                <a href="produits.html" class="nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Produits</span>
                </a>
                <a href="commandes.html" class="nav-link active flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white">
                    <span>Commandes</span>
                </a>
            </nav>
            <div class="p-4 border-t border-gray-700 text-gray-500 text-xs">
                v1.0.0
            </div>
        </aside>

        <!-- CONTENU PRINCIPAL -->
        <main class="flex-1 overflow-y-auto">
            <header class="bg-white border-b px-8 py-5 flex items-center justify-between">
                <div>
                    <h2 class="text-2xl font-semibold">Commandes</h2>
                    <p class="text-gray-500 text-sm mt-1">Gestion des commandes</p>
                </div>
                <button onclick="openModal()" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition">
                    + Nouvelle commande
                </button>
            </header>

            <div class="p-8">
                <div class="bg-white rounded-xl shadow-sm border">
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead class="bg-gray-50 text-left text-sm text-gray-500">
                                <tr>
                                    <th class="px-6 py-3">ID</th>
                                    <th class="px-6 py-3">Client ID</th>
                                    <th class="px-6 py-3">Nb articles</th>
                                    <th class="px-6 py-3">Total</th>
                                    <th class="px-6 py-3">Statut</th>
                                    <th class="px-6 py-3">Date</th>
                                    <th class="px-6 py-3">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="table-commandes" class="divide-y text-sm">
                                <!-- Rempli par JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- MODALE : Nouvelle commande -->
    <div id="modal" class="modal-backdrop fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl mx-4 p-6">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-semibold">Nouvelle commande</h3>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
            </div>
            <form id="form-commande" class="space-y-4">
                <!-- Choix du client -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Client</label>
                    <select id="input-client" required class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none">
                        <option value="">-- Choisir un client --</option>
                    </select>
                </div>

                <!-- Lignes de commande -->
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label class="block text-sm font-medium text-gray-700">Articles</label>
                        <button type="button" onclick="ajouterLigne()" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium">+ Ajouter un article</button>
                    </div>
                    <div id="lignes-container" class="space-y-2">
                        <!-- Lignes ajoutees dynamiquement -->
                    </div>
                </div>

                <!-- Total -->
                <div class="bg-gray-50 rounded-lg p-4 text-right">
                    <span class="text-gray-500">Total : </span>
                    <span id="total-commande" class="text-xl font-bold">0.00 EUR</span>
                </div>

                <div class="flex justify-end gap-3 pt-4">
                    <button type="button" onclick="closeModal()" class="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50 transition">Annuler</button>
                    <button type="submit" class="px-4 py-2 text-sm text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition">Valider la commande</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODALE : Changer le statut -->
    <div id="modal-statut" class="modal-backdrop fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-semibold">Changer le statut</h3>
                <button onclick="closeModalStatut()" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
            </div>
            <form id="form-statut" class="space-y-4">
                <input type="hidden" id="statut-commande-id">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Nouveau statut</label>
                    <select id="input-statut" required class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none">
                        <option value="en_attente">En attente</option>
                        <option value="validee">Validee</option>
                        <option value="en_preparation">En preparation</option>
                        <option value="expediee">Expediee</option>
                        <option value="livree">Livree</option>
                        <option value="annulee">Annulee</option>
                    </select>
                </div>
                <div class="flex justify-end gap-3 pt-4">
                    <button type="button" onclick="closeModalStatut()" class="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50 transition">Annuler</button>
                    <button type="submit" class="px-4 py-2 text-sm text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition">Enregistrer</button>
                </div>
            </form>
        </div>
    </div>

    <script src="js/api.js"></script>
    <script src="js/commandes.js"></script>
</body>
</html>
```

**Les 2 modales :**

| Modale | Utilisation |
|--------|-------------|
| `#modal` | Creer une nouvelle commande (choisir client + ajouter des articles) |
| `#modal-statut` | Changer le statut d'une commande existante |

**Elements specifiques :**

| Element | Explication |
|---------|-------------|
| `<select id="input-client">` | Liste deroulante des clients (remplie par JS) |
| `#lignes-container` | Zone ou on ajoute les articles dynamiquement |
| `#total-commande` | Affiche le total calcule en temps reel |
| Bouton "+ Ajouter un article" | Ajoute une nouvelle ligne (produit + quantite) |

---

### 10. `js/commandes.js`

**C'est quoi ?** Le code JavaScript le plus complexe. Il gere la creation de commandes avec plusieurs articles, le changement de statut et la suppression.

```javascript
var produitsDisponibles = [];

document.addEventListener("DOMContentLoaded", function () {
    loadCommandes();
});

// Charger et afficher les commandes
async function loadCommandes() {
    var tbody = document.getElementById("table-commandes");

    try {
        var commandes = await getCommandes();

        if (commandes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-gray-400">Aucune commande</td></tr>';
            return;
        }

        tbody.innerHTML = commandes.map(function (c) {
            var date = new Date(c.date_commande).toLocaleDateString("fr-FR");
            var nbArticles = c.lignes.length;

            return '<tr class="hover:bg-gray-50">'
                + '<td class="px-6 py-3 font-medium">#' + c.id + '</td>'
                + '<td class="px-6 py-3">' + c.client_id + '</td>'
                + '<td class="px-6 py-3">' + nbArticles + '</td>'
                + '<td class="px-6 py-3 font-medium">' + c.total.toFixed(2) + ' EUR</td>'
                + '<td class="px-6 py-3"><span class="badge badge-' + c.statut + '">' + c.statut + '</span></td>'
                + '<td class="px-6 py-3 text-gray-500">' + date + '</td>'
                + '<td class="px-6 py-3 space-x-2">'
                + '  <button onclick="ouvrirStatut(' + c.id + ', \'' + c.statut + '\')" class="text-indigo-600 hover:text-indigo-800 text-sm font-medium">Statut</button>'
                + '  <button onclick="supprimerCommande(' + c.id + ')" class="text-red-600 hover:text-red-800 text-sm font-medium">Supprimer</button>'
                + '</td>'
                + '</tr>';
        }).join("");

    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-red-500">Erreur de connexion a l\'API</td></tr>';
    }
}

// --- MODALE NOUVELLE COMMANDE ---

async function openModal() {
    // Charger la liste des clients dans le select
    var selectClient = document.getElementById("input-client");
    selectClient.innerHTML = '<option value="">-- Choisir un client --</option>';

    try {
        var clients = await getClients();
        clients.forEach(function (c) {
            selectClient.innerHTML += '<option value="' + c.id + '">' + c.nom + ' ' + c.prenom + ' (' + c.email + ')</option>';
        });
    } catch (e) {
        alert("Impossible de charger les clients");
        return;
    }

    // Charger la liste des produits
    try {
        produitsDisponibles = await getProduits();
    } catch (e) {
        alert("Impossible de charger les produits");
        return;
    }

    // Vider les lignes et en ajouter une par defaut
    document.getElementById("lignes-container").innerHTML = "";
    ajouterLigne();

    document.getElementById("total-commande").textContent = "0.00 EUR";
    document.getElementById("modal").classList.remove("hidden");
    document.getElementById("modal").classList.add("flex");
}

function closeModal() {
    document.getElementById("modal").classList.add("hidden");
    document.getElementById("modal").classList.remove("flex");
}

// Ajouter une ligne d'article dans le formulaire
function ajouterLigne() {
    var container = document.getElementById("lignes-container");
    var index = container.children.length;

    var options = produitsDisponibles.map(function (p) {
        return '<option value="' + p.id + '" data-prix="' + p.prix + '">' + p.nom + ' - ' + p.prix.toFixed(2) + ' EUR</option>';
    }).join("");

    var ligneHTML = '<div class="flex gap-2 items-center ligne-commande">'
        + '<select name="produit" class="flex-1 border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none" onchange="calculerTotal()">'
        + '<option value="">-- Produit --</option>'
        + options
        + '</select>'
        + '<input type="number" name="quantite" value="1" min="1" class="w-20 border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none" onchange="calculerTotal()" oninput="calculerTotal()">'
        + '<button type="button" onclick="supprimerLigne(this)" class="text-red-500 hover:text-red-700 text-lg font-bold px-2">&times;</button>'
        + '</div>';

    container.innerHTML += ligneHTML;
}

// Supprimer une ligne d'article
function supprimerLigne(btn) {
    btn.parentElement.remove();
    calculerTotal();
}

// Calculer le total en temps reel
function calculerTotal() {
    var lignes = document.querySelectorAll(".ligne-commande");
    var total = 0;

    lignes.forEach(function (ligne) {
        var select = ligne.querySelector('select[name="produit"]');
        var qte = parseInt(ligne.querySelector('input[name="quantite"]').value) || 0;
        var option = select.options[select.selectedIndex];

        if (option && option.dataset.prix) {
            total += parseFloat(option.dataset.prix) * qte;
        }
    });

    document.getElementById("total-commande").textContent = total.toFixed(2) + " EUR";
}

// Envoyer le formulaire de commande
document.getElementById("form-commande").addEventListener("submit", async function (e) {
    e.preventDefault();

    var clientId = parseInt(document.getElementById("input-client").value);
    if (!clientId) {
        alert("Veuillez choisir un client");
        return;
    }

    var lignes = [];
    var lignesHTML = document.querySelectorAll(".ligne-commande");

    lignesHTML.forEach(function (ligne) {
        var select = ligne.querySelector('select[name="produit"]');
        var qte = parseInt(ligne.querySelector('input[name="quantite"]').value);
        var option = select.options[select.selectedIndex];

        if (select.value && qte > 0 && option.dataset.prix) {
            lignes.push({
                produit_id: parseInt(select.value),
                quantite: qte,
                prix_unitaire: parseFloat(option.dataset.prix)
            });
        }
    });

    if (lignes.length === 0) {
        alert("Ajoutez au moins un article");
        return;
    }

    var data = {
        client_id: clientId,
        lignes: lignes
    };

    try {
        await createCommande(data);
        closeModal();
        loadCommandes();
    } catch (e) {
        alert("Erreur lors de la creation de la commande");
    }
});

// --- MODALE STATUT ---

function ouvrirStatut(id, statutActuel) {
    document.getElementById("statut-commande-id").value = id;
    document.getElementById("input-statut").value = statutActuel;
    document.getElementById("modal-statut").classList.remove("hidden");
    document.getElementById("modal-statut").classList.add("flex");
}

function closeModalStatut() {
    document.getElementById("modal-statut").classList.add("hidden");
    document.getElementById("modal-statut").classList.remove("flex");
}

document.getElementById("form-statut").addEventListener("submit", async function (e) {
    e.preventDefault();

    var id = document.getElementById("statut-commande-id").value;
    var statut = document.getElementById("input-statut").value;

    try {
        await updateCommande(id, { statut: statut });
        closeModalStatut();
        loadCommandes();
    } catch (e) {
        alert("Erreur lors du changement de statut");
    }
});

// --- SUPPRESSION ---

async function supprimerCommande(id) {
    if (confirm("Voulez-vous vraiment supprimer cette commande ?")) {
        try {
            await deleteCommande(id);
            loadCommandes();
        } catch (e) {
            alert("Erreur lors de la suppression");
        }
    }
}
```

**Les fonctions specifiques aux commandes :**

| Fonction | Ce qu'elle fait |
|----------|----------------|
| `openModal()` | Charge la liste des clients ET des produits dans les listes deroulantes |
| `ajouterLigne()` | Ajoute une nouvelle ligne (choix produit + quantite) dans le formulaire |
| `supprimerLigne()` | Retire une ligne d'article du formulaire |
| `calculerTotal()` | Recalcule le total a chaque changement (produit ou quantite) |
| `ouvrirStatut(id, statut)` | Ouvre la modale de changement de statut |
| `supprimerCommande(id)` | Supprime la commande apres confirmation |

**Concepts nouveaux :**

| Concept | Explication |
|---------|-------------|
| `data-prix` | Attribut HTML personnalise qui stocke le prix dans l'option du select |
| `option.dataset.prix` | Recupere la valeur de `data-prix` en JavaScript |
| `document.querySelectorAll(...)` | Selectionne tous les elements qui correspondent au selecteur |
| `.forEach(function(x) {...})` | Execute une action sur chaque element de la liste |

---

## COMMENT LANCER LE FRONTEND

Le frontend est compose de fichiers HTML statiques. Il suffit d'ouvrir le fichier dans le navigateur :

```bash
# Option 1 : Ouvrir directement dans le navigateur
xdg-open /home/david/dev/Mspr/payetonkawa/gestionpayetonkawa/index.html

# Option 2 : Utiliser un mini serveur Python (recommande)
cd /home/david/dev/Mspr/payetonkawa/gestionpayetonkawa
python3 -m http.server 3000
# Puis ouvrir http://localhost:3000 dans le navigateur
```

L'option 2 (serveur Python) est recommandee car certains navigateurs bloquent les requetes `fetch` depuis un fichier local (`file://`).

---

## RAPPEL IMPORTANT : CORS

Avant de lancer le frontend, il faut ajouter le CORS dans les 3 APIs (voir section "AVANT DE COMMENCER" en haut de ce fichier). Sans ca, le navigateur bloquera toutes les requetes vers les APIs.
