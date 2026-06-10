"""
Dashboard Principal do Sistema de Monitoramento de Intolerância Religiosa

Interface web interativa para visualização e análise dos dados monitorados.
"""

import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Monitoramento de Intolerância Religiosa",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2e4057;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .alert-high {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/pray.png", width=100)
    st.title("🕊️ Sistema de Monitoramento")
    st.markdown("---")
    
    st.markdown("### 📊 Navegação")
    st.markdown("""
    - 📈 Dashboard Geral
    - 📰 Notícias
    - 🕌 Por Religião
    - 🗺️ Mapa Global
    - 🚨 Alertas
    - 🤖 XAI - Explicações
    """)
    
    st.markdown("---")
    st.markdown("### ℹ️ Sobre")
    st.info("""
    Sistema Inteligente de Monitoramento Contínuo 
    de Intolerância Religiosa utilizando 
    Inteligência Artificial Explicável (XAI).
    
    Versão 1.0.0
    """)

# Conteúdo principal
st.markdown('<h1 class="main-header">🕊️ Monitoramento de Intolerância Religiosa</h1>', unsafe_allow_html=True)

# Placeholder para as páginas
st.markdown("""
### Bem-vindo ao Sistema de Monitoramento

Este sistema utiliza Inteligência Artificial para monitorar continuamente 
notícias relacionadas à intolerância religiosa em todo o mundo.

**Funcionalidades:**
- 📊 Dashboard com estatísticas em tempo real
- 📰 Coleta automática de notícias de múltiplas fontes
- 🕌 Análise por religião
- 🗺️ Visualização geográfica dos incidentes
- 🚨 Sistema de alertas para casos graves
- 🤖 Explicações das decisões da IA (XAI)

*Selecione uma página no menu lateral para começar.*
""")


# python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000
# streamlit run dashboard/app.py