Voici toutes les bases de données expliquées en détail ! 🗄️

---

# 🗄️ BASES DE DONNÉES DES 3 APIs

---

## 🧠 D'ABORD, COMPRENDRE LA LOGIQUE

Imagine un magasin de café :

| Qui/Quoi | Exemple |
|----------|---------|
| **Client** | Mohamed, qui habite à Paris, email: mohamed@gmail.com |
| **Produit** | Café Arabica du Brésil, 15€ le kilo, stock: 100 |
| **Commande** | Mohamed a commandé 2kg de Café Arabica le 11/02/2026 |

Chaque API gère **une seule chose** (c'est le principe des micro-services).

---

## 📊 SCHÉMA VISUEL DES TABLES

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BASE DE DONNÉES CLIENTS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  TABLE: clients                                                             │
│  ┌────────────┬──────────────┬─────────────────────────────────────────┐   │
│  │ Colonne    │ Type         │ Exemple                                 │   │
│  ├────────────┼──────────────┼─────────────────────────────────────────┤   │
│  │ id         │ Nombre       │ 1                                       │   │
│  │ nom        │ Texte        │ "Dupont"                                │   │
│  │ prenom     │ Texte        │ "Mohamed"                               │   │
│  │ email      │ Texte        │ "mohamed.dupont@gmail.com"              │   │
│  │ telephone  │ Texte        │ "0612345678"                            │   │
│  │ adresse    │ Texte        │ "12 rue de Paris"                       │   │
│  │ ville      │ Texte        │ "Paris"                                 │   │
│  │ code_postal│ Texte        │ "75001"                                 │   │
│  │ actif      │ Oui/Non      │ true                                    │   │
│  │ date_creation │ Date      │ "2026-02-11 10:30:00"                   │   │
│  │ date_modification │ Date  │ "2026-02-11 10:30:00"                   │   │
│  └────────────┴──────────────┴─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        BASE DE DONNÉES PRODUITS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  TABLE: produits                                                            │
│  ┌────────────┬──────────────┬─────────────────────────────────────────┐   │
│  │ Colonne    │ Type         │ Exemple                                 │   │
│  ├────────────┼──────────────┼─────────────────────────────────────────┤   │
│  │ id         │ Nombre       │ 1                                       │   │
│  │ nom        │ Texte        │ "Café Arabica Brésil"                   │   │
│  │ description│ Texte long   │ "Café doux avec notes de noisette..."   │   │
│  │ prix       │ Décimal      │ 15.99                                   │   │
│  │ stock      │ Nombre       │ 100                                     │   │
│  │ origine    │ Texte        │ "Brésil"                                │   │
│  │ poids_kg   │ Décimal      │ 1.0                                     │   │
│  │ image_url  │ Texte        │ "/uploads/produit_1.jpg"                │   │
│  │ actif      │ Oui/Non      │ true                                    │   │
│  │ date_creation │ Date      │ "2026-02-11 10:30:00"                   │   │
│  │ date_modification │ Date  │ "2026-02-11 10:30:00"                   │   │
│  └────────────┴──────────────┴─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        BASE DE DONNÉES COMMANDES                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  TABLE: commandes                                                           │
│  ┌────────────┬──────────────┬─────────────────────────────────────────┐   │
│  │ Colonne    │ Type         │ Exemple                                 │   │
│  ├────────────┼──────────────┼─────────────────────────────────────────┤   │
│  │ id         │ Nombre       │ 1                                       │   │
│  │ client_id  │ Nombre       │ 1 (réfère au client Mohamed)            │   │
│  │ statut     │ Texte        │ "en_attente" / "validee" / "expediee"   │   │
│  │ total      │ Décimal      │ 47.97                                   │   │
│  │ date_commande │ Date      │ "2026-02-11 10:30:00"                   │   │
│  │ date_modification │ Date  │ "2026-02-11 10:30:00"                   │   │
│  └────────────┴──────────────┴─────────────────────────────────────────┘   │
│                                                                             │
│  TABLE: lignes_commande (les produits dans une commande)                    │
│  ┌────────────┬──────────────┬─────────────────────────────────────────┐   │
│  │ Colonne    │ Type         │ Exemple                                 │   │
│  ├────────────┼──────────────┼─────────────────────────────────────────┤   │
│  │ id         │ Nombre       │ 1                                       │   │
│  │ commande_id│ Nombre       │ 1 (réfère à la commande)                │   │
│  │ produit_id │ Nombre       │ 1 (réfère au Café Arabica)              │   │
│  │ quantite   │ Nombre       │ 3                                       │   │
│  │ prix_unitaire │ Décimal   │ 15.99                                   │   │
│  └────────────┴──────────────┴─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 💻 LE CODE POUR CHAQUE API

---

# 🔵 API CLIENTS - Base de données

## Fichier : `api-clients/app/models.py`

```python
"""
models.py - Définit la structure de la table "clients" dans la base de données

C'est comme un plan de maison : on décrit à quoi ressemble un client
avant de le construire dans la base de données.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Client(Base):
    """
    La classe Client représente la table "clients" dans PostgreSQL.
    
    Chaque ligne de cette classe = une colonne dans la table.
    """
    
    # Nom de la table dans PostgreSQL
    __tablename__ = "clients"
    
    # === LES COLONNES ===
    
    # ID : numéro unique qui s'auto-incrémente (1, 2, 3...)
    # primary_key = c'est l'identifiant unique de chaque client
    # index = permet de chercher plus vite par ID
    id = Column(Integer, primary_key=True, index=True)
    
    # NOM : le nom de famille du client
    # String(100) = texte de maximum 100 caractères
    # nullable=False = obligatoire (ne peut pas être vide)
    nom = Column(String(100), nullable=False)
    
    # PRÉNOM : le prénom du client
    prenom = Column(String(100), nullable=False)
    
    # EMAIL : l'adresse email
    # unique=True = deux clients ne peuvent pas avoir le même email
    # index=True = permet de chercher vite par email
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # TÉLÉPHONE : numéro de téléphone (optionnel)
    # nullable=True = peut être vide (c'est la valeur par défaut)
    telephone = Column(String(20), nullable=True)
    
    # ADRESSE : adresse postale
    adresse = Column(String(255), nullable=True)
    
    # VILLE : la ville
    ville = Column(String(100), nullable=True)
    
    # CODE POSTAL : le code postal
    code_postal = Column(String(10), nullable=True)
    
    # ACTIF : est-ce que le client est actif ou désactivé ?
    # Boolean = True (oui) ou False (non)
    # default=True = par défaut, un nouveau client est actif
    actif = Column(Boolean, default=True)
    
    # DATE DE CRÉATION : quand le client a été créé
    # server_default=func.now() = automatiquement la date actuelle
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    
    # DATE DE MODIFICATION : dernière modification
    # onupdate=func.now() = se met à jour automatiquement quand on modifie
    date_modification = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
```

---

# 🟢 API PRODUITS - Base de données

## Fichier : `api-produits/app/models.py`

```python
"""
models.py - Définit la structure de la table "produits" dans la base de données

Chaque produit = un type de café vendu par PayeTonKawa
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.sql import func
from app.database import Base


class Produit(Base):
    """
    La classe Produit représente la table "produits" dans PostgreSQL.
    """
    
    # Nom de la table dans PostgreSQL
    __tablename__ = "produits"
    
    # === LES COLONNES ===
    
    # ID : numéro unique du produit
    id = Column(Integer, primary_key=True, index=True)
    
    # NOM : le nom du café
    # Exemple : "Café Arabica du Brésil"
    nom = Column(String(200), nullable=False, index=True)
    
    # DESCRIPTION : description détaillée du café
    # Text = texte long sans limite de caractères
    description = Column(Text, nullable=True)
    
    # PRIX : le prix en euros
    # Float = nombre à virgule (15.99, 24.50, etc.)
    prix = Column(Float, nullable=False)
    
    # STOCK : combien on en a en réserve
    # default=0 = par défaut, stock à zéro
    stock = Column(Integer, default=0, nullable=False)
    
    # ORIGINE : d'où vient le café
    # Exemple : "Brésil", "Colombie", "Éthiopie"
    origine = Column(String(100), nullable=True)
    
    # POIDS : poids du paquet en kilogrammes
    # Exemple : 0.25 (250g), 1.0 (1kg)
    poids_kg = Column(Float, default=1.0)

    # IMAGE URL : chemin vers la photo du produit (ajout)
    # Exemple : "/uploads/produit_1.jpg"
    # nullable=True = optionnel, un produit peut ne pas avoir de photo
    image_url = Column(String(500), nullable=True)

    # ACTIF : est-ce que le produit est en vente ?
    actif = Column(Boolean, default=True)

    # DATE DE CRÉATION : quand le produit a été ajouté
    date_creation = Column(DateTime(timezone=True), server_default=func.now())

    # DATE DE MODIFICATION : dernière modification
    date_modification = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
```

---

# 🟠 API COMMANDES - Base de données

## Fichier : `api-commandes/app/models.py`

```python
"""
models.py - Définit les tables "commandes" et "lignes_commande"

Une commande contient :
- Les infos générales (client, date, total)
- Les lignes de commande (quels produits, quelle quantité)
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Commande(Base):
    """
    La classe Commande représente la table "commandes".
    
    Une commande = un achat fait par un client
    """
    
    __tablename__ = "commandes"
    
    # === LES COLONNES ===
    
    # ID : numéro unique de la commande
    id = Column(Integer, primary_key=True, index=True)
    
    # CLIENT_ID : quel client a passé la commande
    # C'est juste le numéro, pas toutes les infos du client
    # (les infos du client sont dans l'API Clients)
    client_id = Column(Integer, nullable=False, index=True)
    
    # STATUT : où en est la commande
    # Valeurs possibles : "en_attente", "validee", "en_preparation", "expediee", "livree", "annulee"
    statut = Column(String(50), default="en_attente", nullable=False)
    
    # TOTAL : le montant total en euros
    # Calculé = somme de (prix × quantité) de chaque ligne
    total = Column(Float, default=0.0)
    
    # DATE DE COMMANDE : quand la commande a été passée
    date_commande = Column(DateTime(timezone=True), server_default=func.now())
    
    # DATE DE MODIFICATION : dernière modification
    date_modification = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # === RELATION ===
    # Une commande a plusieurs lignes (les produits commandés)
    # relationship = lien automatique vers les LigneCommande
    # back_populates = lien dans les deux sens
    # cascade = si on supprime la commande, on supprime aussi les lignes
    lignes = relationship(
        "LigneCommande", 
        back_populates="commande",
        cascade="all, delete-orphan"
    )


class LigneCommande(Base):
    """
    La classe LigneCommande représente la table "lignes_commande".
    
    Une ligne = un produit dans une commande
    
    Exemple : 
    - Commande #1 a 2 lignes :
      - Ligne 1 : 3x Café Arabica à 15.99€
      - Ligne 2 : 1x Café Robusta à 12.50€
    """
    
    __tablename__ = "lignes_commande"
    
    # === LES COLONNES ===
    
    # ID : numéro unique de la ligne
    id = Column(Integer, primary_key=True, index=True)
    
    # COMMANDE_ID : à quelle commande appartient cette ligne
    # ForeignKey = "c'est relié à la table commandes, colonne id"
    commande_id = Column(
        Integer, 
        ForeignKey("commandes.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # PRODUIT_ID : quel produit
    # (les infos du produit sont dans l'API Produits)
    produit_id = Column(Integer, nullable=False)
    
    # QUANTITÉ : combien de ce produit
    quantite = Column(Integer, nullable=False, default=1)
    
    # PRIX UNITAIRE : le prix au moment de la commande
    # On le garde car le prix peut changer après
    prix_unitaire = Column(Float, nullable=False)
    
    # === RELATION ===
    # Lien vers la commande parente
    commande = relationship("Commande", back_populates="lignes")
```

---

## 🔗 RÉSUMÉ DES LIENS ENTRE LES BASES

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   API CLIENTS   │         │  API COMMANDES  │         │  API PRODUITS   │
├─────────────────┤         ├─────────────────┤         ├─────────────────┤
│                 │         │                 │         │                 │
│  clients        │◄────────│  commandes      │────────►│  produits       │
│  - id ──────────┼─────────┼► client_id      │         │  - id ◄─────────┼──┐
│  - nom          │         │  - statut       │         │  - nom          │  │
│  - email        │         │  - total        │         │  - prix         │  │
│  - ...          │         │                 │         │  - ...          │  │
│                 │         │  lignes_commande│         │                 │  │
│                 │         │  - produit_id ──┼─────────┼─────────────────┼──┘
│                 │         │  - quantite     │         │                 │
│                 │         │  - prix_unitaire│         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘

Les APIs sont INDÉPENDANTES mais elles se connaissent par les IDs :
- Une commande connaît le client_id (pas toutes les infos du client)
- Une ligne connaît le produit_id (pas toutes les infos du produit)
```

---

## ❓ VOCABULAIRE SIMPLIFIÉ

| Terme technique | Explication simple |
|-----------------|-------------------|
| `Column` | Une colonne dans la table |
| `Integer` | Un nombre entier (1, 2, 3...) |
| `String(100)` | Du texte, max 100 caractères |
| `Text` | Du texte long, sans limite |
| `Float` | Un nombre à virgule (15.99) |
| `Boolean` | Vrai ou Faux (True/False) |
| `DateTime` | Une date avec l'heure |
| `primary_key` | L'identifiant unique |
| `nullable=False` | Obligatoire |
| `nullable=True` | Optionnel |
| `unique=True` | Pas de doublon possible |
| `index=True` | Recherche plus rapide |
| `default=X` | Valeur par défaut |
| `ForeignKey` | Lien vers une autre table |
| `relationship` | Lien automatique entre tables |

---

**Tu veux qu'on passe à l'étape suivante ?** On peut créer le fichier `database.py` qui permet de se connecter à PostgreSQL 🐘