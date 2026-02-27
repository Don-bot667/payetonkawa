from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas, rabbitmq
from .database import get_db
from .auth import verify_api_key

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[Depends(verify_api_key)]
)

# POST /customers : Créer un client
@router.post("/", response_model=schemas.ClientResponse, status_code=201)
def create_customer(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    db_client = crud.create_client(db=db, client=client)
    rabbitmq.publish_client_created(db_client.id, {
        "nom": db_client.nom,
        "email": db_client.email,
        "adresse": db_client.adresse,
        "telephone": db_client.telephone
    })
    return db_client

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

# PUT /customers/{id} : Modifier un client
@router.put("/{client_id}", response_model=schemas.ClientResponse)
def update_customer(client_id: int, client: schemas.ClientUpdate, db: Session = Depends(get_db)):
    db_client = crud.update_client(db, client_id=client_id, client=client)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    rabbitmq.publish_client_updated(db_client.id, {
        "nom": db_client.nom,
        "email": db_client.email,
        "adresse": db_client.adresse,
        "telephone": db_client.telephone
    })
    return db_client

# DELETE /customers/{id} : Supprimer un client
@router.delete("/{client_id}", status_code=204)
def delete_customer(client_id: int, db: Session = Depends(get_db)):
    success = crud.delete_client(db, client_id=client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    rabbitmq.publish_client_deleted(client_id)