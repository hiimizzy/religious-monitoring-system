"""
Módulo de Classificação de Intolerância Religiosa

Este módulo implementa o classificador binário utilizando
Sentence Transformers e Logistic Regression para detectar
intolerância religiosa em textos.
"""

import logging
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReligiousIntoleranceClassifier:
    """
    Classificador de Intolerância Religiosa usando embeddings semânticos.
    
    Attributes:
        model_path (Path): Caminho para o modelo treinado
        encoder: Modelo Sentence Transformer para gerar embeddings
        classifier: Modelo de Regressão Logística treinado
    """
    
    def __init__(self, model_path: str = "models/text_model.pkl"):
        """
        Inicializa o classificador.
        
        Args:
            model_path: Caminho para o arquivo do modelo treinado
            
        Raises:
            FileNotFoundError: Se o modelo não for encontrado
        """
        self.model_path = Path(model_path)
        self.encoder = None
        self.classifier = None
        self._load_models()
        
    def _load_models(self) -> None:
        """
        Carrega os modelos de embedding e classificação.
        """
        try:
            logger.info("Carregando Sentence Transformer...")
            self.encoder = SentenceTransformer(
                'paraphrase-multilingual-MiniLM-L12-v2'
            )
            
            logger.info(f"Carregando modelo de classificação de {self.model_path}")
            if not self.model_path.exists():
                raise FileNotFoundError(f"Modelo não encontrado: {self.model_path}")
            
            self.classifier = joblib.load(self.model_path)
            logger.info("Modelos carregados com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {str(e)}")
            raise
    
    def predict(self, text: str) -> Dict:
        """
        Realiza a predição de intolerância religiosa em um texto.
        
        Args:
            text: Texto para análise
            
        Returns:
            Dicionário com:
                - classe: 0 ou 1
                - classe_nome: "Não Intolerância" ou "Intolerância"
                - probabilidade: float entre 0 e 1
        """
        try:
            # Gerar embedding do texto
            embedding = self.encoder.encode([text])
            
            # Realizar predição
            prediction = self.classifier.predict(embedding)[0]
            probabilities = self.classifier.predict_proba(embedding)[0]
            
            # Obter probabilidade da classe predita
            probability = probabilities[prediction]
            
            result = {
                "classe": int(prediction),
                "classe_nome": "Intolerância" if prediction == 1 else "Não Intolerância",
                "probabilidade": float(probability)
            }
            
            logger.info(f"Predição realizada: {result['classe_nome']} ({result['probabilidade']:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Erro na predição: {str(e)}")
            raise


# Singleton para uso em toda aplicação
classifier_instance = None

def get_classifier() -> ReligiousIntoleranceClassifier:
    """
    Retorna a instância única do classificador.
    
    Returns:
        Instância do ReligiousIntoleranceClassifier
    """
    global classifier_instance
    if classifier_instance is None:
        classifier_instance = ReligiousIntoleranceClassifier()
    return classifier_instance