import json
import os
import pickle
import hashlib
from pathlib import Path

class Cache:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.embeddings_cache = self.cache_dir / 'embeddings.pkl'
        self.api_cache = self.cache_dir / 'api_responses.json'
        self.embeddings = self._load_embeddings()
        self.api_responses = self._load_api_cache()

    def _load_embeddings(self):
        """Charge le cache des embeddings"""
        if self.embeddings_cache.exists():
            with open(self.embeddings_cache, 'rb') as f:
                return pickle.load(f)
        return {}

    def _load_api_cache(self):
        """Charge le cache des réponses API"""
        if self.api_cache.exists():
            with open(self.api_cache, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_embeddings(self):
        """Sauvegarde les embeddings"""
        with open(self.embeddings_cache, 'wb') as f:
            pickle.dump(self.embeddings, f)

    def _save_api_cache(self):
        """Sauvegarde le cache API"""
        with open(self.api_cache, 'w', encoding='utf-8') as f:
            json.dump(self.api_responses, f, ensure_ascii=False, indent=2)

    def get_embedding(self, text_key):
        """Récupère un embedding depuis le cache"""
        return self.embeddings.get(text_key)

    def set_embedding(self, text_key, embedding):
        """Stocke un embedding dans le cache"""
        self.embeddings[text_key] = embedding
        self._save_embeddings()

    def get_api_response(self, prompt):
        """Récupère une réponse API depuis le cache"""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        return self.api_responses.get(prompt_hash)

    def set_api_response(self, prompt, response):
        """Stocke une réponse API dans le cache"""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        self.api_responses[prompt_hash] = response
        self._save_api_cache()

    def clear_all(self):
        """Vide tous les caches"""
        self.embeddings = {}
        self.api_responses = {}
        self._save_embeddings()
        self._save_api_cache()