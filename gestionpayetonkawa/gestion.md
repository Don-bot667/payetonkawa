# GestionPayeTonKawa - Guide complet du Frontend avec Astro

---

## RESUME RAPIDE

Un site web de gestion pour PayeTonKawa. Il permet de gerer les clients, les produits et les commandes depuis le navigateur. Il appelle les 3 APIs qu'on a deja creees.

Technos : **Astro + Tailwind CSS + TypeScript**

```
gestionpayetonkawa/
├── astro.config.mjs          <- Configuration Astro
├── tailwind.config.mjs       <- Configuration Tailwind
├── tsconfig.json             <- Configuration TypeScript
├── package.json              <- Dependances npm
├── src/
│   ├── layouts/
│   │   └── Layout.astro      <- Layout principal (sidebar + structure)
│   ├── components/
│   │   ├── Sidebar.astro     <- Barre laterale de navigation
│   │   ├── StatCard.astro    <- Carte de statistique
│   │   └── Modal.astro       <- Composant modale reutilisable
│   ├── lib/
│   │   └── api.ts            <- Fonctions pour appeler les 3 APIs
│   ├── pages/
│   │   ├── index.astro       <- Dashboard (page d'accueil)
│   │   ├── clients.astro     <- Page de gestion des clients
│   │   ├── produits.astro    <- Page de gestion des produits
│   │   └── commandes.astro   <- Page de gestion des commandes
│   └── styles/
│       └── global.css        <- Styles globaux
└── gestion.md                <- Ce fichier (le guide)
```

---

## POURQUOI ASTRO ?

| Avantage | Explication |
|----------|-------------|
| **Simple** | Syntaxe proche du HTML, facile a apprendre |
| **Rapide** | Genere du HTML statique, pas de JavaScript inutile |
| **Composants** | On peut reutiliser des morceaux de code (sidebar, modales...) |
| **Tailwind integre** | Installation en une commande |
| **Routing automatique** | Chaque fichier dans `pages/` devient une page |

---

## ETAPE 1 : CREER LE PROJET ASTRO

Ouvre ton terminal et place-toi dans le dossier `gestionpayetonkawa` :

```bash
cd /Users/faouzdon/Desktop/payetonkawa/gestionpayetonkawa
```

Cree le projet Astro (reponds aux questions) :

```bash
npm create astro@latest .
```

Quand il te demande :
- **How would you like to start your new project?** → `Empty`
- **Install dependencies?** → `Yes`
- **Do you plan to write TypeScript?** → `Yes`
- **How strict should TypeScript be?** → `Strict`
- **Initialize a new git repository?** → `No` (on a deja un repo)

---

## ETAPE 2 : INSTALLER TAILWIND CSS

```bash
npx astro add tailwind
```

Reponds `Yes` a toutes les questions. Astro va configurer Tailwind automatiquement.

---

## ETAPE 3 : STRUCTURE DES FICHIERS

Apres l'installation, cree les dossiers manquants :

```bash
mkdir -p src/layouts src/components src/lib src/styles
```

---

## AVANT DE COMMENCER : ACTIVER LE CORS

Les APIs tournent sur les ports 8000, 8001, 8002. Le frontend tourne sur un autre port (4321). Par defaut, le navigateur **bloque** les requetes entre ports differents. Il faut activer le CORS dans chaque API.

Modifie le fichier `main.py` de chaque API en ajoutant ces lignes :

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

Puis relance les conteneurs Docker :
```bash
cd /Users/faouzdon/Desktop/payetonkawa
docker compose down && docker compose up -d --build
```

---

## FICHIER PAR FICHIER

---

### 1. `src/styles/global.css`

**C'est quoi ?** Les styles globaux de l'application. Tailwind est deja inclus via la config.

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

---

### 2. `src/lib/api.ts`

**C'est quoi ?** Le fichier central qui contient toutes les fonctions pour appeler les 3 APIs. TypeScript permet d'avoir des types pour eviter les erreurs.

