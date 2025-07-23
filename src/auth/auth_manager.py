import bcrypt
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from ..database.models import User
from ..database.connection import db_manager
from config import config

class AuthManager:
    """Gerenciador de autenticação da aplicação"""
    
    def __init__(self):
        self.logger = logging.getLogger('devflow.auth')
        self.current_user = None
    
    def hash_password(self, password: str) -> str:
        """Gera hash da senha usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica se a senha corresponde ao hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_token(self, user_id: int) -> str:
        """Gera token JWT para o usuário"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[int]:
        """Verifica token JWT e retorna user_id se válido"""
        try:
            payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
            return payload.get('user_id')
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expirado")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Token inválido")
            return None
    
    def register_user(self, username: str, email: str, password: str, full_name: str) -> bool:
        """Registra um novo usuário"""
        session = db_manager.get_session()
        try:
            # Verifica se usuário já existe
            existing_user = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                self.logger.warning(f"Tentativa de registro com username/email já existente: {username}/{email}")
                return False
            
            # Cria novo usuário
            hashed_password = self.hash_password(password)
            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                full_name=full_name
            )
            
            session.add(new_user)
            session.commit()
            
            self.logger.info(f"Usuário registrado com sucesso: {username}")
            return True
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Erro ao registrar usuário: {e}")
            return False
        finally:
            session.close()
    
    def login(self, username: str, password: str) -> Optional[str]:
        """Autentica usuário e retorna token JWT"""
        session = db_manager.get_session()
        try:
            # Busca usuário
            user = session.query(User).filter(
                (User.username == username) | (User.email == username)
            ).filter(User.is_active == True).first()
            
            if not user:
                self.logger.warning(f"Tentativa de login com usuário inexistente: {username}")
                return None
            
            # Verifica senha
            if not self.verify_password(password, user.password_hash):
                self.logger.warning(f"Tentativa de login com senha incorreta: {username}")
                return None
            
            # Gera token
            token = self.generate_token(user.id)
            self.current_user = user
            
            self.logger.info(f"Login realizado com sucesso: {username}")
            return token
            
        except Exception as e:
            self.logger.error(f"Erro durante login: {e}")
            return None
        finally:
            session.close()
    
    def logout(self):
        """Realiza logout do usuário atual"""
        if self.current_user:
            self.logger.info(f"Logout realizado: {self.current_user.username}")
            self.current_user = None
    
    def get_current_user(self) -> Optional[User]:
        """Retorna o usuário atualmente logado"""
        return self.current_user
    
    def load_user_from_token(self, token: str) -> bool:
        """Carrega usuário a partir de um token válido"""
        user_id = self.verify_token(token)
        if not user_id:
            return False
        
        session = db_manager.get_session()
        try:
            user = session.query(User).filter(
                User.id == user_id,
                User.is_active == True
            ).first()
            
            if user:
                self.current_user = user
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar usuário do token: {e}")
            return False
        finally:
            session.close()
    
    def is_authenticated(self) -> bool:
        """Verifica se há um usuário autenticado"""
        return self.current_user is not None

# Instância global do gerenciador de autenticação
auth_manager = AuthManager()