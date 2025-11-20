import streamlit as st
from core.semantic_engine import SemanticEngine
from core.rag_agent import RAGAgent
import json
from ui.ui_streamlit import show_questionnaire, show_results

def load_data():
    with open('data/competences.json', 'r', encoding='utf-8') as f:
        competences = json.load(f)
    with open('data/metiers.json', 'r', encoding='utf-8') as f:
        metiers = json.load(f)
    return competences, metiers

def main():
    st.title("AISCA - Mini-Agent RAG")
    competences, metiers = load_data()
    # Ne pas passer semantic_engine ici
    rag_agent = RAGAgent(competences, metiers)

    user_input = show_questionnaire()
    if st.button("Analyser"):
        if user_input:
            results = rag_agent.analyze_user(user_input)
            show_results(results)
        else:
            st.warning("Veuillez entrer vos compétences.")

if __name__ == "__main__":
    main()