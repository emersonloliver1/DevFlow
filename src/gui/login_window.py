import customtkinter as ctk
import tkinter.messagebox as messagebox
from typing import Callable
from ..auth.auth_manager import auth_manager
from config import config

class LoginWindow:
    """Janela de login da aplicação"""
    
    def __init__(self, on_success: Callable = None):
        self.on_success = on_success
        self.window = None
        self.username_entry = None
        self.password_entry = None
        self.login_button = None
        self.register_button = None
        
        # Variáveis para registro
        self.register_window = None
        self.reg_username_entry = None
        self.reg_email_entry = None
        self.reg_password_entry = None
        self.reg_confirm_password_entry = None
        self.reg_fullname_entry = None
    
    def _setup_window(self):
        """Configura a janela de login"""
        self.window = ctk.CTkToplevel()
        self.window.title(f"{config.APP_NAME} - Login")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        # Centraliza a janela
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"400x500+{x}+{y}")
        
        # Torna a janela modal
        self.window.transient()
        self.window.grab_set()
        
        # Configura o protocolo de fechamento
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_login_form(self):
        """Cria o formulário de login"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="DevFlow",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=(30, 10))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Sistema de Gestão para Freelancers",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Campo de usuário
        username_label = ctk.CTkLabel(main_frame, text="Usuário ou Email:")
        username_label.pack(pady=(10, 5))
        
        self.username_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Digite seu usuário ou email",
            width=300
        )
        self.username_entry.pack(pady=(0, 10))
        
        # Campo de senha
        password_label = ctk.CTkLabel(main_frame, text="Senha:")
        password_label.pack(pady=(10, 5))
        
        self.password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Digite sua senha",
            show="*",
            width=300
        )
        self.password_entry.pack(pady=(0, 20))
        
        # Botão de login
        self.login_button = ctk.CTkButton(
            main_frame,
            text="Entrar",
            command=self._handle_login,
            width=300,
            height=40
        )
        self.login_button.pack(pady=10)
        
        # Botão de registro
        self.register_button = ctk.CTkButton(
            main_frame,
            text="Criar Nova Conta",
            command=self._show_register,
            width=300,
            height=40,
            fg_color="transparent",
            border_width=2
        )
        self.register_button.pack(pady=10)
        
        # Bind Enter key para login
        self.window.bind('<Return>', lambda event: self._handle_login())
        
        # Foco inicial no campo de usuário
        self.username_entry.focus()
    
    def _handle_login(self):
        """Processa o login do usuário"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return
        
        # Desabilita o botão durante o login
        self.login_button.configure(state="disabled", text="Entrando...")
        
        # Tenta fazer login
        token = auth_manager.login(username, password)
        
        if token:
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            self.window.destroy()
            if self.on_success:
                self.on_success()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")
            self.login_button.configure(state="normal", text="Entrar")
            self.password_entry.delete(0, 'end')
            self.password_entry.focus()
    
    def _show_register(self):
        """Exibe a janela de registro"""
        self._setup_register_window()
        self._create_register_form()
    
    def _setup_register_window(self):
        """Configura a janela de registro"""
        self.register_window = ctk.CTkToplevel(self.window)
        self.register_window.title(f"{config.APP_NAME} - Criar Conta")
        self.register_window.geometry("450x600")
        self.register_window.resizable(False, False)
        
        # Centraliza a janela
        self.register_window.update_idletasks()
        x = (self.register_window.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.register_window.winfo_screenheight() // 2) - (600 // 2)
        self.register_window.geometry(f"450x600+{x}+{y}")
        
        # Torna a janela modal
        self.register_window.transient(self.window)
        self.register_window.grab_set()
    
    def _create_register_form(self):
        """Cria o formulário de registro"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.register_window)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="Criar Nova Conta",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Nome completo
        fullname_label = ctk.CTkLabel(main_frame, text="Nome Completo:")
        fullname_label.pack(pady=(10, 5))
        
        self.reg_fullname_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Digite seu nome completo",
            width=350
        )
        self.reg_fullname_entry.pack(pady=(0, 10))
        
        # Usuário
        username_label = ctk.CTkLabel(main_frame, text="Nome de Usuário:")
        username_label.pack(pady=(10, 5))
        
        self.reg_username_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Digite um nome de usuário",
            width=350
        )
        self.reg_username_entry.pack(pady=(0, 10))
        
        # Email
        email_label = ctk.CTkLabel(main_frame, text="Email:")
        email_label.pack(pady=(10, 5))
        
        self.reg_email_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Digite seu email",
            width=350
        )
        self.reg_email_entry.pack(pady=(0, 10))
        
        # Senha
        password_label = ctk.CTkLabel(main_frame, text="Senha:")
        password_label.pack(pady=(10, 5))
        
        self.reg_password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Digite uma senha",
            show="*",
            width=350
        )
        self.reg_password_entry.pack(pady=(0, 10))
        
        # Confirmar senha
        confirm_password_label = ctk.CTkLabel(main_frame, text="Confirmar Senha:")
        confirm_password_label.pack(pady=(10, 5))
        
        self.reg_confirm_password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Confirme sua senha",
            show="*",
            width=350
        )
        self.reg_confirm_password_entry.pack(pady=(0, 20))
        
        # Botões
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        register_btn = ctk.CTkButton(
            button_frame,
            text="Criar Conta",
            command=self._handle_register,
            width=150
        )
        register_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.register_window.destroy,
            width=150,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="left")
        
        # Foco inicial
        self.reg_fullname_entry.focus()
    
    def _handle_register(self):
        """Processa o registro do usuário"""
        full_name = self.reg_fullname_entry.get().strip()
        username = self.reg_username_entry.get().strip()
        email = self.reg_email_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_password_entry.get()
        
        # Validações
        if not all([full_name, username, email, password, confirm_password]):
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return
        
        if password != confirm_password:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return
        
        if len(password) < 6:
            messagebox.showerror("Erro", "A senha deve ter pelo menos 6 caracteres.")
            return
        
        if "@" not in email:
            messagebox.showerror("Erro", "Por favor, digite um email válido.")
            return
        
        # Tenta registrar
        success = auth_manager.register_user(username, email, password, full_name)
        
        if success:
            messagebox.showinfo("Sucesso", "Conta criada com sucesso! Você já pode fazer login.")
            self.register_window.destroy()
        else:
            messagebox.showerror("Erro", "Erro ao criar conta. Usuário ou email já existem.")
    
    def _on_closing(self):
        """Chamado quando a janela é fechada"""
        import sys
        sys.exit(0)
    
    def show(self):
        """Exibe a janela de login"""
        self._setup_window()
        self._create_login_form()