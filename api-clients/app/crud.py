from sqlalchemy.orm import Session
from . import models, schemas

# CREATE - Créer un client en base
def create_client(db: Session, client: schemas.ClientCreate):
    # On transforme le schéma Pydantic en modèle SQLAlchemy
    db_client = models.Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

# READ - Récupérer un client par son ID unique
def get_client(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id).first()

# READ - Récupérer la liste de tous les clients
def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Client).offset(skip).limit(limit).all()

# DELETE - Supprimer un client
def delete_client(db: Session, client_id: int):
    db_client = get_client(db, client_id)
    if db_client:
        db.delete(db_client)
        db.commit()
        return True
    return False