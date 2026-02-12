from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Ce qu'on envoie pour CREER un produit (POST)
class ProduitCreate(BaseModel):
    nom: str
    description: Optional[str] = None
    prix: float
    stock: int = 0
    origine: Optional[str] = None
    poids_kg: float = 1.0


# Ce qu'on envoie pour MODIFIER un produit (PUT)
class ProduitUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    prix: Optional[float] = None
    stock: Optional[int] = None
    origine: Optional[str] = None
    poids_kg: Optional[float] = None
    actif: Optional[bool] = None


# Ce que l'API RENVOIE (la reponse)
class ProduitResponse(BaseModel):
    id: int
    nom: str
    description: Optional[str]
    prix: float
    stock: int
    origine: Optional[str]
    poids_kg: float
    actif: bool
    date_creation: datetime
    date_modification: datetime

    class Config:
        from_attributes = True