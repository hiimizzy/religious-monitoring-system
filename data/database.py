"""
Módulo de Banco de Dados SQLite

Gerencia todas as operações de banco de dados para o sistema
de monitoramento de intolerância religiosa.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """
    Gerenciador de banco de dados SQLite para o sistema de monitoramento.
    
    Attributes:
        db_path (Path): Caminho para o arquivo do banco de dados
        conn: Conexão com o banco de dados
    """
    
    def __init__(self, db_path: str = "data/monitoring.db"):
        """
        Inicializa a conexão com o banco de dados.
        
        Args:
            db_path: Caminho para o arquivo SQLite
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_database()
    
    def _init_database(self) -> None:
        """Inicializa as tabelas do banco de dados."""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            
            # Criar tabelas
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS noticias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    texto TEXT,
                    url TEXT UNIQUE NOT NULL,
                    fonte TEXT,
                    pais TEXT,
                    cidade TEXT,
                    religiao TEXT,
                    classe INTEGER,
                    probabilidade REAL,
                    explicacao_lime TEXT,
                    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS memes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    imagem_path TEXT,
                    texto_extraido TEXT,
                    classe INTEGER,
                    probabilidade REAL,
                    religiao TEXT,
                    explicacao_lime TEXT,
                    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS alertas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    noticia_id INTEGER,
                    tipo TEXT,
                    mensagem TEXT,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (noticia_id) REFERENCES noticias (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_noticias_data 
                ON noticias(data_coleta);
                
                CREATE INDEX IF NOT EXISTS idx_noticias_classe 
                ON noticias(classe);
                
                CREATE INDEX IF NOT EXISTS idx_noticias_religiao 
                ON noticias(religiao);
                
                CREATE INDEX IF NOT EXISTS idx_noticias_pais 
                ON noticias(pais);
            """)
            
            self.conn.commit()
            logger.info("Banco de dados inicializado com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
            raise
    
    def insert_noticia(self, noticia_data: Dict) -> int:
        """
        Insere uma nova notícia no banco de dados.
        
        Args:
            noticia_data: Dicionário com dados da notícia
            
        Returns:
            ID da notícia inserida
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO noticias 
                (titulo, texto, url, fonte, pais, cidade, religiao, 
                 classe, probabilidade, explicacao_lime)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                noticia_data.get('titulo'),
                noticia_data.get('texto'),
                noticia_data.get('url'),
                noticia_data.get('fonte'),
                noticia_data.get('pais'),
                noticia_data.get('cidade'),
                noticia_data.get('religiao'),
                noticia_data.get('classe'),
                noticia_data.get('probabilidade'),
                noticia_data.get('explicacao_lime')
            ))
            
            self.conn.commit()
            noticia_id = cursor.lastrowid
            logger.info(f"Notícia inserida com ID: {noticia_id}")
            return noticia_id
            
        except Exception as e:
            logger.error(f"Erro ao inserir notícia: {str(e)}")
            raise
    
    def get_noticias(self, filters: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
        """
        Recupera notícias do banco de dados com filtros opcionais.
        
        Args:
            filters: Dicionário com filtros (religiao, pais, classe, data_inicio, data_fim)
            limit: Limite de registros
            
        Returns:
            Lista de notícias
        """
        try:
            query = "SELECT * FROM noticias WHERE 1=1"
            params = []
            
            if filters:
                if 'religiao' in filters:
                    query += " AND religiao = ?"
                    params.append(filters['religiao'])
                
                if 'pais' in filters:
                    query += " AND pais = ?"
                    params.append(filters['pais'])
                
                if 'classe' in filters:
                    query += " AND classe = ?"
                    params.append(filters['classe'])
                
                if 'data_inicio' in filters:
                    query += " AND data_coleta >= ?"
                    params.append(filters['data_inicio'])
                
                if 'data_fim' in filters:
                    query += " AND data_coleta <= ?"
                    params.append(filters['data_fim'])
            
            query += " ORDER BY data_coleta DESC LIMIT ?"
            params.append(limit)
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Erro ao recuperar notícias: {str(e)}")
            raise
    
    def get_statistics(self) -> Dict:
        """
        Calcula estatísticas gerais do monitoramento.
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            cursor = self.conn.cursor()
            
            # Total de notícias
            cursor.execute("SELECT COUNT(*) as total FROM noticias")
            total = cursor.fetchone()['total']
            
            # Total de intolerância
            cursor.execute("SELECT COUNT(*) as total FROM noticias WHERE classe = 1")
            intolerancia = cursor.fetchone()['total']
            
            # Última atualização
            cursor.execute("SELECT MAX(data_coleta) as ultima FROM noticias")
            ultima = cursor.fetchone()['ultima']
            
            # Por religião
            cursor.execute("""
                SELECT religiao, COUNT(*) as total 
                FROM noticias 
                WHERE classe = 1 
                GROUP BY religiao 
                ORDER BY total DESC
            """)
            por_religiao = [dict(row) for row in cursor.fetchall()]
            
            # Por país
            cursor.execute("""
                SELECT pais, COUNT(*) as total 
                FROM noticias 
                WHERE classe = 1 
                GROUP BY pais 
                ORDER BY total DESC
            """)
            por_pais = [dict(row) for row in cursor.fetchall()]
            
            return {
                "total_noticias": total,
                "total_intolerancia": intolerancia,
                "total_nao_intolerancia": total - intolerancia,
                "ultima_atualizacao": ultima,
                "por_religiao": por_religiao,
                "por_pais": por_pais
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {str(e)}")
            raise
    
    def get_alertas(self) -> List[Dict]:
        """
        Recupera alertas gerados (notícias com probabilidade > 0.90).
        
        Returns:
            Lista de alertas
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM noticias 
                WHERE probabilidade > 0.90 AND classe = 1
                ORDER BY probabilidade DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Erro ao recuperar alertas: {str(e)}")
            raise
    
    def close(self) -> None:
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()
            logger.info("Conexão com banco de dados fechada")


# Singleton
db_instance = None

def get_database() -> Database:
    """
    Retorna a instância única do banco de dados.
    
    Returns:
        Instância do Database
    """
    global db_instance
    if db_instance is None:
        db_instance = Database()
    return db_instance