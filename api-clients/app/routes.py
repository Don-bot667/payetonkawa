from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas
from .database import get_db

router = APIRouter(prefix="/customers", tags=["Customers"])

# POST /customers : Créer un client
@router.post("/", response_model=schemas.ClientResponse, status_code=201)
def create_customer(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    return crud.create_client(db=db, client=client)

# GET /customers : Liste tous les clients
@router.get("/", response_model=List[schemas.ClientResponse])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_clients(db, skip=skip, limit=limit)

# GET /customers/{id} : Récupérer un client spécifique
@router.get("/{client_id}", response_model=schemas.ClientResponse)
def read_customer(client_id: int, db: Session = Depends(get_db)):
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return db_client

# DELETE /customers/{id} : Supprimer un client
@router.delete("/{client_id}", status_code=204)
def delete_customer(client_id: int, db: Session = Depends(get_db)):
    success = crud.delete_client(db, client_id=client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client non trouvé")