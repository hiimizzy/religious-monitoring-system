# religious-monitoring-system

Sistema completo de monitoramento de notícias e futuramente memes relacionados à intolerância religiosa, utilizando Inteligência Artificial Explicável (XAI).

## 📋 Características

- **Monitoramento Automático**: Coleta de notícias de múltiplas fontes RSS
- **Classificação IA**: Modelo de Machine Learning para detecção de intolerância
- **IA Explicável**: Explicações LIME para decisões do modelo
- **Dashboard Interativo**: Visualizações ricas com Streamlit
- **Mapas Geográficos**: Distribuição global dos casos
- **Sistema de Alertas**: Notificações para casos de alta probabilidade
- **API REST**: Backend completo com FastAPI
- **Arquitetura Modular**: Código pronto para produção

## Arquitetura

religious_monitoring/
├── backend/ # API e lógica de negócio
├── dashboard/ # Interface Streamlit
├── models/ # Modelos de ML
├── data/ # Banco de dados




## Instalação Rápida

### Usando Docker (Recomendado)

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/religious-monitoring.git
cd religious_monitoring

# Iniciar com Docker Compose
docker-compose up -d

# Acessar
# Dashboard: http://localhost:8501
# API: http://localhost:8000
# Docs API: http://localhost:8000/docs

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Colocar modelo treinado
cp seu_modelo.pkl models/text_model.pkl

# Iniciar serviços
chmod +x start.sh
./start.sh
```
