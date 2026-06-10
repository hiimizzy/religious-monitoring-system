"""
API FastAPI para o Sistema de Monitoramento de Intolerância Religiosa

Fornece endpoints REST para consulta e análise dos dados monitorados.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data.database import get_database

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Religious Intolerance Monitoring API",
    description="API para monitoramento de intolerância religiosa usando IA Explicável",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    classe: int
    classe_nome: str
    probabilidade: float

class NewsFilter(BaseModel):
    religiao: Optional[str] = None
    pais: Optional[str] = None
    classe: Optional[int] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    limit: int = 100

# Configuração de autenticação da API
API_KEY = os.environ.get("API_KEY")


def validate_api_key(request: Request):
    if not API_KEY:
        return

    authorization = request.headers.get("authorization", "")
    api_key_header = request.headers.get("x-api-key", "")
    if authorization.startswith("Bearer "):
        provided_key = authorization.split("Bearer ", 1)[1].strip()
    else:
        provided_key = api_key_header.strip()

    if provided_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


# Instâncias
database = get_database()
classifier = None
explainer = None
extractor = None


def get_classifier_instance():
    global classifier
    if classifier is None:
        from backend.classifier import get_classifier
        classifier = get_classifier()
    return classifier


def get_explainer_instance():
    global explainer
    if explainer is None:
        from backend.lime_explainer import get_explainer
        explainer = get_explainer()
    return explainer


def get_extractor_instance():
    global extractor
    if extractor is None:
        from backend.entity_extractor import get_extractor
        extractor = get_extractor()
    return extractor


@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "name": "Religious Intolerance Monitoring API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/news")
async def get_news(
    religiao: Optional[str] = Query(None),
    pais: Optional[str] = Query(None),
    classe: Optional[int] = Query(None),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    limit: int = Query(100, le=1000)
):
    """
    Recupera notícias com filtros opcionais.
    
    Args:
        religiao: Filtrar por religião
        pais: Filtrar por país
        classe: Filtrar por classe (0 ou 1)
        data_inicio: Data inicial (ISO format)
        data_fim: Data final (ISO format)
        limit: Limite de resultados
    """
    try:
        filters = {}
        if religiao:
            filters['religiao'] = religiao
        if pais:
            filters['pais'] = pais
        if classe is not None:
            filters['classe'] = classe
        if data_inicio:
            filters['data_inicio'] = data_inicio
        if data_fim:
            filters['data_fim'] = data_fim
        
        news = database.get_noticias(filters, limit)
        return {"total": len(news), "noticias": news}
        
    except Exception as e:
        logger.error(f"Erro ao recuperar notícias: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", response_model=PredictResponse)
async def predict(req: Request, payload: PredictRequest):
    """
    Realiza predição de intolerância religiosa em um texto.
    
    Args:
        req: Requisição HTTP com headers autorizados
        payload: Objeto com o texto para análise
    """
    try:
        validate_api_key(req)
        classifier = get_classifier_instance()
        result = classifier.predict(payload.text)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na predição: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts")
async def get_alerts():
    """Recupera alertas de alta probabilidade de intolerância."""
    try:
        alertas = database.get_alertas()
        return {"total": len(alertas), "alertas": alertas}
        
    except Exception as e:
        logger.error(f"Erro ao recuperar alertas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics")
async def get_statistics():
    """Recupera estatísticas gerais do monitoramento."""
    try:
        stats = database.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao recuperar estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain")
async def explain_prediction(req: Request, payload: PredictRequest):
    """
    Gera explicação LIME para uma predição.
    
    Args:
        req: Requisição HTTP com headers autorizados
        payload: Objeto com o texto para explicar
    """
    try:
        validate_api_key(req)
        explainer = get_explainer_instance()
        explanation = explainer.explain(payload.text)
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na explicação: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da API."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)