```typescript
// Adresses des 3 APIs
const API_CLIENTS = "http://localhost:8000";
const API_PRODUITS = "http://localhost:8001";
const API_COMMANDES = "http://localhost:8002";

// --- TYPES ---

export interface Client {
    id: number;
    nom: string;
    prenom: string;
    email: string;
    telephone?: string;
    adresse?: string;
}

export interface ClientCreate {
    nom: string;
    prenom: string;
    email: string;
    telephone?: string;
    adresse?: string;
}

export interface Produit {
    id: number;
    nom: string;
    description?: string;
    prix: number;
    stock: number;
    poids_kg: number;
    origine?: string;
}

export interface ProduitCreate {
    nom: string;
    description?: string;
    prix: number;
    stock: number;
    poids_kg: number;
    origine?: string;
}

export interface LigneCommande {
    id: number;
    produit_id: number;
    quantite: number;
    prix_unitaire: number;
}

export interface LigneCommandeCreate {
    produit_id: number;
    quantite: number;
    prix_unitaire: number;
}

export interface Commande {
    id: number;
    client_id: number;
    date_commande: string;
    statut: string;
    total: number;
    lignes: LigneCommande[];
}

export interface CommandeCreate {
    client_id: number;
    lignes: LigneCommandeCreate[];
}

// --- CLIENTS ---

export async function getClients(): Promise<Client[]> {
    const response = await fetch(`${API_CLIENTS}/customers/`);
    return await response.json();
}

export async function getClient(id: number): Promise<Client> {
    const response = await fetch(`${API_CLIENTS}/customers/${id}`);
    return await response.json();
}

export async function createClient(data: ClientCreate): Promise<Client> {
    const response = await fetch(`${API_CLIENTS}/customers/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return await response.json();
}

export async function deleteClient(id: number): Promise<void> {
    await fetch(`${API_CLIENTS}/customers/${id}`, {
        method: "DELETE"
    });
}

// --- PRODUITS ---

export async function getProduits(): Promise<Produit[]> {
    const response = await fetch(`${API_PRODUITS}/products/`);
    return await response.json();
}

export async function getProduit(id: number): Promise<Produit> {
    const response = await fetch(`${API_PRODUITS}/products/${id}`);
    return await response.json();
}

