import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from config import config

# Base para os modelos
Base = declarative_base()

class DatabaseManager:
    """Gerenciador de conexão com o banco de dados"""
    
    def __init__(self):
        self.logger = logging.getLogger('devflow.database')
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Inicializa o engine do SQLAlchemy"""
        try:
            self.engine = create_engine(
                config.DATABASE_URL,
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self.logger.info("Engine do banco de dados inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar engine do banco: {e}")
            raise
    
    def test_connection(self):
        """Testa a conexão com o banco de dados"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                self.logger.info("Conexão com banco de dados testada com sucesso")
                return True
        except SQLAlchemyError as e:
            self.logger.error(f"Erro na conexão com banco de dados: {e}")
            return False
    
    def get_session(self):
        """Retorna uma nova sessão do banco de dados"""
        return self.SessionLocal()
    
    def create_tables(self):
        """Cria todas as tabelas definidas nos modelos"""
        try:
            # Os modelos já foram importados no topo do arquivo
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("Tabelas criadas com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao criar tabelas: {e}")
            raise
    
    def run_migrations(self):
        """Executa migrações do banco de dados"""
        try:
            # Por enquanto, apenas cria as tabelas
            # Em uma versão futura, pode usar Alembic para migrações mais complexas
            self.create_tables()
            self.logger.info("Migrações executadas com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao executar migrações: {e}")
            raise

# Instância global do gerenciador
db_manager = DatabaseManager()