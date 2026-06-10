"""
Página de Explicabilidade (XAI)

Exibe explicações LIME para as decisões do modelo.
"""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

st.set_page_config(page_title="XAI - Explicações", layout="wide")

API_URL = os.environ.get("API_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY")
try:
    API_KEY = st.secrets.get("api", {}).get("key") or API_KEY
except Exception:
    pass
API_HEADERS = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

st.title("🤖 Inteligência Artificial Explicável (XAI)")

# Input para análise
st.subheader("🔍 Analisar Texto")
texto_analise = st.text_area(
    "Digite ou cole um texto para análise:",
    height=150,
    placeholder="Digite aqui o texto da notícia para análise..."
)

if st.button("🔬 Analisar com XAI", type="primary"):
    if texto_analise:
        with st.spinner("Gerando explicação LIME..."):
            try:
                # Fazer predição
                predict_response = requests.post(
                    f"{API_URL}/predict",
                    json={"text": texto_analise},
                    headers=API_HEADERS
                )
                
                if predict_response.status_code == 200:
                    prediction = predict_response.json()
                    
                    # Gerar explicação
                    explain_response = requests.post(
                        f"{API_URL}/explain",
                        json={"text": texto_analise},
                        headers=API_HEADERS
                    )
                    
                    if explain_response.status_code == 200:
                        explanation = explain_response.json()
                        
                        # Exibir resultados
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            st.subheader("📊 Resultado da Predição")
                            
                            # Métrica principal
                            probabilidade = prediction['probabilidade'] * 100
                            cor = "red" if prediction['classe'] == 1 else "green"
                            
                            st.markdown(f"""
                            <div style='padding: 20px; background-color: {cor}20; border-radius: 10px; border-left: 5px solid {cor};'>
                                <h2 style='color: {cor};'>{prediction['classe_nome']}</h2>
                                <h3>Probabilidade: {probabilidade:.1f}%</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Features principais
                            st.subheader("🎯 Palavras-Chave")
                            
                            if explanation['features_positivas']:
                                st.markdown("**✅ Indicadores de Intolerância:**")
                                for feature in explanation['features_positivas'][:5]:
                                    st.markdown(f"- **{feature['palavra']}** (peso: {feature['peso']:.3f})")
                            
                            if explanation['features_negativas']:
                                st.markdown("**❌ Indicadores Contrários:**")
                                for feature in explanation['features_negativas'][:5]:
                                    st.markdown(f"- **{feature['palavra']}** (peso: {feature['peso']:.3f})")
                        
                        with col2:
                            st.subheader("📈 Visualização LIME")
                            
                            # Gráfico de barras com features
                            all_features = (
                                explanation['features_positivas'] + 
                                explanation['features_negativas']
                            )
                            
                            if all_features:
                                df_features = pd.DataFrame(all_features)
                                df_features = df_features.sort_values('peso', ascending=True)
                                
                                # Criar gráfico de barras horizontal
                                fig = go.Figure()
                                
                                # Cores baseadas no peso
                                colors = ['red' if x > 0 else 'blue' for x in df_features['peso']]
                                
                                fig.add_trace(go.Bar(
                                    y=df_features['palavra'],
                                    x=df_features['peso'],
                                    orientation='h',
                                    marker_color=colors,
                                    text=[f"{x:.3f}" for x in df_features['peso']],
                                    textposition='outside'
                                ))
                                
                                fig.update_layout(
                                    title="Importância das Palavras (LIME)",
                                    xaxis_title="Peso da Feature",
                                    yaxis_title="Palavra/Frase",
                                    height=400,
                                    showlegend=False
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # Explicação detalhada
                            st.subheader("💡 Interpretação")
                            st.markdown("""
                            **Como interpretar:**
                            - **Barras vermelhas (positivas):** Palavras que aumentam a probabilidade de intolerância
                            - **Barras azuis (negativas):** Palavras que diminuem a probabilidade de intolerância
                            - **Peso:** Magnitude da influência na decisão do modelo
                            
                            O LIME (Local Interpretable Model-agnostic Explanations) cria 
                            variações do texto original e observa como as predições mudam, 
                            identificando quais palavras são mais influentes na decisão final.
                            """)
                        
                    else:
                        st.error("Erro ao gerar explicação LIME.")
                else:
                    st.error("Erro ao realizar predição.")
                    
            except Exception as e:
                st.error(f"Erro na análise: {str(e)}")
    else:
        st.warning("Por favor, digite um texto para análise.")

# Histórico de análises
st.markdown("---")
st.subheader("📚 Histórico de Análises Recentes")

try:
    response = requests.get(f"{API_URL}/news", params={"limit": 5, "classe": 1})
    if response.status_code == 200:
        recent_news = response.json()
        
        if recent_news['noticias']:
            for news in recent_news['noticias']:
                with st.expander(f"📰 {news['titulo'][:100]}... - {news['probabilidade']:.1%}"):
                    st.markdown(f"**Texto:** {news['texto'][:300]}...")
                    if news.get('explicacao_lime'):
                        st.info("Explicação LIME disponível. Selecione o texto acima para análise detalhada.")
                        
except:
    st.info("Histórico de análises não disponível no momento.")