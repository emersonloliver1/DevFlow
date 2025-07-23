from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base
import enum

class ProjectStatus(enum.Enum):
    """Status possíveis para projetos"""
    PROPOSTA = "proposta"
    ATIVO = "ativo"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"
    PAUSADO = "pausado"

class TransactionType(enum.Enum):
    """Tipos de transação financeira"""
    RECEITA = "receita"
    DESPESA = "despesa"

class TaskStatus(enum.Enum):
    """Status das tarefas no quadro kanban"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"

class TaskPriority(enum.Enum):
    """Prioridade das tarefas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class User(Base):
    """Modelo para usuários do sistema"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relacionamentos
    clients = relationship("Client", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    time_entries = relationship("TimeEntry", back_populates="user", cascade="all, delete-orphan")
    boards = relationship("Board", back_populates="user", cascade="all, delete-orphan")

class Client(Base):
    """Modelo para clientes"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    company = Column(String(100))
    address = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relacionamentos
    user = relationship("User", back_populates="clients")
    projects = relationship("Project", back_populates="client", cascade="all, delete-orphan")

class Project(Base):
    """Modelo para projetos"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    budget = Column(DECIMAL(10, 2))
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PROPOSTA)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    contract_drive_link = Column(Text)
    contract_file_name = Column(Text)
    contract_uploaded_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="projects")
    client = relationship("Client", back_populates="projects")
    transactions = relationship("Transaction", back_populates="project", cascade="all, delete-orphan")
    time_entries = relationship("TimeEntry", back_populates="project", cascade="all, delete-orphan")
    boards = relationship("Board", back_populates="project", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="project", cascade="all, delete-orphan")

class Transaction(Base):
    """Modelo para transações financeiras (receitas e despesas)"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # Pode ser nulo para despesas gerais
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    description = Column(String(200), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    category = Column(String(50))  # Ex: "Software", "Hardware", "Pagamento Cliente"
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="transactions")
    project = relationship("Project", back_populates="transactions")

class TimeEntry(Base):
    """Modelo para controle de tempo trabalhado"""
    __tablename__ = "time_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    description = Column(String(200), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)  # Duração em minutos
    hourly_rate = Column(DECIMAL(8, 2))  # Taxa por hora para este trabalho
    date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="time_entries")
    project = relationship("Project", back_populates="time_entries")

class Contract(Base):
    """Modelo para contratos/arquivos associados aos projetos"""
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    description = Column(Text)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    project = relationship("Project", back_populates="contracts")

class Board(Base):
    """Modelo para quadros kanban"""
    __tablename__ = "boards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="boards")
    project = relationship("Project", back_populates="boards")
    columns = relationship("BoardColumn", back_populates="board", cascade="all, delete-orphan", order_by="BoardColumn.position")

class BoardColumn(Base):
    """Modelo para colunas do quadro kanban"""
    __tablename__ = "board_columns"
    
    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    name = Column(String(50), nullable=False)
    position = Column(Integer, nullable=False)
    color = Column(String(7), default="#2196F3")  # Cor em hexadecimal
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan", order_by="Task.position")

class Task(Base):
    """Modelo para tarefas do quadro kanban"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    column_id = Column(Integer, ForeignKey("board_columns.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    position = Column(Integer, nullable=False)
    estimated_hours = Column(DECIMAL(5, 2))
    assigned_to = Column(String(100))  # Nome do responsável
    due_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    column = relationship("BoardColumn", back_populates="tasks")