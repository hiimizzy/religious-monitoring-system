# religious-monitoring-system

Sistema completo de monitoramento de notícias e futuramente memes relacionados à intolerância religiosa, utilizando Inteligência Artificial Explicável (XAI).

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
