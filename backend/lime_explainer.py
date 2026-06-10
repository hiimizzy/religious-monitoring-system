"""
Módulo de Explicabilidade com LIME

Implementa explicações LIME para as predições do modelo
de classificação de intolerância religiosa.
"""

import json
import logging
from typing import Dict, List, Tuple

import numpy as np
from lime.lime_text import LimeTextExplainer

from .classifier import get_classifier

logger = logging.getLogger(__name__)


class LimeExplainer:
    """
    Explicador LIME para o classificador de intolerância religiosa.
    
    Attributes:
        classifier: Instância do classificador
        explainer: Instância do LimeTextExplainer
        class_names: Nomes das classes
    """
    
    def __init__(self):
        """Inicializa o explicador LIME."""
        self.classifier = get_classifier()
        self.explainer = LimeTextExplainer(
            class_names=['Não Intolerância', 'Intolerância'],
            feature_selection='auto'
        )
        
    def _predict_proba(self, texts: List[str]) -> np.ndarray:
        """
        Função de predição para o LIME.
        
        Args:
            texts: Lista de textos
            
        Returns:
            Matriz de probabilidades
        """
        probabilities = []
        for text in texts:
            embedding = self.classifier.encoder.encode([text])
            proba = self.classifier.classifier.predict_proba(embedding)[0]
            probabilities.append(proba)
        
        return np.array(probabilities)
    
    def explain(self, text: str, num_features: int = 10) -> Dict:
        """
        Gera explicação LIME para um texto.
        
        Args:
            text: Texto para explicar
            num_features: Número de features para mostrar
            
        Returns:
            Dicionário com explicação
        """
        try:
            logger.info("Gerando explicação LIME...")
            
            # Gerar explicação
            exp = self.explainer.explain_instance(
                text,
                self._predict_proba,
                num_features=num_features,
                num_samples=5000
            )
            
            # Extrair features importantes
            explanation_list = exp.as_list()
            
            # Separar features positivas e negativas
            positive_features = []
            negative_features = []
            
            for word, weight in explanation_list:
                feature_data = {
                    'palavra': word,
                    'peso': float(weight)
                }
                if weight > 0:
                    positive_features.append(feature_data)
                else:
                    negative_features.append(feature_data)
            
            # Ordenar por peso absoluto
            positive_features.sort(key=lambda x: abs(x['peso']), reverse=True)
            negative_features.sort(key=lambda x: abs(x['peso']), reverse=True)
            
            # Obter predição
            prediction = self._predict_proba([text])[0]
            
            explanation = {
                'texto': text,
                'predicao': {
                    'classe': int(np.argmax(prediction)),
                    'classe_nome': 'Intolerância' if np.argmax(prediction) == 1 else 'Não Intolerância',
                    'probabilidade': float(prediction[np.argmax(prediction)])
                },
                'features_positivas': positive_features,
                'features_negativas': negative_features,
                'importancia_total': {
                    'positiva': sum(f['peso'] for f in positive_features),
                    'negativa': sum(f['peso'] for f in negative_features)
                }
            }
            
            logger.info(f"Explicação gerada: {len(positive_features)} features positivas, {len(negative_features)} negativas")
            return explanation
            
        except Exception as e:
            logger.error(f"Erro ao gerar explicação LIME: {str(e)}")
            raise
    
    def save_explanation(self, explanation: Dict) -> str:
        """
        Salva explicação em formato JSON.
        
        Args:
            explanation: Dicionário com explicação
            
        Returns:
            String JSON da explicação
        """
        return json.dumps(explanation, ensure_ascii=False)


# Singleton
explainer_instance = None

def get_explainer() -> LimeExplainer:
    """
    Retorna a instância única do explicador LIME.
    
    Returns:
        Instância do LimeExplainer
    """
    global explainer_instance
    if explainer_instance is None:
        explainer_instance = LimeExplainer()
    return explainer_instance