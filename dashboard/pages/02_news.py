"""
Página de Notícias

Exibe tabela interativa com todas as notícias coletadas e processadas.
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Notícias", layout="wide")

API_URL = "http://localhost:8000"

def load_news(filters=None):
    """Carrega notícias da API."""
    try:
        response = requests.get(f"{API_URL}/news", params=filters)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

st.title("📰 Notícias Monitoradas")

# Filtros
col1, col2, col3, col4 = st.columns(4)

with col1:
    religiao_filter = st.selectbox(
        "Religião",
        ["Todas", "cristianismo", "catolicismo", "evangélico", "islamismo", 
         "judaísmo", "budismo", "hinduísmo", "umbanda", "candomblé", "Outras"]
    )

with col2:
    pais_filter = st.text_input("País", "")

with col3:
    classe_filter = st.selectbox(
        "Classe",
        ["Todas", "0 - Não Intolerância", "1 - Intolerância"]
    )

with col4:
    limit = st.slider("Limite de resultados", 10, 1000, 100)

# Preparar filtros
filters = {'limit': limit}
if religiao_filter != "Todas":
    filters['religiao'] = religiao_filter
if pais_filter:
    filters['pais'] = pais_filter
if classe_filter != "Todas":
    filters['classe'] = int(classe_filter.split(' - ')[0])

# Carregar dados
news_data = load_news(filters)

if news_data:
    st.info(f"Total de notícias encontradas: {news_data['total']}")
    
    if news_data['noticias']:
        df = pd.DataFrame(news_data['noticias'])
        
        # Formatar dados
        df['probabilidade'] = df['probabilidade'].apply(lambda x: f"{x:.2%}")
        df['classe_nome'] = df['classe'].apply(
            lambda x: "🚨 Intolerância" if x == 1 else "✅ Não Intolerância"
        )
        
        # Selecionar colunas para exibição
        display_columns = [
            'titulo', 'fonte', 'religiao', 'pais', 'cidade',
            'classe_nome', 'probabilidade', 'data_coleta'
        ]
        
        st.dataframe(
            df[display_columns],
            use_container_width=True,
            hide_index=True
        )
        
        # Exportar CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Exportar CSV",
            data=csv,
            file_name=f"noticias_monitoramento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhuma notícia encontrada com os filtros selecionados.")
else:
    st.error("Não foi possível carregar as notícias. Verifique se a API está rodando.")