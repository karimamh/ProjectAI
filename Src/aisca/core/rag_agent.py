from core.semantic_engine import SemanticEngine
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
import unicodedata
import re


class RAGAgent:
    def __init__(self, competencies, jobs):
        self.competencies = competencies
        self.jobs = jobs
        self.semantic_engine = SemanticEngine()

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text.lower().strip()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = text.replace("’", "'")
        text = re.sub(r"\s+", " ", text)
        return text

    def analyze_user(self, user_input):
        """Analyse complète utilisateur avec scoring pondéré"""
        analysis_results = self.semantic_engine.analyze_user_input(user_input)
        top_jobs, job_scores = self.semantic_engine.get_top_jobs(analysis_results, self.jobs)
        block_scores = analysis_results["block_scores"]

        # Récupère les compétences requises des métiers recommandés
        mastered_raw = analysis_results["mastered"]
        mastered_norm = {self._normalize_text(c) for c in mastered_raw}

        required_competencies = []
        for job_title, _ in top_jobs:
            for job in self.jobs:
                if job["title"] == job_title:
                    for comp in job.get("required_competencies", []):
                        required_competencies.append(comp["competency"] if isinstance(comp, dict) else comp)

        required_norm = {self._normalize_text(c) for c in required_competencies}
        validated_in_top_jobs = sum(1 for comp in required_norm if comp in mastered_norm)
        required_total = len(required_norm)

        validated_ratio = (validated_in_top_jobs / required_total) if required_total > 0 else 0.0

        # Même logique que pour les métiers: 0 -> x1.00, 100% -> x1.35
        pertinence_multiplier = 1.0 + 0.35 * validated_ratio

        # Score de pertinence = meilleur score parmi le top 3 métiers
        global_score = top_jobs[0][1] if top_jobs else 0.0

        missing = [c for c in required_competencies if self._normalize_text(c) not in mastered_norm]
        missing = list(dict.fromkeys(missing))  # retire doublons en gardant l'ordre

        return {
            "block_scores": block_scores, 
            "global_score": global_score,
            "mastered": analysis_results['mastered'],
            "missing": missing,
            "top_jobs": top_jobs,
            "job_scores": job_scores
        }

    def needs_enrichment(self, user_input):
        """Vérifie si enrichissement API nécessaire (phrases < 5 mots)"""
        if isinstance(user_input, str):
            user_inputs = [user_input]
        else:
            user_inputs = user_input
        return any(len(text.split()) < 5 for text in user_inputs)
    
    def generate_llm_feedback(self, user_input, analysis):
        """Génère un feedback personnalisé avec Gemini Pro"""
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = (
            f"Profil utilisateur : {user_input}\n"
            f"Score global : {analysis['global_score']:.2f}\n"
            f"Compétences maîtrisées : {', '.join(analysis['mastered'])}\n"
            f"Compétences manquantes : {', '.join(analysis['missing'])}\n"
            f"Métiers recommandés : {', '.join([job for job, _ in analysis['top_jobs']])}\n"
            "Donne un résumé personnalisé et des conseils pour progresser."
        )
        response = model.generate_content(prompt)
        return response.text
