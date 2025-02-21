import pandas as pd
import mysql.connector
from mysql.connector import Error
from typing import Iterator
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_csv_in_chunks(filename: str, chunksize: int = 10000) -> Iterator[pd.DataFrame]:
    """
    Processa o arquivo CSV em chunks para economizar memória.
    """
    try:
        for chunk in pd.read_csv(filename, chunksize=chunksize):
            chunk['event_date'] = pd.to_datetime(chunk['event_date'])
            yield chunk
    except Exception as e:
        logger.error(f"Erro ao ler o arquivo CSV: {e}")
        raise

def create_table_if_not_exists(cursor) -> None:
    """
    Cria a tabela se ela não existir.
    Inclui índices para otimização de consultas comuns.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_events (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        event_date DATETIME,
        session VARCHAR(255),
        user VARCHAR(255),
        page_type VARCHAR(50),
        event_type VARCHAR(50),
        product BIGINT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_event_date (event_date),
        INDEX idx_user (user),
        INDEX idx_session (session),
        INDEX idx_page_type (page_type),
        INDEX idx_event_type (event_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    try:
        cursor.execute(create_table_query)
        logger.info("Tabela criada ou já existente")
    except Error as e:
        logger.error(f"Erro ao criar tabela: {e}")
        raise

def insert_data_batch(connection, cursor, chunk: pd.DataFrame) -> None:
    """
    Insere dados em lotes usando executemany.
    """
    insert_query = """
    INSERT INTO user_events 
    (event_date, session, user, page_type, event_type, product)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        values = chunk.values.tolist()
        cursor.executemany(insert_query, values)
        connection.commit()
        logger.info(f"Inseridos {len(values)} registros com sucesso")
    except Error as e:
        logger.error(f"Erro ao inserir lote: {e}")
        connection.rollback()
        raise

def import_csv_to_mysql(host: str, user: str, password: str, database: str, csv_file: str, 
                       chunksize: int = 10000) -> None:
    """
    Função principal que coordena a importação dos dados.
    """
    start_time = datetime.now()
    total_records = 0

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            use_unicode=True,
            buffered=True
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            create_table_if_not_exists(cursor)
            
            for chunk in process_csv_in_chunks(csv_file, chunksize):
                insert_data_batch(connection, cursor, chunk)
                total_records += len(chunk)
                
            cursor.execute("OPTIMIZE TABLE user_events")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Importação concluída! Tempo total: {duration:.2f} segundos")
            logger.info(f"Total de registros importados: {total_records}")

    except Error as e:
        logger.error(f"Erro na conexão MySQL: {e}")
        raise
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("Conexão MySQL fechada")

if __name__ == "__main__":
    
    mysql_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '01280415',
        'database': 'autodoc'
    }
    
    
    config = {
        'csv_file': 'data.csv',  
        'chunksize': 10000        
    }
    
    try:
        import_csv_to_mysql(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database'],
            csv_file=config['csv_file'],
            chunksize=config['chunksize']
        )
    except Exception as e:
        logger.error(f"Erro durante a importação: {e}")