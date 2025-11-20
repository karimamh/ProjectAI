from sentence_transformers import SentenceTransformer
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
from utils.cache import Cache

class SemanticEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.cache = Cache()
        self.competencies = self.load_competencies()
        self.competency_embeddings = self._precompute_competency_embeddings()

    def load_competencies(self):
        with open('data/competences.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def _precompute_competency_embeddings(self):
        """Encode et cache tous les embeddings du référentiel"""
        embeddings_dict = {}
        
        for block in self.competencies:
            block_id = block['block_id']
            cache_key = f"block_{block_id}"
            
            cached_embeddings = self.cache.get_embedding(cache_key)
            if cached_embeddings is not None:
                embeddings_dict[block_id] = cached_embeddings
            else:
                competencies = block['competencies']
                embeddings = self.model.encode(competencies, convert_to_tensor=False)
                embeddings_dict[block_id] = embeddings
                self.cache.set_embedding(cache_key, embeddings)
        
        return embeddings_dict

    def encode_texts(self, texts):
        """Encode des textes"""
        return self.model.encode(texts, convert_to_tensor=False)

    def calculate_cosine_similarity(self, embeddings1, embeddings2):
        """Calcule la similarité cosinus normalisée"""
        return cosine_similarity(embeddings1, embeddings2)

    def analyze_user_input(self, user_input):
        """Analyse complète de l'input utilisateur"""
        if isinstance(user_input, str):
            user_inputs = [user_input]
        else:
            user_inputs = user_input

        user_embeddings = self.encode_texts(user_inputs)
        
        block_scores = {}
        mastered = []
        missing = []

        for block in self.competencies:
            block_id = block['block_id']
            comp_texts = block['competencies']
            comp_embeddings = self.competency_embeddings[block_id]

            scores = self.calculate_cosine_similarity(user_embeddings, comp_embeddings)
            
            # Max par compétence
            comp_max_scores = scores.max(axis=0)
            
            # Score du bloc = moyenne des scores des compétences
            block_score = float(np.mean(comp_max_scores))
            block_scores[block_id] = block_score

            # Compétences maîtrisées/manquantes
            for idx, comp_score in enumerate(comp_max_scores):
                if comp_score >= 0.5:
                    mastered.append(comp_texts[idx])
                else:
                    missing.append(comp_texts[idx])

        return {
            "block_scores": block_scores,
            "mastered": mastered,
            "missing": missing,
            "user_embeddings": user_embeddings
        }

    def get_top_jobs(self, analysis_results, jobs_data):
        """Calcule le top 3 métiers avec pondération"""
        block_scores = analysis_results['block_scores']
        user_embeddings = analysis_results['user_embeddings']
        job_scores = {}
        
        for job in jobs_data:
            required_blocks = job['required_blocks']
            required_comps = job.get('required_competencies', [])
            
            # Score blocs (20%)
            if required_blocks:
                block_score = np.mean([block_scores.get(bid, 0) for bid in required_blocks])
            else:
                block_score = 0
            
            # Score compétences pondéré (80%)
            if required_comps:
                total_weight = 0
                weighted_score = 0
                
                for comp_data in required_comps:
                    comp_text = comp_data['competency']
                    weight = comp_data['weight']
                    
                    comp_embedding = self.model.encode([comp_text], convert_to_tensor=False)
                    similarity = self.calculate_cosine_similarity(user_embeddings, comp_embedding)
                    max_sim = float(similarity.max())
                    
                    weighted_score += max_sim * weight
                    total_weight += weight
                
                comp_score = weighted_score / total_weight if total_weight > 0 else 0
            else:
                comp_score = 0
            
            final_score = 0.2 * block_score + 0.8 * comp_score
            job_scores[job['title']] = float(final_score)

        top_jobs = sorted(job_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        return top_jobs, job_scores