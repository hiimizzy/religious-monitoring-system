"""
Módulo Coletor de Notícias RSS

Coleta notícias de múltiplas fontes RSS relacionadas à intolerância religiosa.
"""

import asyncio
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class NewsCollector:
    """
    Coletor de notícias de fontes RSS.
    
    Attributes:
        sources: Lista de fontes RSS configuradas
        keywords: Palavras-chave para filtragem
        timeout: Timeout para requisições HTTP
    """
    
    def __init__(self):
        """Inicializa o coletor com fontes e palavras-chave."""
        self.sources = {
            'google_news': 'https://news.google.com/rss/search?q=intolerância+religiosa&hl=pt-BR&gl=BR&ceid=BR:pt-419',
            'reuters': 'https://www.reuters.com/tools/rss',
            'bbc': 'http://feeds.bbci.co.uk/news/world/rss.xml',
            'the_guardian': 'https://www.theguardian.com/world/rss',
            'g1': 'https://g1.globo.com/rss/g1/',
            'uol': 'https://rss.uol.com.br/feed/noticias.xml',
            'agencia_brasil': 'https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml'
        }
        
        self.keywords = [
            'religious intolerance',
            'religious discrimination',
            'religious hate crime',
            'religious attack',
            'intolerância religiosa',
            'discriminação religiosa',
            'ataque religioso',
            'ataque a templo',
            'ataque a igreja',
            'ataque a terreiro',
            'racismo religioso',
            'violência religiosa',
            'perseguição religiosa'
        ]
        
        self.timeout = 30
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Religious Intolerance Monitor Bot/1.0'
        })
    
    def _generate_hash(self, text: str) -> str:
        """
        Gera hash MD5 do texto para evitar duplicatas.
        
        Args:
            text: Texto para gerar hash
            
        Returns:
            Hash MD5
        """
        return hashlib.md5(text.encode()).hexdigest()
    
    def _extract_text(self, html_content: str) -> str:
        """
        Extrai texto principal de conteúdo HTML.
        
        Args:
            html_content: Conteúdo HTML
            
        Returns:
            Texto extraído
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remover scripts e estilos
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extrair texto
            text = soup.get_text()
            
            # Limpar texto
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:5000]  # Limitar tamanho
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto: {str(e)}")
            return ""
    
    def _is_related(self, text: str) -> bool:
        """
        Verifica se o texto está relacionado à intolerância religiosa.
        
        Args:
            text: Texto para verificar
            
        Returns:
            True se relacionado
        """
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)
    
    async def fetch_feed(self, source_name: str, feed_url: str) -> List[Dict]:
        """
        Busca notícias de uma fonte RSS específica.
        
        Args:
            source_name: Nome da fonte
            feed_url: URL do feed RSS
            
        Returns:
            Lista de notícias encontradas
        """
        try:
            logger.info(f"Buscando notícias de {source_name}...")
            
            # Parsear feed RSS
            feed = await asyncio.get_event_loop().run_in_executor(
                None, feedparser.parse, feed_url
            )
            
            news_items = []
            
            for entry in feed.entries[:10]:  # Limitar a 10 notícias por fonte
                try:
                    # Extrair informações básicas
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    summary = entry.get('summary', '')
                    
                    # Verificar se está relacionado
                    full_text = f"{title} {summary}"
                    if not self._is_related(full_text):
                        continue
                    
                    # Tentar obter texto completo
                    try:
                        response = await asyncio.get_event_loop().run_in_executor(
                            None, 
                            lambda: self.session.get(link, timeout=self.timeout)
                        )
                        if response.status_code == 200:
                            full_content = self._extract_text(response.text)
                        else:
                            full_content = summary
                    except:
                        full_content = summary
                    
                    news_item = {
                        'titulo': title,
                        'texto': full_content[:2000],
                        'url': link,
                        'fonte': source_name,
                        'data_coleta': datetime.now().isoformat()
                    }
                    
                    news_items.append(news_item)
                    logger.info(f"Notícia encontrada: {title[:100]}")
                    
                except Exception as e:
                    logger.warning(f"Erro ao processar entrada RSS: {str(e)}")
                    continue
            
            logger.info(f"Encontradas {len(news_items)} notícias de {source_name}")
            return news_items
            
        except Exception as e:
            logger.error(f"Erro ao buscar feed de {source_name}: {str(e)}")
            return []
    
    async def collect_all_news(self) -> List[Dict]:
        """
        Coleta notícias de todas as fontes configuradas.
        
        Returns:
            Lista de todas as notícias coletadas
        """
        tasks = []
        for source_name, feed_url in self.sources.items():
            tasks.append(self.fetch_feed(source_name, feed_url))
        
        results = await asyncio.gather(*tasks)
        
        # Combinar resultados
        all_news = []
        for news_list in results:
            all_news.extend(news_list)
        
        logger.info(f"Total de notícias coletadas: {len(all_news)}")
        return all_news


# Singleton
collector_instance = None

def get_collector() -> NewsCollector:
    """
    Retorna a instância única do coletor de notícias.
    
    Returns:
        Instância do NewsCollector
    """
    global collector_instance
    if collector_instance is None:
        collector_instance = NewsCollector()
    return collector_instance