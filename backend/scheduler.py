"""
Módulo Agendador de Tarefas

Gerencia o agendamento automático da coleta de notícias
e classificação.
"""

import asyncio
import logging
from datetime import datetime

from .news_collector import get_collector
from .classifier import get_classifier
from .entity_extractor import get_extractor
from .lime_explainer import get_explainer
from ..data.database import get_database

logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    Agendador de tarefas para coleta e processamento de notícias.
    
    Attributes:
        collector: Instância do coletor de notícias
        classifier: Instância do classificador
        extractor: Instância do extrator de entidades
        explainer: Instância do explicador LIME
        database: Instância do banco de dados
        interval: Intervalo entre execuções em segundos
    """
    
    def __init__(self, interval: int = 3600):
        """
        Inicializa o agendador.
        
        Args:
            interval: Intervalo entre coletas em segundos (padrão: 1 hora)
        """
        self.collector = get_collector()
        self.classifier = get_classifier()
        self.extractor = get_extractor()
        self.explainer = get_explainer()
        self.database = get_database()
        self.interval = interval
        
    async def process_news(self) -> None:
        """Processa todas as notícias coletadas."""
        try:
            logger.info("Iniciando processamento de notícias...")
            
            # Coletar notícias
            news_list = await self.collector.collect_all_news()
            
            processed_count = 0
            intolerance_count = 0
            
            for news in news_list:
                try:
                    # Classificar notícia
                    prediction = self.classifier.predict(news['texto'])
                    
                    # Extrair entidades
                    entities = self.extractor.extract_entities(news['texto'])
                    
                    # Gerar explicação LIME se for intolerância
                    explicacao = None
                    if prediction['classe'] == 1:
                        explicacao = self.explainer.explain(news['texto'])
                        intolerance_count += 1
                    
                    # Preparar dados para o banco
                    noticia_data = {
                        'titulo': news['titulo'],
                        'texto': news['texto'],
                        'url': news['url'],
                        'fonte': news['fonte'],
                        'pais': entities.get('pais'),
                        'cidade': entities.get('cidade'),
                        'religiao': entities.get('religiao'),
                        'classe': prediction['classe'],
                        'probabilidade': prediction['probabilidade'],
                        'explicacao_lime': str(explicacao) if explicacao else None
                    }
                    
                    # Inserir no banco
                    self.database.insert_noticia(noticia_data)
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao processar notícia: {str(e)}")
                    continue
            
            logger.info(f"Processamento concluído: {processed_count} notícias processadas, {intolerance_count} casos de intolerância")
            
        except Exception as e:
            logger.error(f"Erro no processamento: {str(e)}")
    
    async def run_continuously(self) -> None:
        """Executa o agendador continuamente."""
        logger.info(f"Iniciando agendador com intervalo de {self.interval} segundos...")
        
        while True:
            try:
                await self.process_news()
                logger.info(f"Próxima execução em {self.interval} segundos...")
                await asyncio.sleep(self.interval)
                
            except KeyboardInterrupt:
                logger.info("Agendador interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro no agendador: {str(e)}")
                await asyncio.sleep(60)  # Esperar 1 minuto em caso de erro


def start_scheduler():
    """Inicia o agendador de tarefas."""
    scheduler = TaskScheduler()
    asyncio.run(scheduler.run_continuously())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    start_scheduler()