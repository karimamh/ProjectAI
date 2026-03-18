import streamlit as st
from core.rag_agent import RAGAgent
import json
from ui.ui_streamlit import show_questionnaire, show_results, show_job_competency_checkboxes
import os

def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    with open(os.path.join(data_dir, 'competences.json'), 'r', encoding='utf-8') as f:
        competences = json.load(f)
    with open(os.path.join(data_dir, 'metiers.json'), 'r', encoding='utf-8') as f:
        metiers = json.load(f)
    return competences, metiers

def main():
    st.title("AISCA - Mini-Agent RAG")
    competences, metiers = load_data()
    rag_agent = RAGAgent(competences, metiers)

    user_input = show_questionnaire()
    selected_competencies = show_job_competency_checkboxes(metiers)
    if st.button("Analyser"):
        merged_input = []
        if user_input and user_input.strip():
            merged_input.append(user_input.strip())
        merged_input.extend(selected_competencies)

        if merged_input:
            results = rag_agent.analyze_user(merged_input)
            llm_feedback = rag_agent.generate_llm_feedback(merged_input, results)
            show_results(results, llm_feedback)
        else:
            st.warning("Veuillez entrer vos compétences.")

if __name__ == "__main__":
    main()