"""
Página do Dashboard Principal

Exibe estatísticas gerais e gráficos do monitoramento.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

# Configuração da página
st.set_page_config(page_title="Dashboard", layout="wide")

# API endpoint
API_URL = "http://localhost:8000"

def load_statistics():
    """Carrega estatísticas da API."""
    try:
        response = requests.get(f"{API_URL}/statistics")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def load_news(filters=None):
    """Carrega notícias da API."""
    try:
        response = requests.get(f"{API_URL}/news", params=filters)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Título
st.title("📊 Dashboard Geral")

# Carregar dados
stats = load_statistics()

if stats:
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total de Notícias",
            stats['total_noticias'],
            delta=None
        )
    
    with col2:
        st.metric(
            "Casos de Intolerância",
            stats['total_intolerancia'],
            delta=f"{stats['total_intolerancia']/max(stats['total_noticias'],1)*100:.1f}%" if stats['total_noticias'] > 0 else "0%"
        )
    
    with col3:
        st.metric(
            "Não Intolerância",
            stats['total_nao_intolerancia']
        )
    
    with col4:
        st.metric(
            "Última Atualização",
            stats['ultima_atualizacao'][:10] if stats['ultima_atualizacao'] else "N/A"
        )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Casos por Religião")
        if stats['por_religiao']:
            df_religiao = pd.DataFrame(stats['por_religiao'])
            fig = px.bar(
                df_religiao,
                x='religiao',
                y='total',
                title="Intolerância por Religião",
                labels={'religiao': 'Religião', 'total': 'Total de Casos'},
                color='total',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🌍 Casos por País")
        if stats['por_pais']:
            df_pais = pd.DataFrame(stats['por_pais'])
            fig = px.bar(
                df_pais,
                x='pais',
                y='total',
                title="Intolerância por País",
                labels={'pais': 'País', 'total': 'Total de Casos'},
                color='total',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico temporal
    st.subheader("📈 Evolução Temporal")
    news_data = load_news({'limit': 1000})
    if news_data and news_data['noticias']:
        df_temporal = pd.DataFrame(news_data['noticias'])
        df_temporal['data_coleta'] = pd.to_datetime(df_temporal['data_coleta'])
        df_temporal = df_temporal.sort_values('data_coleta')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_temporal['data_coleta'],
            y=df_temporal['probabilidade'],
            mode='lines+markers',
            name='Probabilidade',
            line=dict(color='red', width=2)
        ))
        fig.update_layout(
            title="Probabilidade de Intolerância ao Longo do Tempo",
            xaxis_title="Data",
            yaxis_title="Probabilidade",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Não foi possível carregar as estatísticas. Verifique se a API está rodando.")