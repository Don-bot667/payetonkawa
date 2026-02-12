from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas
from .database import get_db

router = APIRouter(prefix="/products", tags=["Products"])


# POST /products : Creer un produit
@router.post("/", response_model=schemas.ProduitResponse, status_code=201)
def create_product(produit: schemas.ProduitCreate, db: Session = Depends(get_db)):
    return crud.create_produit(db=db, produit=produit)


# GET /products : Lister tous les produits
@router.get("/", response_model=List[schemas.ProduitResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_produits(db, skip=skip, limit=limit)


# GET /products/{id} : Recuperer un produit par son ID
@router.get("/{produit_id}", response_model=schemas.ProduitResponse)
def read_product(produit_id: int, db: Session = Depends(get_db)):
    db_produit = crud.get_produit(db, produit_id=produit_id)
    if db_produit is None:
        raise HTTPException(status_code=404, detail="Produit non trouve")
    return db_produit


# PUT /products/{id} : Modifier un produit
@router.put("/{produit_id}", response_model=schemas.ProduitResponse)
def update_product(produit_id: int, produit: schemas.ProduitUpdate, db: Session = Depends(get_db)):
    db_produit = crud.update_produit(db, produit_id=produit_id, produit=produit)
    if db_produit is None:
        raise HTTPException(status_code=404, detail="Produit non trouve")
    return db_produit


# DELETE /products/{id} : Supprimer un produit
@router.delete("/{produit_id}", status_code=204)
def delete_product(produit_id: int, db: Session = Depends(get_db)):
    success = crud.delete_produit(db, produit_id=produit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Produit non trouve")