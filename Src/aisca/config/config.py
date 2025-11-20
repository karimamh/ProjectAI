import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
CACHE_DIR = BASE_DIR / 'cache'

# Fichiers de données
COMPETENCES_FILE = DATA_DIR / 'competences.json'
METIERS_FILE = DATA_DIR / 'metiers.json'

# Paramètres SBERT
SBERT_MODEL = 'all-MiniLM-L6-v2'
SIMILARITY_THRESHOLD = 0.5

# Cache
ENABLE_CACHE = True
CACHE_EMBEDDINGS = True
CACHE_API_RESPONSES = True

# API (pour génération future)
API_PROVIDER = 'gemini'  # ou 'openai'
API_MAX_RETRIES = 3