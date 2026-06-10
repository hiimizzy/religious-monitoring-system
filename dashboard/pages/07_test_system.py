"""
Página de Teste do Sistema
Permite testar e validar o sistema com notícias personalizadas
"""

import os
import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="Teste do Sistema", layout="wide")

# Configuração da API
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Debug - Mostrar URL da API (remova em produção)
st.sidebar.info(f"🔗 API: {API_URL}")

st.title("🧪 Teste do Sistema")

# Área de teste manual
st.subheader("📝 Teste Manual de Notícia")

col1, col2 = st.columns([1, 1])

with col1:
    titulo_teste = st.text_input("Título da Notícia", "Digite o título aqui...")
    
with col2:
    fonte_teste = st.selectbox(
        "Fonte da Notícia",
        ["Manual", "Google News", "G1", "UOL", "Reuters", "BBC", "The Guardian"]
    )

texto_teste = st.text_area(
    "Texto da Notícia",
    height=200,
    placeholder="Cole aqui o texto completo da notícia para análise..."
)

if st.button("🔬 Analisar Notícia", type="primary"):
    if texto_teste:
        with st.spinner("Analisando notícia..."):
            
            # Verificar se a API está acessível
            try:
                health_check = requests.get(f"{API_URL}/health", timeout=5)
                if health_check.status_code != 200:
                    st.error(f"❌ API não está respondendo. Status: {health_check.status_code}")
                    st.stop()
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Não foi possível conectar à API em {API_URL}")
                st.info("Verifique se o backend está rodando: `python -m backend.api`")
                st.stop()
            
            # 1. Fazer predição
            st.write("🔄 Realizando predição...")
            try:
                predict_response = requests.post(
                    f"{API_URL}/predict",
                    json={"text": texto_teste},
                    timeout=30
                )
                
                if predict_response.status_code != 200:
                    st.error(f"❌ Erro na predição. Status: {predict_response.status_code}")
                    st.json(predict_response.json() if predict_response.text else {"error": "Sem resposta"})
                    st.stop()
                
                prediction = predict_response.json()
                st.success("✅ Predição realizada!")
                
            except Exception as e:
                st.error(f"❌ Erro na predição: {str(e)}")
                st.stop()
            
            # Exibir resultado da predição
            col1, col2, col3 = st.columns(3)
            
            with col1:
                classe = prediction.get('classe', 0)
                classe_nome = prediction.get('classe_nome', 'Desconhecido')
                st.metric(
                    "Classificação",
                    classe_nome,
                    delta="🚨" if classe == 1 else "✅"
                )
            
            with col2:
                probabilidade = prediction.get('probabilidade', 0)
                st.metric(
                    "Probabilidade",
                    f"{probabilidade:.2%}"
                )
            
            with col3:
                alerta = probabilidade > 0.90 and classe == 1
                st.metric(
                    "Alerta",
                    "🚨 SIM" if alerta else "✅ NÃO"
                )
            
            # 2. Gerar explicação LIME
            st.write("🔍 Gerando explicação LIME...")
            st.info("O LIME pode levar alguns segundos para gerar a explicação...")
            
            try:
                explain_response = requests.post(
                    f"{API_URL}/explain",
                    json={"text": texto_teste},
                    timeout=60  # Timeout maior para LIME
                )
                
                st.write(f"Status da explicação: {explain_response.status_code}")
                
                if explain_response.status_code == 200:
                    explanation = explain_response.json()
                    st.success("✅ Explicação LIME gerada com sucesso!")
                    
                    # Debug - Mostrar estrutura da resposta (remova em produção)
                    with st.expander("🔧 Debug - Resposta completa da API"):
                        st.json(explanation)
                    
                    # Exibir explicação LIME
                    st.subheader("🔍 Explicação LIME")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**✅ Indicadores de Intolerância**")
                        features_positivas = explanation.get('features_positivas', [])
                        
                        if features_positivas:
                            df_pos = pd.DataFrame(features_positivas)
                            if not df_pos.empty:
                                # Renomear colunas para português
                                df_pos = df_pos.rename(columns={
                                    'palavra': 'Palavra/Frase',
                                    'peso': 'Peso'
                                })
                                # Formatar peso
                                df_pos['Peso'] = df_pos['Peso'].apply(lambda x: f"{x:.4f}")
                                # Ordenar por peso absoluto
                                df_pos = df_pos.sort_values('Peso', ascending=False)
                                
                                st.dataframe(
                                    df_pos,
                                    use_container_width=True,
                                    hide_index=True
                                )
                            else:
                                st.info("Nenhum indicador positivo encontrado")
                        else:
                            st.info("Nenhum indicador positivo encontrado")
                        
                        # Mostrar importância total positiva
                        importancia = explanation.get('importancia_total', {})
                        if importancia:
                            st.metric(
                                "Peso Total Positivo",
                                f"{importancia.get('positiva', 0):.4f}"
                            )
                    
                    with col2:
                        st.markdown("**❌ Indicadores Contrários**")
                        features_negativas = explanation.get('features_negativas', [])
                        
                        if features_negativas:
                            df_neg = pd.DataFrame(features_negativas)
                            if not df_neg.empty:
                                # Renomear colunas para português
                                df_neg = df_neg.rename(columns={
                                    'palavra': 'Palavra/Frase',
                                    'peso': 'Peso'
                                })
                                # Formatar peso (mostrar valor absoluto para negativo)
                                df_neg['Peso'] = df_neg['Peso'].apply(lambda x: f"{abs(x):.4f}")
                                # Ordenar por peso absoluto
                                df_neg = df_neg.sort_values('Peso', ascending=False)
                                
                                st.dataframe(
                                    df_neg,
                                    use_container_width=True,
                                    hide_index=True
                                )
                            else:
                                st.info("Nenhum indicador negativo encontrado")
                        else:
                            st.info("Nenhum indicador negativo encontrado")
                        
                        # Mostrar importância total negativa
                        importancia = explanation.get('importancia_total', {})
                        if importancia:
                            st.metric(
                                "Peso Total Negativo",
                                f"{abs(importancia.get('negativa', 0)):.4f}"
                            )
                    
                elif explain_response.status_code == 500:
                    error_detail = explain_response.json().get('detail', 'Erro desconhecido')
                    st.error(f"❌ Erro no servidor ao gerar explicação: {error_detail}")
                    st.info("Verifique os logs do backend para mais detalhes")
                    
                elif explain_response.status_code == 422:
                    st.error("❌ Erro de validação. Verifique o formato do texto enviado.")
                    st.json(explain_response.json())
                    
                else:
                    st.warning(f"⚠️ Status inesperado: {explain_response.status_code}")
                    st.text(explain_response.text[:500])
                    
            except requests.exceptions.Timeout:
                st.error("❌ Timeout ao gerar explicação LIME. O texto pode ser muito longo.")
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Conexão perdida com a API em {API_URL}")
            except Exception as e:
                st.error(f"❌ Erro inesperado na explicação: {str(e)}")
                import traceback
                with st.expander("Detalhes do erro"):
                    st.code(traceback.format_exc())

