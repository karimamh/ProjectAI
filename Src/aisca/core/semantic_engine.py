from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from utils.cache import Cache
import json
import os
import numpy as np
import unicodedata
import re

class SemanticEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name, device="cpu")
        self.cache = Cache()
        self.competencies = self.load_competencies()
        self.competency_embeddings = self._precompute_competency_embeddings()

    def load_competencies(self):
        # Obtenir le chemin absolu vers le fichier
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, '..', 'data', 'competences.json')
        
        with open(data_path, 'r', encoding='utf-8') as f:
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
    
    
  
    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text.lower().strip()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = text.replace("’", "'")
        text = re.sub(r"\s+", " ", text)
        return text

    # Calibrage de la similarité pour mieux différencier les scores (le high n est pas utile mais le low et toujours utilisé pour éviter les faux positifs)
    @staticmethod
    def _calibrate_similarity(sim: float, low: float = 0.32, high: float = 0.70) -> float:
        return float(np.clip((sim - low) / (high - low), 0.0, 1.0))
    
    def analyze_user_input(self, user_input):
        if isinstance(user_input, str):
            chunks = [
                s.strip()
                for s in re.split(r"[.\n;!?]+", user_input)
                if len(s.strip().split()) >= 3
            ]
            user_inputs = chunks if chunks else [user_input]
        else:
            user_inputs = user_input

        user_embeddings = self.encode_texts(user_inputs)

        block_scores = {}
        block_scores_by_id = {}
        mastered = []
        missing = []
        competency_scores = {}  

        for block in self.competencies:
            block_id = block.get("block_id")
            block_name = block.get("block_name", f"Bloc {block_id}")
            comp_texts = block.get("competencies", [])
            if not comp_texts:
                continue

            comp_embeddings = self.competency_embeddings.get(block_id)
            if comp_embeddings is None or len(comp_embeddings) == 0:
                continue

            sims = self.calculate_cosine_similarity(user_embeddings, comp_embeddings)
            comp_max_scores = sims.max(axis=0)

            # Score bloc plus robuste: moyenne du top 40% (au moins 3 compétences)
            cal_scores = np.array([self._calibrate_similarity(float(s)) for s in comp_max_scores])
            k = max(4, int(np.ceil(len(cal_scores) * 0.5)))
            depth = float(np.mean(np.sort(cal_scores)[-k:]))
            coverage = float(np.mean(cal_scores >= 0.65))
            block_score = 0.65 * depth + 0.35 * coverage

            block_scores[block_name] = block_score
            block_scores_by_id[block_id] = block_score

            for idx, comp_score in enumerate(comp_max_scores):
                comp = comp_texts[idx]
                competency_scores[self._normalize_text(comp)] = float(comp_score)
                calibrated = self._calibrate_similarity(float(comp_score))
                if calibrated >= 0.60:
                    mastered.append(comp)
                elif calibrated < 0.30:
                    missing.append(comp)

        return {
            "block_scores": block_scores,
            "block_scores_by_id": block_scores_by_id,
            "competency_scores": competency_scores,
            "mastered": mastered,
            "missing": missing,
            "user_embeddings": user_embeddings
        }
    def get_top_jobs(self, analysis_results, jobs_data):
      
        block_scores_by_id = analysis_results.get("block_scores_by_id", {})
        competency_scores = analysis_results.get("competency_scores", {})
        user_embeddings = analysis_results["user_embeddings"]

        job_scores = {}

        for job in jobs_data:
            required_blocks = job.get("required_blocks", [])
            required_comps = job.get("required_competencies", [])

            # Bloc: map correct par ID
            block_score = float(np.mean([block_scores_by_id.get(bid, 0.0) for bid in required_blocks])) if required_blocks else 0.0

            # Compétences pondérées
            weighted_sum = 0.0
            total_weight = 0.0
            covered_weight = 0.0
            validated_count = 0
            required_count = len(required_comps)

            for comp_data in required_comps:
                if isinstance(comp_data, dict):
                    comp_text = comp_data.get("competency", "")
                    weight = float(comp_data.get("weight", 1.0))
                else:
                    comp_text = str(comp_data)
                    weight = 1.0

                key = self._normalize_text(comp_text)
                if key in competency_scores:
                    sim = competency_scores[key]
                else:
                    # fallback embedding si compétence non alignée avec référentiel
                    emb = self.model.encode([comp_text], convert_to_tensor=False)
                    sim = float(self.calculate_cosine_similarity(user_embeddings, emb).max())

                sim_cal = self._calibrate_similarity(float(sim))
                weighted_sum += sim_cal * weight
                total_weight += weight

                if sim_cal >= 0.65:
                    covered_weight += weight
                    validated_count += 1

            comp_score = (weighted_sum / total_weight) if total_weight > 0 else 0.0
            coverage_ratio = (covered_weight / total_weight) if total_weight > 0 else 0.0
            validated_ratio = (validated_count / required_count) if required_count > 0 else 0.0

            # Score de base
            base_score = 0.30 * block_score + 0.70 * comp_score
            validated_multiplier = 1.0 + 0.25 * validated_ratio
            coverage_penalty = (1 - 0.25 * (1 - coverage_ratio))

            final_score = min(1.0, base_score * validated_multiplier * coverage_penalty)
            job_scores[job["title"]] = float(final_score)

        top_jobs = sorted(job_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        return top_jobs, job_scores

    