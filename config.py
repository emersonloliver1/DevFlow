import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Configurações da aplicação DevFlow"""
    
    # Configurações do banco de dados
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Configurações de autenticação
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    # Configurações da aplicação
    APP_NAME = "DevFlow"
    APP_VERSION = "1.0.0"
    
    # Configurações de interface
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    THEME_MODE = "dark"  # "light" ou "dark"
    COLOR_THEME = "blue"  # "blue", "green", "dark-blue"
    
    # Configurações de arquivos
    UPLOAD_FOLDER = "uploads"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}
    
    # Configurações de relatórios
    REPORTS_FOLDER = "reports"
    
    @classmethod
    def validate_config(cls):
        """Valida se as configurações essenciais estão definidas"""
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL não está definida no arquivo .env")
        
        # Cria diretórios necessários
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(cls.REPORTS_FOLDER, exist_ok=True)

# Instância global de configuração
config = Config()