"""
Módulo de Extração de Entidades

Extrai entidades como países, cidades e religiões dos textos
utilizando técnicas de NLP.
"""

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class EntityExtractor:
    """
    Extrator de entidades para textos sobre intolerância religiosa.
    
    Attributes:
        countries: Lista de países em português e inglês
        religions: Lista de religiões monitoradas
        cities: Lista de cidades principais
    """
    
    def __init__(self):
        """Inicializa o extrator com listas de entidades."""
        self.countries = {
            'Brasil', 'Brazil', 'Estados Unidos', 'United States', 'USA',
            'Índia', 'India', 'Paquistão', 'Pakistan', 'Nigéria', 'Nigeria',
            'Egito', 'Egypt', 'Indonésia', 'Indonesia', 'Reino Unido',
            'United Kingdom', 'UK', 'França', 'France', 'Alemanha', 'Germany',
            'Itália', 'Italy', 'Espanha', 'Spain', 'Portugal', 'Portugal',
            'China', 'China', 'Japão', 'Japan', 'Rússia', 'Russia',
            'África do Sul', 'South Africa', 'Canadá', 'Canada', 'México',
            'Mexico', 'Argentina', 'Colômbia', 'Colombia'
        }
        
        self.religions = {
            'cristianismo': ['cristianismo', 'cristãos', 'cristã', 'christianity', 'christian'],
            'catolicismo': ['catolicismo', 'católicos', 'católica', 'catholicism', 'catholic'],
            'evangélico': ['evangélico', 'evangélicos', 'evangélica', 'evangelical', 'protestant'],
            'islamismo': ['islamismo', 'islâmico', 'muçulmanos', 'islam', 'muslim', 'islamic'],
            'judaísmo': ['judaísmo', 'judeus', 'judia', 'judaism', 'jewish'],
            'budismo': ['budismo', 'budistas', 'buddhism', 'buddhist'],
            'hinduísmo': ['hinduísmo', 'hindus', 'hinduism', 'hindu'],
            'umbanda': ['umbanda', 'umbandistas', 'umbanda'],
            'candomblé': ['candomblé', 'candomblecistas', 'candomble'],
            'religiões afro-brasileiras': ['afro-brasileira', 'afro brasileira', 'afro-brazilian']
        }
        
        self.cities = {
            'São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza',
            'Belo Horizonte', 'Manaus', 'Curitiba', 'Recife', 'Porto Alegre',
            'New York', 'London', 'Paris', 'Berlin', 'Rome', 'Madrid',
            'Moscow', 'Beijing', 'Tokyo', 'Delhi', 'Cairo', 'Lagos'
        }
    
    def extract_entities(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extrai entidades do texto.
        
        Args:
            text: Texto para extrair entidades
            
        Returns:
            Dicionário com país, cidade e religião
        """
        try:
            text_lower = text.lower()
            
            # Extrair religião
            religion = self._extract_religion(text_lower)
            
            # Extrair país
            country = self._extract_country(text)
            
            # Extrair cidade
            city = self._extract_city(text)
            
            entities = {
                'pais': country,
                'cidade': city,
                'religiao': religion
            }
            
            logger.info(f"Entidades extraídas: {entities}")
            return entities
            
        except Exception as e:
            logger.error(f"Erro ao extrair entidades: {str(e)}")
            return {'pais': None, 'cidade': None, 'religiao': None}
    
    def _extract_religion(self, text: str) -> Optional[str]:
        """
        Extrai religião do texto.
        
        Args:
            text: Texto em minúsculas
            
        Returns:
            Nome da religião ou None
        """
        for religion, keywords in self.religions.items():
            for keyword in keywords:
                if keyword in text:
                    return religion
        
        return 'Outras'
    
    def _extract_country(self, text: str) -> Optional[str]:
        """
        Extrai país do texto.
        
        Args:
            text: Texto original
            
        Returns:
            Nome do país ou None
        """
        for country in self.countries:
            if country.lower() in text.lower():
                return country
        
        return None
    
    def _extract_city(self, text: str) -> Optional[str]:
        """
        Extrai cidade do texto.
        
        Args:
            text: Texto original
            
        Returns:
            Nome da cidade ou None
        """
        for city in self.cities:
            if city.lower() in text.lower():
                return city
        
        return None


# Singleton
extractor_instance = None

def get_extractor() -> EntityExtractor:
    """
    Retorna a instância única do extrator de entidades.
    
    Returns:
        Instância do EntityExtractor
    """
    global extractor_instance
    if extractor_instance is None:
        extractor_instance = EntityExtractor()
    return extractor_instance