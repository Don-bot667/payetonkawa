from fastapi import FastAPI
from .database import engine, Base
from .routes import router

# Création automatique des tables au démarrage (pour le dev)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PayeTonKawa - API Clients",
    version="1.0.0"
)

# Inclusion des routes définies précédemment
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Clients de PayeTonKawa"}