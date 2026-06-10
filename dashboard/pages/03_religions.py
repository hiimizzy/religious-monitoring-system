"""
Página de Análise por Religião

Exibe estatísticas detalhadas por religião monitorada.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Religiões", layout="wide")

API_URL = "http://localhost:8000"

st.title("🕌 Análise por Religião")

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

if stats and stats['por_religiao']:
    df = pd.DataFrame(stats['por_religiao'])
    
    # Gráfico de pizza
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Distribuição de Casos por Religião")
        fig = px.pie(
            df,
            values='total',
            names='religiao',
            title="Proporção de Casos de Intolerância",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Ranking de Religiões Afetadas")
        fig = px.bar(
            df.sort_values('total', ascending=True),
            x='total',
            y='religiao',
            orientation='h',
            title="Casos por Religião",
            labels={'total': 'Total de Casos', 'religiao': 'Religião'},
            color='total',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    st.subheader("📋 Detalhamento")
    st.dataframe(
        df.sort_values('total', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # Análise adicional
    st.subheader("🔍 Religiões Mais Vulneráveis")
    
    # Calcular percentuais
    total_casos = df['total'].sum()
    df['percentual'] = (df['total'] / total_casos * 100).round(2)
    
    top_3 = df.nlargest(3, 'total')
    
    for _, row in top_3.iterrows():
        with st.expander(f"{row['religiao']} - {row['total']} casos ({row['percentual']}%)"):
            st.metric(
                label=f"Casos de Intolerância contra {row['religiao']}",
                value=f"{row['total']} ocorrências",
                delta=f"{row['percentual']}% do total"
            )
            
            # Barra de progresso
            st.progress(row['percentual'] / 100)
    
else:
    st.info("Nenhum dado de religião disponível para análise.")