export async function createProduit(data: ProduitCreate): Promise<Produit> {
    const response = await fetch(`${API_PRODUITS}/products/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return await response.json();
}

export async function updateProduit(id: number, data: Partial<ProduitCreate>): Promise<Produit> {
    const response = await fetch(`${API_PRODUITS}/products/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return await response.json();
}

export async function deleteProduit(id: number): Promise<void> {
    await fetch(`${API_PRODUITS}/products/${id}`, {
        method: "DELETE"
    });
}

// --- COMMANDES ---

export async function getCommandes(): Promise<Commande[]> {
    const response = await fetch(`${API_COMMANDES}/orders/`);
    return await response.json();
}

export async function getCommande(id: number): Promise<Commande> {
    const response = await fetch(`${API_COMMANDES}/orders/${id}`);
    return await response.json();
}

export async function createCommande(data: CommandeCreate): Promise<Commande> {
    const response = await fetch(`${API_COMMANDES}/orders/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return await response.json();
}

export async function updateCommande(id: number, data: { statut: string }): Promise<Commande> {
    const response = await fetch(`${API_COMMANDES}/orders/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return await response.json();
}

export async function deleteCommande(id: number): Promise<void> {
    await fetch(`${API_COMMANDES}/orders/${id}`, {
        method: "DELETE"
    });
}
```

**Explication des concepts TypeScript :**

| Concept | Explication simple |
|---------|-------------------|
| `interface` | Definit la structure d'un objet (quels champs, quels types) |
| `Promise<Client[]>` | La fonction retourne une promesse qui contiendra une liste de clients |
| `Partial<ProduitCreate>` | Permet d'envoyer seulement certains champs (pas tous obligatoires) |
| `?: string` | Le champ est optionnel (peut etre absent ou null) |

---

### 3. `src/components/Sidebar.astro`

**C'est quoi ?** La barre laterale de navigation. On la met dans un composant pour la reutiliser sur toutes les pages.

```astro
---
// Props : la page actuelle pour mettre le lien en surbrillance
interface Props {
    currentPage: 'dashboard' | 'clients' | 'produits' | 'commandes';
}

const { currentPage } = Astro.props;
---

<aside class="w-64 bg-gray-900 text-white flex flex-col">
    <div class="p-6 border-b border-gray-700">
        <h1 class="text-xl font-bold">PayeTonKawa</h1>
        <p class="text-gray-400 text-sm">Gestion</p>
    </div>
    <nav class="flex-1 p-4 space-y-1">
        <a
            href="/"
            class:list={[
                "nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white",
                { active: currentPage === 'dashboard' }
            ]}
        >
            <span>Dashboard</span>
        </a>
        <a
            href="/clients"
            class:list={[
                "nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white",
                { active: currentPage === 'clients' }
            ]}
        >
            <span>Clients</span>
        </a>
        <a
            href="/produits"
            class:list={[
                "nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white",
                { active: currentPage === 'produits' }
            ]}
        >
            <span>Produits</span>
        </a>
        <a
            href="/commandes"
            class:list={[
                "nav-link flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white",
                { active: currentPage === 'commandes' }
            ]}
        >
            <span>Commandes</span>
        </a>
    </nav>
    <div class="p-4 border-t border-gray-700 text-gray-500 text-xs">
        v1.0.0
    </div>
</aside>
```

**Explication Astro :**

| Concept | Explication |
|---------|-------------|
| `---` (frontmatter) | Code JavaScript/TypeScript execute cote serveur |
| `interface Props` | Definit les parametres que le composant accepte |
| `Astro.props` | Recupere les parametres passes au composant |
| `class:list` | Permet de conditionner les classes CSS |

---

### 4. `src/components/StatCard.astro`

**C'est quoi ?** Une carte de statistique reutilisable pour le dashboard.

```astro
---
interface Props {
    title: string;
    value: string | number;
    description: string;
    id?: string;
}

const { title, value, description, id } = Astro.props;
---

<div class="bg-white rounded-xl shadow-sm border p-6">
    <p class="text-sm text-gray-500 uppercase tracking-wide">{title}</p>
    <p id={id} class="text-3xl font-bold mt-2">{value}</p>
    <p class="text-sm text-gray-400 mt-1">{description}</p>
</div>
```

---

### 5. `src/layouts/Layout.astro`

**C'est quoi ?** Le layout principal qui englobe toutes les pages. Il contient le head HTML, la sidebar et la structure generale.

```astro
---
import Sidebar from '../components/Sidebar.astro';
import '../styles/global.css';

interface Props {
    title: string;
    currentPage: 'dashboard' | 'clients' | 'produits' | 'commandes';
}

const { title, currentPage } = Astro.props;
---

<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - GestionPayeTonKawa</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-gray-50 text-gray-800">
    <div class="flex h-screen">
        <Sidebar currentPage={currentPage} />

        <main class="flex-1 overflow-y-auto">
            <slot />
        </main>
    </div>
</body>
</html>
```

**Explication :**

| Concept | Explication |
|---------|-------------|
| `import` | Importe un composant ou un fichier CSS |
| `<slot />` | L'endroit ou le contenu de la page sera insere |
| `{title}` | Affiche la valeur de la variable `title` |

---

### 6. `src/pages/index.astro` (Dashboard)

**C'est quoi ?** La page d'accueil. Elle affiche 3 cartes avec les statistiques et un tableau des dernieres commandes.

```astro
---
import Layout from '../layouts/Layout.astro';
import StatCard from '../components/StatCard.astro';
---

<Layout title="Dashboard" currentPage="dashboard">
    <header class="bg-white border-b px-8 py-5">
        <h2 class="text-2xl font-semibold">Dashboard</h2>
        <p class="text-gray-500 text-sm mt-1">Vue d'ensemble de l'activite</p>
    </header>

    <div class="p-8">
        <!-- 3 CARTES DE STATISTIQUES -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <StatCard
                title="Clients"
                value="--"
                description="clients enregistres"
                id="stat-clients"
            />
            <StatCard
                title="Produits"
                value="--"
                description="produits en catalogue"
                id="stat-produits"
            />
            <StatCard
                title="Commandes"
                value="--"
                description="commandes passees"
                id="stat-commandes"
            />
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
                        <tr>
                            <td colspan="5" class="px-6 py-8 text-center text-gray-400">Chargement...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</Layout>

<script>
    // Ce code s'execute cote client (dans le navigateur)
    import { getClients, getProduits, getCommandes } from '../lib/api';

    async function loadDashboard() {
        // Charger les stats clients
        try {
            const clients = await getClients();
            const el = document.getElementById("stat-clients");
            if (el) el.textContent = String(clients.length);
        } catch (e) {
            const el = document.getElementById("stat-clients");
            if (el) el.textContent = "Err";
        }

        // Charger les stats produits
        try {
            const produits = await getProduits();
            const el = document.getElementById("stat-produits");
            if (el) el.textContent = String(produits.length);
        } catch (e) {
            const el = document.getElementById("stat-produits");
            if (el) el.textContent = "Err";
        }

        // Charger les stats commandes + tableau
        try {
            const commandes = await getCommandes();
            const elStat = document.getElementById("stat-commandes");
            if (elStat) elStat.textContent = String(commandes.length);

            const tbody = document.getElementById("table-commandes");
            if (!tbody) return;

            const dernieres = commandes.slice(-5).reverse();

            if (dernieres.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-gray-400">Aucune commande</td></tr>';
                return;
            }

            tbody.innerHTML = dernieres.map(c => {
                const date = new Date(c.date_commande).toLocaleDateString("fr-FR");
                return `<tr class="hover:bg-gray-50">
                    <td class="px-6 py-3 font-medium">#${c.id}</td>
                    <td class="px-6 py-3">${c.client_id}</td>
                    <td class="px-6 py-3 font-medium">${c.total.toFixed(2)} EUR</td>
                    <td class="px-6 py-3"><span class="badge badge-${c.statut}">${c.statut}</span></td>
                    <td class="px-6 py-3 text-gray-500">${date}</td>
                </tr>`;
            }).join("");

        } catch (e) {
            const el = document.getElementById("stat-commandes");
            if (el) el.textContent = "Err";
        }
    }

    // Lancer au chargement de la page
    loadDashboard();
</script>
```

**Explication du `<script>` dans Astro :**

| Concept | Explication |
|---------|-------------|
| `<script>` | Code qui s'execute dans le navigateur (cote client) |
| `import` dans script | Importe les fonctions API |
| Template literals `` ` `` | Permet d'inserer des variables dans du texte avec `${variable}` |

---

### 7. `src/pages/clients.astro`

**C'est quoi ?** La page de gestion des clients. Affiche un tableau et permet d'ajouter/supprimer des clients.

```astro
---
import Layout from '../layouts/Layout.astro';
---

<Layout title="Clients" currentPage="clients">
    <header class="bg-white border-b px-8 py-5 flex items-center justify-between">
        <div>
            <h2 class="text-2xl font-semibold">Clients</h2>
            <p class="text-gray-500 text-sm mt-1">Gestion des clients</p>
        </div>
        <button id="btn-ajouter" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition">
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
                        <tr>
                            <td colspan="6" class="px-6 py-8 text-center text-gray-400">Chargement...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- MODALE : Formulaire d'ajout -->
    <div id="modal" class="modal-backdrop fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 p-6">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-semibold">Nouveau client</h3>
                <button id="btn-close-modal" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
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
                    <button type="button" id="btn-annuler" class="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50 transition">Annuler</button>
                    <button type="submit" class="px-4 py-2 text-sm text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition">Enregistrer</button>
                </div>
            </form>
        </div>
    </div>
</Layout>

<script>
    import { getClients, createClient, deleteClient, type ClientCreate } from '../lib/api';

    const modal = document.getElementById("modal")!;
    const btnAjouter = document.getElementById("btn-ajouter")!;
    const btnClose = document.getElementById("btn-close-modal")!;
    const btnAnnuler = document.getElementById("btn-annuler")!;
    const form = document.getElementById("form-client") as HTMLFormElement;
    const tbody = document.getElementById("table-clients")!;

    // Charger les clients
    async function loadClients() {
        try {
            const clients = await getClients();

            if (clients.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-gray-400">Aucun client enregistre</td></tr>';
                return;
            }

            tbody.innerHTML = clients.map(c => `
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-3 font-medium">#${c.id}</td>
                    <td class="px-6 py-3">${c.nom}</td>
                    <td class="px-6 py-3">${c.prenom}</td>
                    <td class="px-6 py-3">${c.email}</td>
                    <td class="px-6 py-3">${c.telephone || '-'}</td>
                    <td class="px-6 py-3">
                        <button data-delete="${c.id}" class="text-red-600 hover:text-red-800 text-sm font-medium">Supprimer</button>
                    </td>
                </tr>
            `).join("");

            // Ajouter les event listeners pour les boutons supprimer
            document.querySelectorAll('[data-delete]').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const id = (e.target as HTMLElement).dataset.delete!;
                    if (confirm("Voulez-vous vraiment supprimer ce client ?")) {
                        try {
                            await deleteClient(parseInt(id));
                            loadClients();
                        } catch {
                            alert("Erreur lors de la suppression");
                        }
                    }
                });
            });

        } catch {
            tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-red-500">Erreur de connexion a l\'API</td></tr>';
        }
    }

    // Ouvrir/fermer la modale
    function openModal() {
        modal.classList.remove("hidden");
        modal.classList.add("flex");
    }

    function closeModal() {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
        form.reset();
    }

    btnAjouter.addEventListener('click', openModal);
    btnClose.addEventListener('click', closeModal);
    btnAnnuler.addEventListener('click', closeModal);

    // Soumettre le formulaire
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data: ClientCreate = {
            nom: (document.getElementById("input-nom") as HTMLInputElement).value,
            prenom: (document.getElementById("input-prenom") as HTMLInputElement).value,
            email: (document.getElementById("input-email") as HTMLInputElement).value,
            telephone: (document.getElementById("input-telephone") as HTMLInputElement).value || undefined,
            adresse: (document.getElementById("input-adresse") as HTMLInputElement).value || undefined
        };

        try {
            await createClient(data);
            closeModal();
            loadClients();
        } catch {
            alert("Erreur lors de la creation du client");
        }
    });

    // Charger au demarrage
    loadClients();
</script>
```

**Concepts importants :**

| Concept | Explication |
|---------|-------------|
| `document.getElementById("...")!` | Le `!` dit a TypeScript que l'element existe forcement |
| `as HTMLFormElement` | Indique a TypeScript le type exact de l'element |
| `data-delete="${c.id}"` | Attribut HTML personnalise pour stocker l'ID |
| `dataset.delete` | Recupere la valeur de `data-delete` en JavaScript |

---

### 8. `src/pages/produits.astro`

**C'est quoi ?** La page de gestion des produits. Permet d'ajouter, modifier et supprimer des produits.

```astro
---
import Layout from '../layouts/Layout.astro';
---

<Layout title="Produits" currentPage="produits">
    <header class="bg-white border-b px-8 py-5 flex items-center justify-between">
        <div>
            <h2 class="text-2xl font-semibold">Produits</h2>
            <p class="text-gray-500 text-sm mt-1">Catalogue des cafes</p>
        </div>
        <button id="btn-ajouter" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition">
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
                        <tr>
                            <td colspan="7" class="px-6 py-8 text-center text-gray-400">Chargement...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- MODALE : Formulaire d'ajout/modification -->
    <div id="modal" class="modal-backdrop fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 p-6">
            <div class="flex items-center justify-between mb-6">
                <h3 id="modal-title" class="text-lg font-semibold">Nouveau produit</h3>
                <button id="btn-close-modal" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
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
                    <button type="button" id="btn-annuler" class="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50 transition">Annuler</button>
                    <button type="submit" class="px-4 py-2 text-sm text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition">Enregistrer</button>
                </div>
            </form>
        </div>
    </div>
</Layout>

<script>
    import { getProduits, getProduit, createProduit, updateProduit, deleteProduit, type ProduitCreate } from '../lib/api';

    let editMode = false;

    const modal = document.getElementById("modal")!;
    const modalTitle = document.getElementById("modal-title")!;
    const btnAjouter = document.getElementById("btn-ajouter")!;
    const btnClose = document.getElementById("btn-close-modal")!;
    const btnAnnuler = document.getElementById("btn-annuler")!;
    const form = document.getElementById("form-produit") as HTMLFormElement;
    const tbody = document.getElementById("table-produits")!;

    const inputId = document.getElementById("input-id") as HTMLInputElement;
    const inputNom = document.getElementById("input-nom") as HTMLInputElement;
    const inputDescription = document.getElementById("input-description") as HTMLTextAreaElement;
    const inputPrix = document.getElementById("input-prix") as HTMLInputElement;
    const inputStock = document.getElementById("input-stock") as HTMLInputElement;
    const inputPoids = document.getElementById("input-poids") as HTMLInputElement;
    const inputOrigine = document.getElementById("input-origine") as HTMLInputElement;

    // Charger les produits
    async function loadProduits() {
        try {
            const produits = await getProduits();

            if (produits.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-gray-400">Aucun produit en catalogue</td></tr>';
                return;
            }

            tbody.innerHTML = produits.map(p => `
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-3 font-medium">#${p.id}</td>
                    <td class="px-6 py-3">${p.nom}</td>
                    <td class="px-6 py-3 font-medium">${p.prix.toFixed(2)} EUR</td>
                    <td class="px-6 py-3">${p.stock}</td>
                    <td class="px-6 py-3">${p.origine || '-'}</td>
                    <td class="px-6 py-3">${p.poids_kg} kg</td>
                    <td class="px-6 py-3 space-x-2">
                        <button data-edit="${p.id}" class="text-indigo-600 hover:text-indigo-800 text-sm font-medium">Modifier</button>
                        <button data-delete="${p.id}" class="text-red-600 hover:text-red-800 text-sm font-medium">Supprimer</button>
                    </td>
                </tr>
            `).join("");

            // Event listeners pour modifier
            document.querySelectorAll('[data-edit]').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const id = parseInt((e.target as HTMLElement).dataset.edit!);
                    await openEditModal(id);
                });
            });

            // Event listeners pour supprimer
            document.querySelectorAll('[data-delete]').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const id = (e.target as HTMLElement).dataset.delete!;
                    if (confirm("Voulez-vous vraiment supprimer ce produit ?")) {
                        try {
                            await deleteProduit(parseInt(id));
                            loadProduits();
                        } catch {
                            alert("Erreur lors de la suppression");
                        }
                    }
                });
            });

        } catch {
            tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-red-500">Erreur de connexion a l\'API</td></tr>';
        }
    }

    // Ouvrir modale en mode ajout
    function openModal() {
        editMode = false;
        modalTitle.textContent = "Nouveau produit";
        form.reset();
        inputStock.value = "0";
        inputPoids.value = "1.0";
        modal.classList.remove("hidden");
        modal.classList.add("flex");
    }

    // Ouvrir modale en mode modification
    async function openEditModal(id: number) {
        editMode = true;
        modalTitle.textContent = "Modifier le produit";

        const p = await getProduit(id);
        inputId.value = String(p.id);
        inputNom.value = p.nom;
        inputDescription.value = p.description || "";
        inputPrix.value = String(p.prix);
        inputStock.value = String(p.stock);
        inputPoids.value = String(p.poids_kg);
        inputOrigine.value = p.origine || "";

        modal.classList.remove("hidden");
        modal.classList.add("flex");
    }

    function closeModal() {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
    }

    btnAjouter.addEventListener('click', openModal);
    btnClose.addEventListener('click', closeModal);
    btnAnnuler.addEventListener('click', closeModal);

    // Soumettre le formulaire
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const data: ProduitCreate = {
            nom: inputNom.value,
            description: inputDescription.value || undefined,
            prix: parseFloat(inputPrix.value),
            stock: parseInt(inputStock.value),
            poids_kg: parseFloat(inputPoids.value),
            origine: inputOrigine.value || undefined
        };

        try {
            if (editMode) {
                await updateProduit(parseInt(inputId.value), data);
            } else {
                await createProduit(data);
            }
            closeModal();
            loadProduits();
        } catch {
            alert("Erreur lors de l'enregistrement");
        }
    });

    // Charger au demarrage
    loadProduits();
</script>
```

---

### 9. `src/pages/commandes.astro`

**C'est quoi ?** La page la plus complexe. Elle affiche les commandes et permet d'en creer (en choisissant un client et des produits).

```astro
---
import Layout from '../layouts/Layout.astro';
---

<Layout title="Commandes" currentPage="commandes">
    <header class="bg-white border-b px-8 py-5 flex items-center justify-between">
        <div>
            <h2 class="text-2xl font-semibold">Commandes</h2>
            <p class="text-gray-500 text-sm mt-1">Gestion des commandes</p>
        </div>
        <button id="btn-ajouter" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition">
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
                        <tr>
                            <td colspan="7" class="px-6 py-8 text-center text-gray-400">Chargement...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- MODALE : Nouvelle commande -->
    <div id="modal" class="modal-backdrop fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl mx-4 p-6">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-semibold">Nouvelle commande</h3>
                <button id="btn-close-modal" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
            </div>
            <form id="form-commande" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Client</label>
                    <select id="input-client" required class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none">
                        <option value="">-- Choisir un client --</option>
                    </select>
                </div>

                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label class="block text-sm font-medium text-gray-700">Articles</label>
                        <button type="button" id="btn-ajouter-ligne" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium">+ Ajouter un article</button>
                    </div>
                    <div id="lignes-container" class="space-y-2">
                        <!-- Lignes ajoutees dynamiquement -->
                    </div>
                </div>

                <div class="bg-gray-50 rounded-lg p-4 text-right">
                    <span class="text-gray-500">Total : </span>
                    <span id="total-commande" class="text-xl font-bold">0.00 EUR</span>
                </div>

                <div class="flex justify-end gap-3 pt-4">
                    <button type="button" id="btn-annuler" class="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50 transition">Annuler</button>
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
                <button id="btn-close-statut" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
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
                    <button type="button" id="btn-annuler-statut" class="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50 transition">Annuler</button>
                    <button type="submit" class="px-4 py-2 text-sm text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition">Enregistrer</button>
                </div>
            </form>
        </div>
    </div>
</Layout>

<script>
    import {
        getClients, getProduits, getCommandes,
        createCommande, updateCommande, deleteCommande,
        type Produit, type LigneCommandeCreate
    } from '../lib/api';

    let produitsDisponibles: Produit[] = [];

    const modal = document.getElementById("modal")!;
    const modalStatut = document.getElementById("modal-statut")!;
    const btnAjouter = document.getElementById("btn-ajouter")!;
    const btnClose = document.getElementById("btn-close-modal")!;
    const btnAnnuler = document.getElementById("btn-annuler")!;
    const btnCloseStatut = document.getElementById("btn-close-statut")!;
    const btnAnnulerStatut = document.getElementById("btn-annuler-statut")!;
    const btnAjouterLigne = document.getElementById("btn-ajouter-ligne")!;
    const form = document.getElementById("form-commande") as HTMLFormElement;
    const formStatut = document.getElementById("form-statut") as HTMLFormElement;
    const tbody = document.getElementById("table-commandes")!;
    const inputClient = document.getElementById("input-client") as HTMLSelectElement;
    const lignesContainer = document.getElementById("lignes-container")!;
    const totalEl = document.getElementById("total-commande")!;
    const inputStatut = document.getElementById("input-statut") as HTMLSelectElement;
    const statutCommandeId = document.getElementById("statut-commande-id") as HTMLInputElement;

    // Charger les commandes
    async function loadCommandes() {
        try {
            const commandes = await getCommandes();

            if (commandes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-gray-400">Aucune commande</td></tr>';
                return;
            }

            tbody.innerHTML = commandes.map(c => {
                const date = new Date(c.date_commande).toLocaleDateString("fr-FR");
                const nbArticles = c.lignes.length;
                return `
                    <tr class="hover:bg-gray-50">
                        <td class="px-6 py-3 font-medium">#${c.id}</td>
                        <td class="px-6 py-3">${c.client_id}</td>
                        <td class="px-6 py-3">${nbArticles}</td>
                        <td class="px-6 py-3 font-medium">${c.total.toFixed(2)} EUR</td>
                        <td class="px-6 py-3"><span class="badge badge-${c.statut}">${c.statut}</span></td>
                        <td class="px-6 py-3 text-gray-500">${date}</td>
                        <td class="px-6 py-3 space-x-2">
                            <button data-statut="${c.id}" data-current="${c.statut}" class="text-indigo-600 hover:text-indigo-800 text-sm font-medium">Statut</button>
                            <button data-delete="${c.id}" class="text-red-600 hover:text-red-800 text-sm font-medium">Supprimer</button>
                        </td>
                    </tr>
                `;
            }).join("");

            // Event listeners pour statut
            document.querySelectorAll('[data-statut]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const target = e.target as HTMLElement;
                    const id = target.dataset.statut!;
                    const current = target.dataset.current!;
                    openStatutModal(parseInt(id), current);
                });
            });

            // Event listeners pour supprimer
            document.querySelectorAll('[data-delete]').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const id = (e.target as HTMLElement).dataset.delete!;
                    if (confirm("Voulez-vous vraiment supprimer cette commande ?")) {
                        try {
                            await deleteCommande(parseInt(id));
                            loadCommandes();
                        } catch {
                            alert("Erreur lors de la suppression");
                        }
                    }
                });
            });

        } catch {
            tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-red-500">Erreur de connexion a l\'API</td></tr>';
        }
    }

    // Ouvrir modale nouvelle commande
    async function openModal() {
        // Charger les clients
        inputClient.innerHTML = '<option value="">-- Choisir un client --</option>';
        try {
            const clients = await getClients();
            clients.forEach(c => {
                inputClient.innerHTML += `<option value="${c.id}">${c.nom} ${c.prenom} (${c.email})</option>`;
            });
        } catch {
            alert("Impossible de charger les clients");
            return;
        }

        // Charger les produits
        try {
            produitsDisponibles = await getProduits();
        } catch {
            alert("Impossible de charger les produits");
            return;
        }

        lignesContainer.innerHTML = "";
        ajouterLigne();
        totalEl.textContent = "0.00 EUR";

        modal.classList.remove("hidden");
        modal.classList.add("flex");
    }

    function closeModal() {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
    }

    // Ajouter une ligne d'article
    function ajouterLigne() {
        const options = produitsDisponibles.map(p =>
            `<option value="${p.id}" data-prix="${p.prix}">${p.nom} - ${p.prix.toFixed(2)} EUR</option>`
        ).join("");

        const ligneHTML = `
            <div class="flex gap-2 items-center ligne-commande">
                <select name="produit" class="flex-1 border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none">
                    <option value="">-- Produit --</option>
                    ${options}
                </select>
                <input type="number" name="quantite" value="1" min="1" class="w-20 border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none">
                <button type="button" class="btn-supprimer-ligne text-red-500 hover:text-red-700 text-lg font-bold px-2">&times;</button>
            </div>
        `;

        lignesContainer.insertAdjacentHTML('beforeend', ligneHTML);

        // Event listeners pour la nouvelle ligne
        const nouvelleLigne = lignesContainer.lastElementChild!;
        nouvelleLigne.querySelector('select')!.addEventListener('change', calculerTotal);
        nouvelleLigne.querySelector('input')!.addEventListener('input', calculerTotal);
        nouvelleLigne.querySelector('.btn-supprimer-ligne')!.addEventListener('click', (e) => {
            (e.target as HTMLElement).closest('.ligne-commande')!.remove();
            calculerTotal();
        });
    }

    // Calculer le total
    function calculerTotal() {
        const lignes = document.querySelectorAll('.ligne-commande');
        let total = 0;

        lignes.forEach(ligne => {
            const select = ligne.querySelector('select[name="produit"]') as HTMLSelectElement;
            const qteInput = ligne.querySelector('input[name="quantite"]') as HTMLInputElement;
            const qte = parseInt(qteInput.value) || 0;
            const option = select.options[select.selectedIndex];

            if (option && option.dataset.prix) {
                total += parseFloat(option.dataset.prix) * qte;
            }
        });

        totalEl.textContent = total.toFixed(2) + " EUR";
    }

    btnAjouter.addEventListener('click', openModal);
    btnClose.addEventListener('click', closeModal);
    btnAnnuler.addEventListener('click', closeModal);
    btnAjouterLigne.addEventListener('click', ajouterLigne);

    // Soumettre le formulaire de commande
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const clientId = parseInt(inputClient.value);
        if (!clientId) {
            alert("Veuillez choisir un client");
            return;
        }

        const lignes: LigneCommandeCreate[] = [];
        document.querySelectorAll('.ligne-commande').forEach(ligne => {
            const select = ligne.querySelector('select[name="produit"]') as HTMLSelectElement;
            const qteInput = ligne.querySelector('input[name="quantite"]') as HTMLInputElement;
            const qte = parseInt(qteInput.value);
            const option = select.options[select.selectedIndex];

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

        try {
            await createCommande({ client_id: clientId, lignes });
            closeModal();
            loadCommandes();
        } catch {
            alert("Erreur lors de la creation de la commande");
        }
    });

    // Modale statut
    function openStatutModal(id: number, currentStatut: string) {
        statutCommandeId.value = String(id);
        inputStatut.value = currentStatut;
        modalStatut.classList.remove("hidden");
        modalStatut.classList.add("flex");
    }

    function closeStatutModal() {
        modalStatut.classList.add("hidden");
        modalStatut.classList.remove("flex");
    }

    btnCloseStatut.addEventListener('click', closeStatutModal);
    btnAnnulerStatut.addEventListener('click', closeStatutModal);

    formStatut.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = parseInt(statutCommandeId.value);
        const statut = inputStatut.value;

        try {
            await updateCommande(id, { statut });
            closeStatutModal();
            loadCommandes();
        } catch {
            alert("Erreur lors du changement de statut");
        }
    });

    // Charger au demarrage
    loadCommandes();
</script>
```

---

## COMMENT LANCER LE PROJET

### 1. Installer les dependances (une seule fois)

```bash
cd /Users/faouzdon/Desktop/payetonkawa/gestionpayetonkawa
npm install
```

### 2. Lancer en mode developpement

```bash
npm run dev
```

Astro demarre sur **http://localhost:4321**. Ouvre cette URL dans ton navigateur.

### 3. Build pour la production (optionnel)

```bash
npm run build
```

Les fichiers statiques sont generes dans le dossier `dist/`.

---

## RAPPEL IMPORTANT : CORS

Avant de lancer le frontend, il faut ajouter le CORS dans les 3 APIs (voir section "AVANT DE COMMENCER" en haut de ce fichier). Sans ca, le navigateur bloquera toutes les requetes vers les APIs.

---

## RESUME DES COMMANDES

```bash
# 1. Creer le projet Astro
cd /Users/faouzdon/Desktop/payetonkawa/gestionpayetonkawa
npm create astro@latest .

# 2. Installer Tailwind
npx astro add tailwind

# 3. Creer les dossiers
mkdir -p src/layouts src/components src/lib src/styles

# 4. Creer tous les fichiers (voir sections ci-dessus)

# 5. Lancer le serveur de dev
npm run dev

# Le site sera accessible sur http://localhost:4321
```

---

## STRUCTURE FINALE

```
gestionpayetonkawa/
├── astro.config.mjs
├── tailwind.config.mjs
├── tsconfig.json
├── package.json
├── package-lock.json
├── node_modules/
├── src/
│   ├── layouts/
│   │   └── Layout.astro
│   ├── components/
│   │   ├── Sidebar.astro
│   │   └── StatCard.astro
│   ├── lib/
│   │   └── api.ts
│   ├── pages/
│   │   ├── index.astro
│   │   ├── clients.astro
│   │   ├── produits.astro
│   │   └── commandes.astro
│   └── styles/
│       └── global.css
└── gestion.md
```
