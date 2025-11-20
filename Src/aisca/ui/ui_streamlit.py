import streamlit as st
import plotly.graph_objects as go

def show_questionnaire():
    st.title("AISCA - Questionnaire compétences")
    user_input = st.text_area("Décrivez vos compétences et expériences (texte libre):")
    return user_input

def show_results(results):
    st.header("Résultats de l'analyse sémantique")

    st.subheader("Score par bloc de compétences")
    st.write(results["block_scores"])

    st.subheader("Score global")
    st.write(f"{results['global_score']:.2f}")

    st.subheader("Top 3 métiers recommandés")
    for job, score in results["top_jobs"]:
        st.write(f"{job} : {score:.2f}")

    st.subheader("Compétences maîtrisées")
    st.write(results["mastered"])

    st.subheader("Compétences à renforcer")
    st.write(results["missing"])

    # Radar par bloc
    st.subheader("Visualisation radar (blocs de compétences)")
    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(
        r=list(results["block_scores"].values()),
        theta=list(results["block_scores"].keys()),
        fill='toself',
        name='Score par bloc'
    ))
    radar_fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1])), showlegend=False)
    st.plotly_chart(radar_fig)

    # Barres métiers
    st.subheader("Visualisation barres (métiers recommandés)")
    bar_fig = go.Figure([go.Bar(
        x=[job for job, _ in results["top_jobs"]],
        y=[score for _, score in results["top_jobs"]],
        marker_color='indigo'
    )])
    bar_fig.update_layout(yaxis=dict(range=[0,1]))
    st.plotly_chart(bar_fig)