from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Ce qu'on reçoit lors de la CRÉATION [cite: 286]
class ClientCreate(BaseModel):
    nom: str
    prenom: str
    email: EmailStr 
    telephone: Optional[str] = None
    adresse: Optional[str] = None

# Ce qu'on renvoie au client (RESPONSE) [cite: 287]
class ClientResponse(BaseModel):
    id: int
    nom: str
    prenom: str
    email: str
    actif: bool
    created_at: datetime

    class Config:
        from_attributes = True # Permet de convertir l'objet BDD en JSON automatiquement [cite: 287]