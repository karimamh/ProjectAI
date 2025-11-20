---
applyTo: '**'
---
🎯 Objectif du projet

Développer AISCA, un mini-agent RAG spécialisé dans :

l’analyse sémantique de compétences utilisateurs,

le scoring des correspondances avec un référentiel,

la recommandation de métiers technologiques,

et la génération d’un plan de progression + bio professionnelle (IA générative).

Le projet doit utiliser :

Embeddings SBERT (local, pas d’API)

Similarité cosinus

Une architecture RAG simplifiée

Streamlit pour l’interface

Un usage minimal d’API (Gemini ou OpenAI free-tier)

📌 Structure DATA déjà fournie

Deux fichiers JSON servent de base :

1. competences.json

Contient 8 blocs de compétences tech (Dev, Web, Data, ML, IA/NLP, Cloud, Cybersécurité, Gestion de projet).
Chaque bloc contient 6 compétences rédigées en français, sous forme de phrases structurées pour SBERT.

Format :

[
  {
    "block_id": 1,
    "block_name": "Développement logiciel",
    "competencies": [
      "concevoir des architectures logicielles orientées objet",
      ...
    ]
  }
]

2. metiers.json

Contient 12 métiers tech, chacun avec :

un job_id

un title

une liste de required_blocks

une liste de required_competencies

Format :

[
  {
    "job_id": "J01",
    "title": "Développeur logiciel",
    "required_blocks": [1],
    "required_competencies": [
      "concevoir des architectures logicielles orientées objet",
      ...
    ]
  }
]

🧠 Fonctionnement attendu du moteur sémantique
1. Chargement SBERT local

Modèle :

all-MiniLM-L6-v2

2. Pipeline d’analyse

Encoder toutes les réponses utilisateur (texte libre)

Encoder toutes les compétences du référentiel

Calculer la similarité cosinus

Pour chaque bloc :

récupérer le score max pour chaque phrase utilisateur

calculer la moyenne → score du bloc

Générer un score global (moyenne pondérée des blocs)

Calculer score par métier

Retourner top 3 métiers

🧩 RAG minimal à implémenter
Retrieval

filtrer les compétences les mieux associées à l’utilisateur

identifier les faiblesses (scores faibles)

sélectionner données pertinentes pour la génération

Augmentation

si une phrase utilisateur fait < 5 mots → enrichissement via API LLM

construire un prompt contenant :

résultats de similarité

compétences maîtrisées

compétences manquantes

métiers recommandés

Generation (1 seul appel)

produire un plan de progression

produire une bio professionnelle

🖥️ Interface Streamlit attendue

Pages :

Questionnaire (Likert + texte libre)

Résultats

Visualisations :

radar par bloc

barres par métier recommandé

Bio & plan généré

🧪 Composants techniques que Copilot doit aider à générer

Loader des JSON

Encoder les textes avec SBERT

Fonction de similarité cosinus

Calcul du score de bloc

Calcul du score métier

Retour top 3 métiers

Vérification longueur des phrases + appel API conditionnel

Prompt unique pour la génération

Interface Streamlit propre et modulaire

Graphiques radar (matplotlib ou plotly)

Fichiers utilitaires :

semantic_engine.py

rag_agent.py

ui_streamlit.py

config.py

✔️ Résultats finaux affichés à l’utilisateur

Score par bloc de compétences

Score par métier

Top 3 métiers conseillés

Écart entre compétences maîtrisées / manquantes

Bio professionnelle générée

Plan de progression généré

🔒 Contraintes à respecter

SBERT local obligatoire

Appels API limités

1 appel pour l’enrichissement (si nécessaire)

1 appel pour la bio + plan

Pas d’appels répétés inutiles → prévoir un cache local

Architecture claire et modulable