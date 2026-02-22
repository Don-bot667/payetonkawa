/**
 * AUTHENTIFICATION SIMPLIFIEE
 * Les donnees sont stockees dans localStorage.
 */

import { getClients, createClient, type Client, type ClientCreate } from './api';

const STORAGE_KEY = 'payetonkawa_user';

export function getUser(): Client | null {
    if (typeof window === 'undefined') return null;

    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;

    try {
        return JSON.parse(stored);
    } catch {
        return null;
    }
}

export function isLoggedIn(): boolean {
    return getUser() !== null;
}

export async function login(email: string): Promise<Client> {
    const clients = await getClients();
    const client = clients.find(c => c.email.toLowerCase() === email.toLowerCase());

    if (!client) {
        throw new Error("Aucun compte trouve avec cet email");
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(client));
    return client;
}

export async function register(data: ClientCreate): Promise<Client> {
    const clients = await getClients();
    const exists = clients.some(c => c.email.toLowerCase() === data.email.toLowerCase());

    if (exists) {
        throw new Error("Un compte existe deja avec cet email");
    }

    const newClient = await createClient(data);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newClient));
    return newClient;
}

export function logout(): void {
    localStorage.removeItem(STORAGE_KEY);
}
