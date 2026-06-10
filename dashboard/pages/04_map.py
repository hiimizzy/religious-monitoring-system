"""
Página do Mapa Global

Exibe mapa coroplético com distribuição geográfica dos casos.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Mapa Global", layout="wide")

API_URL = "http://localhost:8000"

st.title("🗺️ Mapa Global de Intolerância Religiosa")

# Carregar estatísticas
try:
    response = requests.get(f"{API_URL}/statistics")
    if response.status_code == 200:
        stats = response.json()
    else:
        stats = None
except:
    stats = None
    st.error("Não foi possível carregar as estatísticas.")

if stats and stats['por_pais']:
    df = pd.DataFrame(stats['por_pais'])
    
    # Mapeamento de nomes de países
    country_mapping = {
        'Brasil': 'Brazil',
        'Estados Unidos': 'United States of America',
        'Reino Unido': 'United Kingdom',
        'Índia': 'India',
        'Paquistão': 'Pakistan',
        'Nigéria': 'Nigeria',
        'Egito': 'Egypt',
        'Indonésia': 'Indonesia',
        'França': 'France',
        'Alemanha': 'Germany',
        'Itália': 'Italy',
        'Espanha': 'Spain',
        'Portugal': 'Portugal',
        'China': 'China',
        'Japão': 'Japan',
        'Rússia': 'Russia',
        'África do Sul': 'South Africa',
        'Canadá': 'Canada',
        'México': 'Mexico',
        'Argentina': 'Argentina',
        'Colômbia': 'Colombia'
    }
    
    # Mapear nomes para inglês
    df['pais_ingles'] = df['pais'].map(country_mapping).fillna(df['pais'])
    
    # Criar mapa
    fig = px.choropleth(
        df,
        locations='pais_ingles',
        locationmode='country names',
        color='total',
        hover_name='pais',
        color_continuous_scale='Reds',
        title='Casos de Intolerância Religiosa por País',
        labels={'total': 'Total de Casos'}
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de dados
    st.subheader("📊 Dados por País")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.dataframe(
            df[['pais', 'total']].sort_values('total', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.metric(
            "Total de Países",
            len(df)
        )
        st.metric(
            "País Mais Afetado",
            df.nlargest(1, 'total')['pais'].values[0] if len(df) > 0 else "N/A"
        )
else:
    st.info("Nenhum dado geográfico disponível para o mapa.")