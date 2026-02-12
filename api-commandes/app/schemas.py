from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# --- LIGNES DE COMMANDE ---

# Ce qu'on envoie pour creer une ligne (dans une commande)
class LigneCommandeCreate(BaseModel):
    produit_id: int
    quantite: int = 1
    prix_unitaire: float


# Ce que l'API renvoie pour une ligne
class LigneCommandeResponse(BaseModel):
    id: int
    commande_id: int
    produit_id: int
    quantite: int
    prix_unitaire: float

    class Config:
        from_attributes = True


# --- COMMANDES ---

# Ce qu'on envoie pour CREER une commande (POST)
class CommandeCreate(BaseModel):
    client_id: int
    lignes: List[LigneCommandeCreate]


# Ce qu'on envoie pour MODIFIER le statut (PUT)
class CommandeUpdate(BaseModel):
    statut: Optional[str] = None


# Ce que l'API RENVOIE (la reponse complete)
class CommandeResponse(BaseModel):
    id: int
    client_id: int
    statut: str
    total: float
    date_commande: datetime
    date_modification: datetime
    lignes: List[LigneCommandeResponse]

    class Config:
        from_attributes = True