"""
Página de Alertas

Exibe alertas de alta probabilidade de intolerância religiosa.
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Alertas", layout="wide")

API_URL = "http://localhost:8000"

st.title("🚨 Alertas de Intolerância")

# Carregar alertas
try:
    response = requests.get(f"{API_URL}/alerts")
    if response.status_code == 200:
        alertas_data = response.json()
    else:
        alertas_data = None
except:
    alertas_data = None
    st.error("Não foi possível carregar os alertas.")

if alertas_data and alertas_data['alertas']:
    st.warning(f"🚨 {alertas_data['total']} alertas de alta probabilidade encontrados!")
    
    df = pd.DataFrame(alertas_data['alertas'])
    
    # Exibir alertas como cards
    for _, alerta in df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"### {alerta['titulo']}")
                st.markdown(f"📰 **Fonte:** {alerta['fonte']}")
                st.markdown(f"📅 **Data:** {alerta['data_coleta'][:10]}")
            
            with col2:
                probabilidade = alerta['probabilidade'] * 100
                st.metric(
                    "Confiança",
                    f"{probabilidade:.1f}%",
                    delta="Alta"
                )
            
            with col3:
                st.markdown(f"🕌 **Religião:** {alerta.get('religiao', 'Não identificada')}")
                st.markdown(f"🌍 **Local:** {alerta.get('pais', 'Não identificado')}")
                if alerta.get('cidade'):
                    st.markdown(f"📍 {alerta['cidade']}")
            
            if st.button(f"🔗 Ver Detalhes", key=f"alert_{alerta['id']}"):
                st.markdown(f"**URL:** {alerta['url']}")
                st.text_area("Texto da Notícia", alerta.get('texto', ''), height=200)
            
            st.markdown("---")
    
    # Estatísticas dos alertas
    st.subheader("📊 Análise dos Alertas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Alertas por religião
        religiao_counts = df['religiao'].value_counts()
        st.bar_chart(religiao_counts)
    
    with col2:
        # Alertas por país
        pais_counts = df['pais'].value_counts()
        st.bar_chart(pais_counts)
    
else:
    st.success("✅ Nenhum alerta de alta probabilidade no momento.")
    st.info("Alertas são gerados quando a probabilidade de intolerância é superior a 90%.")