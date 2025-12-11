from core.semantic_engine import SemanticEngine
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os


class RAGAgent:
    def __init__(self, competencies, jobs):
        self.competencies = competencies
        self.jobs = jobs
        self.semantic_engine = SemanticEngine()

    def analyze_user(self, user_input):
        """Analyse complète utilisateur avec scoring pondéré"""
        analysis_results = self.semantic_engine.analyze_user_input(user_input)
        top_jobs, job_scores = self.semantic_engine.get_top_jobs(analysis_results, self.jobs)
        block_scores = analysis_results['block_scores']
        global_score = sum(block_scores.values()) / len(block_scores) if block_scores else 0

        # Récupère les compétences requises des métiers recommandés
        required_competencies = set()
        for job_title, _ in top_jobs:
            for job in self.jobs:
                if job['title'] == job_title:
                    for comp in job.get('required_competencies', []):
                        if isinstance(comp, dict):
                            required_competencies.add(comp['competency'])
                        elif isinstance(comp, str):
                            required_competencies.add(comp)

        # Compétences à renforcer = requises par les métiers recommandés et non maîtrisées
        mastered = set(analysis_results['mastered'])
        missing = list(required_competencies - mastered)

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
