"""
ingest.py
---------
Script à lancer UNE FOIS pour :
- lire tous les fichiers CSV dans `data/`
- créer / mettre à jour une base vectorielle ChromaDB dans `chromadb_data/`

Pour l’instant, ce fichier est un squelette minimal à compléter selon ton schéma CSV.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv


BASE_DIR = Path(__file__).parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
CHROMA_DB_DIR = Path(os.getenv("CHROMA_DB_DIR", BASE_DIR / "chromadb_data"))


def get_client() -> chromadb.Client:
    CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    return client


def build_collection_name(name: str = "hospitals") -> str:
    return name


def ingest() -> None:
    """
    À compléter : lire tes CSV dans `DATA_DIR` et les insérer dans ChromaDB.

    Exemple de logique :
    - parcourir `DATA_DIR.glob("*.csv")`
    - pour chaque ligne, construire un texte (FR/AR) décrivant l’hôpital
    - ajouter dans la collection avec un id et des métadonnées
    """
    client = get_client()
    collection = client.get_or_create_collection(name=build_collection_name())

    # TODO: implémenter la lecture effective des CSV et l'insert dans `collection.add(...)`.
    print("Ingestion skeleton ready. Complète la fonction `ingest()` pour ton schéma CSV.")


if __name__ == "__main__":
    load_dotenv()
    ingest()
*** End Patch```}/>

