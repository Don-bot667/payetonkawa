
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