# Teste em lote
st.markdown("---")
st.subheader("📊 Teste em Lote")

# Templates de teste
test_templates = {
    "Notícias PT-BR": [
        "Ataque a terreiro de candomblé em Salvador - Grupo invade local sagrado e destrói imagens",
        "Igreja realiza festa junina beneficente para comunidade carente",
        "Mesquita vandalizada com pichações islamofóbicas no Rio de Janeiro",
        "Encontro inter-religioso promove paz e diálogo entre diferentes crenças",
        "Judeus denunciam aumento de ataques antissemitas em redes sociais"
    ],
    "Notícias EN": [
        "Religious hate crime targets mosque in London - Windows smashed and hate messages painted",
        "Interfaith community garden brings Christians, Muslims and Jews together in Manchester",
        "Buddhist temple defaced with extremist symbols in California",
        "Church charity helps homeless regardless of religious beliefs"
    ],
    "Casos Limite": [
        "Debate acalorado sobre religião termina em discussão, mas sem violência física",
        "Crítica teológica a doutrinas religiosas em artigo acadêmico",
        "Manifestantes protestam pacificamente contra decisão de líder religioso",
        "Sátira religiosa em programa de comédia gera controvérsia nas redes sociais"
    ]
}

categoria = st.selectbox("Selecione categoria de teste", list(test_templates.keys()))

if st.button("🚀 Executar Teste em Lote"):
    textos = test_templates[categoria]
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, texto in enumerate(textos):
        status_text.text(f"Processando {i+1}/{len(textos)}: {texto[:50]}...")
        
        try:
            # Predição
            response = requests.post(
                f"{API_URL}/predict",
                json={"text": texto},
                timeout=30
            )
            
            if response.status_code == 200:
                pred = response.json()
                results.append({
                    "Texto": texto[:100] + "...",
                    "Classificação": pred['classe_nome'],
                    "Probabilidade": f"{pred['probabilidade']:.2%}",
                    "Alerta": "🚨" if pred['probabilidade'] > 0.90 and pred['classe'] == 1 else "✅"
                })
            else:
                results.append({
                    "Texto": texto[:100] + "...",
                    "Classificação": "ERRO",
                    "Probabilidade": "N/A",
                    "Alerta": "❌"
                })
            
            progress_bar.progress((i + 1) / len(textos))
            
        except Exception as e:
            st.error(f"Erro ao testar '{texto[:50]}...': {str(e)}")
            results.append({
                "Texto": texto[:100] + "...",
                "Classificação": "ERRO",
                "Probabilidade": "N/A",
                "Alerta": "❌"
            })
    
    status_text.text("Processamento concluído!")
    
    if results:
        st.success(f"✅ Teste concluído! {len(results)} notícias analisadas")
        df_results = pd.DataFrame(results)
        st.dataframe(df_results, use_container_width=True)
        
        # Estatísticas
        col1, col2 = st.columns(2)
        
        with col1:
            intolerancia = sum(1 for r in results if 'Intolerância' in r['Classificação'])
            st.metric("Casos de Intolerância", intolerancia)
        
        with col2:
            alertas = sum(1 for r in results if r['Alerta'] == "🚨")
            st.metric("Alertas Gerados", alertas)

# Histórico de testes
st.markdown("---")
st.subheader("📜 Histórico de Testes Recentes")

try:
    response = requests.get(f"{API_URL}/news", params={"limit": 10}, timeout=10)
    if response.status_code == 200:
        recent = response.json()
        if recent['noticias']:
            st.info(f"Últimas {len(recent['noticias'])} notícias processadas")
            df_recent = pd.DataFrame(recent['noticias'])
            st.dataframe(
                df_recent[['titulo', 'classe', 'probabilidade', 'data_coleta']],
                use_container_width=True
            )
        else:
            st.info("Nenhuma notícia processada ainda")
except:
    st.warning("Histórico não disponível")


# python -m backend.api