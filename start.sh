#!/bin/bash

echo "🕊️ Iniciando Sistema de Monitoramento de Intolerância Religiosa"
echo "=============================================================="

# Criar diretórios necessários
mkdir -p data models logs

# Verificar se o modelo existe
if [ ! -f "models/text_model.pkl" ]; then
    echo "⚠️  Modelo não encontrado. Por favor, coloque o arquivo text_model.pkl na pasta models/"
    exit 1
fi

# Iniciar serviços
echo "📡 Iniciando API Backend..."
uvicorn backend.api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "📊 Iniciando Dashboard Streamlit..."
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0 &
DASHBOARD_PID=$!

echo "⏰ Iniciando Agendador de Tarefas..."
python -m backend.scheduler &
SCHEDULER_PID=$!

echo ""
echo "✅ Sistema iniciado com sucesso!"
echo ""
echo "📡 API Backend: http://localhost:8000"
echo "📊 Dashboard: http://localhost:8501"
echo "📚 Documentação API: http://localhost:8000/docs"
echo ""
echo "Pressione Ctrl+C para parar todos os serviços"

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "🛑 Parando serviços..."
    kill $BACKEND_PID $DASHBOARD_PID $SCHEDULER_PID 2>/dev/null
    echo "✅ Serviços parados"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Manter script rodando
wait