import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import plotly.graph_objects as go
from core.rag_agent import RAGAgent
import json

# Configuration de la page
st.set_page_config(
    page_title="AISCA - Career Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS PERSONNALISÉ POUR LE LOOK ---
def local_css():
    st.markdown("""
    <style>
        /* Fond général plus doux */
        .stApp {
            background-color: #f8f9fa;
        }
        /* Style des cartes de métriques */
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e0e0e0;
            text-align: center;
        }
        /* Titres */
        h1, h2, h3 {
            font-family: 'Helvetica Neue', sans-serif;
            color: #2c3e50;
        }
        /* Zone de texte */
        .stTextArea textarea {
            border-radius: 10px;
            border: 1px solid #d1d5db;
        }
        /* Boutons */
        .stButton button {
            border-radius: 20px;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

def show_questionnaire():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🚀 AISCA")
        st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Votre assistant de carrière intelligent</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.info("💡 **Conseil :** Soyez précis sur vos outils, langages et réalisations pour une meilleure analyse.")
        
        user_input = st.text_area(
            "Décrivez votre parcours :",
            height=200,
            placeholder="Exemple : Je suis développeur Fullstack avec 3 ans d'expérience. Je maîtrise Python, Django et React. J'ai déployé des applications sur AWS et utilisé Docker..."
        )
        return user_input

def show_results(results, llm_feedback=None):
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>📊 Analyse de votre profil</h2>", unsafe_allow_html=True)
    st.write("") # Spacer

    # --- KPI CARDS ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🎯 Score de Pertinence", value=f"{results['global_score']:.1%}")
    with col2:
        st.metric(label="✅ Compétences Validées", value=len(results.get("mastered", [])))
    with col3:
        st.metric(label="📈 Potentiel d'évolution", value=len(results.get("missing", [])))

    st.write("") # Spacer

    # --- ONGLETS D'AFFICHAGE ---
    tab1, tab2, tab3 = st.tabs(["🏆 Métiers & Scores", "🔍 Détails Compétences", "🤖 Coach IA"])

    # ONGLET 1 : GRAPHIQUES
    with tab1:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Répartition par domaine")
            # Radar Chart amélioré
            radar_fig = go.Figure()
            radar_fig.add_trace(go.Scatterpolar(
                r=list(results["block_scores"].values()),
                theta=list(results["block_scores"].keys()),
                fill='toself',
                name='Score',
                line_color='#4F46E5',
                fillcolor='rgba(79, 70, 229, 0.2)'
            ))
            radar_fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 1], showticklabels=False),
                    bgcolor='#ffffff'
                ),
                margin=dict(l=40, r=40, t=40, b=40),
                showlegend=False,
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(radar_fig, use_container_width=True)

        with col_chart2:
            st.subheader("Top 3 Métiers recommandés")
            # Bar Chart amélioré
            jobs = [job for job, _ in results["top_jobs"]]
            scores = [score for _, score in results["top_jobs"]]
            
            bar_fig = go.Figure([go.Bar(
                x=scores,
                y=jobs,
                orientation='h',
                marker=dict(
                    color=scores,
                    colorscale='Viridis',
                    showscale=False
                ),
                text=[f"{s:.0%}" for s in scores],
                textposition='auto',
            )])
            bar_fig.update_layout(
                xaxis=dict(range=[0, 1], showgrid=False),
                yaxis=dict(autorange="reversed"),
                margin=dict(l=20, r=20, t=20, b=20),
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(bar_fig, use_container_width=True)

    # ONGLET 2 : LISTES
    with tab2:
        col_list1, col_list2 = st.columns(2)
        
        with col_list1:
            st.subheader("✅ Vos forces")
            if results.get("mastered"):
                for comp in results["mastered"]:
                    st.markdown(f"- {comp}")
            else:
                st.info("Continuez à décrire vos expériences pour détecter vos forces.")

        with col_list2:
            st.subheader("⚠️ À développer")
            if results.get("missing"):
                for comp in results["missing"]:
                    st.markdown(f"- {comp}")
            else:
                st.balloons()
                st.success("Excellent ! Votre profil couvre parfaitement les besoins.")

    # ONGLET 3 : FEEDBACK IA
    with tab3:
        st.subheader("🤖 L'avis de votre Coach IA")
        if llm_feedback:
            st.markdown(f"""
            <div style="background-color: #eef2ff; padding: 20px; border-radius: 10px; border-left: 5px solid #4F46E5;">
                {llm_feedback}
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("Analyse approfondie en cours par Gemini..."):
                st.empty()

# --- FONCTION PRINCIPALE ---
def main():
    # Charger les données
    with open('data/competences.json', 'r', encoding='utf-8') as f:
        competencies = json.load(f)
    with open('data/metiers.json', 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    # Initialiser le RAGAgent
    rag_agent = RAGAgent(competencies, jobs)
    
    # Afficher le questionnaire
    user_input = show_questionnaire()
    
    if user_input:
        # Centrage du bouton
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Analyser mon profil", use_container_width=True):
                # Analyser le profil
                results = rag_agent.analyze_user(user_input)
                
                # Générer le feedback IA si l'input est riche
                llm_feedback = None
                if not rag_agent.needs_enrichment(user_input):
                    llm_feedback = rag_agent.generate_llm_feedback(user_input, results)
                
                # Afficher les résultats
                show_results(results, llm_feedback)

if __name__ == "__main__":
    main()