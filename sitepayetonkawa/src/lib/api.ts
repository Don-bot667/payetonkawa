// Configuration des APIs
const API_CLIENTS = "http://localhost:8000";
const API_PRODUITS = "http://localhost:8001";
const API_COMMANDES = "http://localhost:8002";

// ============ TYPES ============

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

// ============ CLIENTS ============

export async function getClients(): Promise<Client[]> {
    const response = await fetch(`${API_CLIENTS}/customers/`);
    if (!response.ok) throw new Error("Erreur API Clients");
    return response.json();
}

export async function getClient(id: number): Promise<Client> {
    const response = await fetch(`${API_CLIENTS}/customers/${id}`);
    if (!response.ok) throw new Error("Client non trouve");
    return response.json();
}

export async function createClient(data: ClientCreate): Promise<Client> {
    const response = await fetch(`${API_CLIENTS}/customers/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error("Erreur creation client");
    return response.json();
}

// ============ PRODUITS ============

export async function getProduits(): Promise<Produit[]> {
    const response = await fetch(`${API_PRODUITS}/products/`);
    if (!response.ok) throw new Error("Erreur API Produits");
    return response.json();
}

export async function getProduit(id: number): Promise<Produit> {
    const response = await fetch(`${API_PRODUITS}/products/${id}`);
    if (!response.ok) throw new Error("Produit non trouve");
    return response.json();
}

// ============ COMMANDES ============

export async function getCommandes(): Promise<Commande[]> {
    const response = await fetch(`${API_COMMANDES}/orders/`);
    if (!response.ok) throw new Error("Erreur API Commandes");
    return response.json();
}

export async function getCommandesByClient(clientId: number): Promise<Commande[]> {
    const response = await fetch(`${API_COMMANDES}/orders/client/${clientId}`);
    if (!response.ok) throw new Error("Erreur recuperation commandes");
    return response.json();
}

export async function createCommande(data: CommandeCreate): Promise<Commande> {
    const response = await fetch(`${API_COMMANDES}/orders/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error("Erreur creation commande");
    return response.json();
}
