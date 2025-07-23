import logging
import os
from datetime import datetime

def setup_logger(name='devflow', level=logging.INFO):
    """Configura o sistema de logging da aplicação"""
    
    # Cria diretório de logs se não existir
    logs_dir = 'logs'
    os.makedirs(logs_dir, exist_ok=True)
    
    # Nome do arquivo de log com data
    log_filename = f"{logs_dir}/devflow_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configura o formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configura o logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove handlers existentes para evitar duplicação
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger