from core.semantic_engine import SemanticEngine
import json

class RAGAgent:
    def __init__(self, competencies, jobs):
        self.competencies = competencies
        self.jobs = jobs
        self.semantic_engine = SemanticEngine()

    def analyze_user(self, user_input):
        """Analyse complète utilisateur avec scoring pondéré"""
        # 1. Analyse sémantique via semantic_engine
        analysis_results = self.semantic_engine.analyze_user_input(user_input)
        
        # 2. Top 3 métiers avec pondération (utilise get_top_jobs du semantic_engine)
        top_jobs, job_scores = self.semantic_engine.get_top_jobs(analysis_results, self.jobs)
        
        # 3. Score global
        block_scores = analysis_results['block_scores']
        global_score = sum(block_scores.values()) / len(block_scores) if block_scores else 0
        
        return {
            "block_scores": block_scores,
            "global_score": global_score,
            "mastered": analysis_results['mastered'],
            "missing": analysis_results['missing'],
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