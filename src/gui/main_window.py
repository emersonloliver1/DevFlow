import customtkinter as ctk
import logging
from typing import Optional
from config import config
from ..auth.auth_manager import auth_manager
from .login_window import LoginWindow
from .dashboard import Dashboard
from .clients_frame import ClientsFrame
from .projects_frame import ProjectsFrame
from .finances_frame import FinancesFrame
from .timesheet_frame import TimesheetFrame
from .reports_frame import ReportsFrame
from .boards_frame import BoardsFrame
from .help_window import HelpWindow
import tkinter as tk
from datetime import datetime

class MainWindow:
    """Janela principal da aplicação DevFlow - Interface Modernizada"""
    
    def __init__(self):
        self.logger = logging.getLogger('devflow.gui')
        self.root = None
        self.current_frame = None
        self.sidebar_frame = None
        self.main_frame = None
        self.header_frame = None
        self.status_bar = None
        
        # Frames da aplicação
        self.dashboard_frame = None
        self.clients_frame = None
        self.projects_frame = None
        self.boards_frame = None
        self.finances_frame = None
        self.timesheet_frame = None
        self.reports_frame = None
        self.help_window = None
        
        # Configurações de tema
        self.current_theme = "dark"  # dark ou light
        self.sidebar_collapsed = False
        
        # Cores do tema
        self.themes = {
            "dark": {
                "bg_primary": "#1a1a1a",
                "bg_secondary": "#2d2d2d",
                "bg_tertiary": "#3d3d3d",
                "text_primary": "#ffffff",
                "text_secondary": "#b0b0b0",
                "accent": "#00d4aa",
                "accent_hover": "#00b894",
                "danger": "#e74c3c",
                "warning": "#f39c12",
                "success": "#27ae60",
                "info": "#3498db"
            },
            "light": {
                "bg_primary": "#ffffff",
                "bg_secondary": "#f8f9fa",
                "bg_tertiary": "#e9ecef",
                "text_primary": "#212529",
                "text_secondary": "#6c757d",
                "accent": "#007bff",
                "accent_hover": "#0056b3",
                "danger": "#dc3545",
                "warning": "#ffc107",
                "success": "#28a745",
                "info": "#17a2b8"
            }
        }
        
        self._setup_window()
    
    def _setup_window(self):
        """Configura a janela principal com design moderno"""
        # Configurar tema customizado
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme("blue")
        
        # Criar janela principal
        self.root = ctk.CTk()
        self.root.title("DevFlow - Sistema de Gestão de Projetos")
        self.root.geometry("1600x900")
        self.root.minsize(1400, 800)
        
        # Configurar ícone da janela (se disponível)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # Configurar cores da janela
        theme = self.themes[self.current_theme]
        self.root.configure(fg_color=theme["bg_primary"])
        
        # Configurar grid principal
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Criar componentes da interface
        self._create_header()
        self._create_sidebar()
        self._create_main_area()
        self._create_status_bar()
        
        # Configurar eventos
        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Control-t>", self._toggle_theme)
        self.root.bind("<Control-b>", self._toggle_sidebar)
        
        # Centralizar janela na tela
        self._center_window()
        
        # Configura o protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_header(self):
        """Cria o cabeçalho moderno da aplicação"""
        theme = self.themes[self.current_theme]
        
        self.header_frame = ctk.CTkFrame(
            self.root,
            height=60,
            fg_color=theme["bg_secondary"],
            corner_radius=0
        )
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_propagate(False)
        
        # Logo e título
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🚀 DevFlow",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=theme["accent"]
        )
        title_label.pack(side="left")
        
        version_label = ctk.CTkLabel(
            title_frame,
            text="v2.0",
            font=ctk.CTkFont(size=12),
            text_color=theme["text_secondary"]
        )
        version_label.pack(side="left", padx=(10, 0))
        
        # Área central com informações
        info_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=20)
        
        # Data e hora atual
        current_time = datetime.now().strftime("%d/%m/%Y - %H:%M")
        time_label = ctk.CTkLabel(
            info_frame,
            text=f"📅 {current_time}",
            font=ctk.CTkFont(size=12),
            text_color=theme["text_secondary"]
        )
        time_label.pack(side="left", padx=(0, 20))
        
        # Controles do usuário
        controls_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=2, sticky="e", padx=20, pady=10)
        
        # Botão de alternar tema
        theme_btn = ctk.CTkButton(
            controls_frame,
            text="🌙" if self.current_theme == "dark" else "☀️",
            width=40,
            height=40,
            command=self._toggle_theme,
            fg_color=theme["bg_tertiary"],
            hover_color=theme["accent"],
            font=ctk.CTkFont(size=16)
        )
        theme_btn.pack(side="right", padx=(5, 0))
        
        # Botão de colapsar sidebar
        sidebar_btn = ctk.CTkButton(
            controls_frame,
            text="◀" if not self.sidebar_collapsed else "▶",
            width=40,
            height=40,
            command=self._toggle_sidebar,
            fg_color=theme["bg_tertiary"],
            hover_color=theme["accent"],
            font=ctk.CTkFont(size=12)
        )
        sidebar_btn.pack(side="right", padx=(5, 0))
        
        # Informações do usuário
        user_info = auth_manager.get_current_user()
        if user_info:
            user_label = ctk.CTkLabel(
                controls_frame,
                text=f"👤 {user_info.get('username', 'Usuário')}",
                font=ctk.CTkFont(size=12),
                text_color=theme["text_primary"]
            )
            user_label.pack(side="right", padx=(0, 15))
    
    def _create_status_bar(self):
        """Cria a barra de status na parte inferior"""
        theme = self.themes[self.current_theme]
        
        self.status_bar = ctk.CTkFrame(
            self.root,
            height=30,
            fg_color=theme["bg_secondary"],
            corner_radius=0
        )
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self.status_bar.grid_propagate(False)
        
        # Status da aplicação
        status_label = ctk.CTkLabel(
            self.status_bar,
            text="✅ Sistema operacional",
            font=ctk.CTkFont(size=10),
            text_color=theme["success"]
        )
        status_label.pack(side="left", padx=10, pady=5)
        
        # Informações adicionais
        info_label = ctk.CTkLabel(
            self.status_bar,
            text="Pressione F11 para tela cheia | Ctrl+T para alternar tema | Ctrl+B para sidebar",
            font=ctk.CTkFont(size=10),
            text_color=theme["text_secondary"]
        )
        info_label.pack(side="right", padx=10, pady=5)
    
    def _center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _toggle_fullscreen(self, event=None):
        """Alterna entre tela cheia e janela normal"""
        current_state = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not current_state)
    
    def _toggle_theme(self, event=None):
        """Alterna entre tema escuro e claro"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        ctk.set_appearance_mode(self.current_theme)
        self._refresh_interface()
    
    def _toggle_sidebar(self, event=None):
        """Colapsa/expande a sidebar"""
        self.sidebar_collapsed = not self.sidebar_collapsed
        if self.sidebar_collapsed:
            self.sidebar_frame.configure(width=80)
        else:
            self.sidebar_frame.configure(width=250)
        self._refresh_sidebar()
    
    def _refresh_interface(self):
        """Atualiza a interface com o novo tema"""
        theme = self.themes[self.current_theme]
        
        # Atualizar janela principal
        self.root.configure(fg_color=theme["bg_primary"])
        
        # Atualizar header
        if self.header_frame:
            self.header_frame.configure(fg_color=theme["bg_secondary"])
        
        # Atualizar sidebar
        if self.sidebar_frame:
            self.sidebar_frame.configure(fg_color=theme["bg_secondary"])
        
        # Atualizar status bar
        if self.status_bar:
            self.status_bar.configure(fg_color=theme["bg_secondary"])
        
        # Atualizar frame principal
        if self.main_frame:
            self.main_frame.configure(fg_color=theme["bg_primary"])
    
    def _refresh_sidebar(self):
        """Atualiza a sidebar com base no estado de colapso"""
        # Esta função será implementada quando atualizarmos a sidebar
        pass
    
    def _create_sidebar(self):
        """Cria a barra lateral moderna com navegação"""
        theme = self.themes[self.current_theme]
        
        self.sidebar_frame = ctk.CTkFrame(
            self.root, 
            width=250, 
            corner_radius=0,
            fg_color=theme["bg_secondary"]
        )
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_rowconfigure(10, weight=1)
        self.sidebar_frame.grid_propagate(False)
        
        # Seção do usuário
        user_section = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color=theme["bg_tertiary"],
            corner_radius=10
        )
        user_section.grid(row=0, column=0, padx=15, pady=20, sticky="ew")
        
        user_info = auth_manager.get_current_user()
        if user_info:
            user_avatar = ctk.CTkLabel(
                user_section,
                text="👤",
                font=ctk.CTkFont(size=24),
                text_color=theme["accent"]
            )
            user_avatar.pack(pady=(10, 5))
            
            user_name = ctk.CTkLabel(
                user_section,
                text=user_info.get('username', 'Usuário'),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=theme["text_primary"]
            )
            user_name.pack(pady=(0, 10))
        
        # Separador
        separator = ctk.CTkFrame(
            self.sidebar_frame,
            height=2,
            fg_color=theme["bg_tertiary"]
        )
        separator.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        
        # Botões de navegação modernos
        self.nav_buttons = {}
        
        nav_items = [
            ('dashboard', '📊', 'Dashboard', 'Visão geral do sistema'),
            ('clients', '👥', 'Clientes', 'Gerenciar clientes'),
            ('projects', '🚀', 'Projetos', 'Gerenciar projetos'),
            ('boards', '📋', 'Quadros', 'Quadros Kanban'),
            ('finances', '💰', 'Finanças', 'Controle financeiro'),
            ('timesheet', '⏰', 'Timesheet', 'Controle de tempo'),
            ('reports', '📈', 'Relatórios', 'Relatórios e análises'),
            ('help', '❓', 'Ajuda', 'Central de ajuda')
        ]
        
        for i, (key, icon, text, tooltip) in enumerate(nav_items):
            btn_frame = ctk.CTkFrame(
                self.sidebar_frame,
                fg_color="transparent"
            )
            btn_frame.grid(row=i+2, column=0, padx=15, pady=3, sticky="ew")
            
            self.nav_buttons[key] = ctk.CTkButton(
                btn_frame,
                text=f"{icon}  {text}" if not self.sidebar_collapsed else icon,
                command=lambda k=key: self.show_frame(k),
                anchor="w",
                height=45,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="transparent",
                hover_color=theme["accent"],
                text_color=theme["text_primary"],
                corner_radius=8
            )
            self.nav_buttons[key].pack(fill="x")
            
            # Adicionar tooltip (simulado com bind)
            self._create_tooltip(self.nav_buttons[key], tooltip)
        
        # Seção inferior com configurações
        bottom_section = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color="transparent"
        )
        bottom_section.grid(row=11, column=0, padx=15, pady=20, sticky="ew")
        
        # Botão de logout
        logout_btn = ctk.CTkButton(
            bottom_section,
            text="🚪 Sair",
            command=self._logout,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color=theme["danger"],
            hover_color="#c0392b",
            corner_radius=8
        )
        logout_btn.pack(fill="x", pady=(0, 10))
        
        # Informações da versão
        version_label = ctk.CTkLabel(
            bottom_section,
            text="DevFlow v2.0",
            font=ctk.CTkFont(size=10),
            text_color=theme["text_secondary"]
        )
        version_label.pack(pady=5)
    
    def _create_tooltip(self, widget, text):
        """Cria um tooltip simples para o widget"""
        def on_enter(event):
            # Implementação simples de tooltip
            pass
        
        def on_leave(event):
            pass
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _create_main_area(self):
        """Cria a área principal moderna onde serão exibidos os conteúdos"""
        theme = self.themes[self.current_theme]
        
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color=theme["bg_primary"],
            corner_radius=15
        )
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=15, pady=15)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Container interno com padding
        self.content_container = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.content_container.pack(fill="both", expand=True, padx=20, pady=20)
    
    def _update_nav_buttons(self, active_frame: str):
        """Atualiza o estado visual dos botões de navegação"""
        theme = self.themes[self.current_theme]
        
        for key, button in self.nav_buttons.items():
            if key == active_frame:
                button.configure(
                    fg_color=theme["accent"],
                    text_color="white"
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=theme["text_primary"]
                )
    
    def show_frame(self, frame_name):
        """Exibe o frame especificado"""
        # Limpa o container atual
        for widget in self.content_container.winfo_children():
            widget.pack_forget()
        
        # Exibe um indicador de carregamento
        loading_frame = ctk.CTkFrame(self.content_container)
        loading_frame.pack(fill="both", expand=True)
        
        loading_label = ctk.CTkLabel(
            loading_frame,
            text="Carregando...",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        loading_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Atualiza a UI para mostrar o indicador de carregamento
        self.content_container.update()
        
        # Inicializa o frame se ainda não existir
        if frame_name == "dashboard" and self.dashboard_frame is None:
            self.dashboard_frame = Dashboard(self.content_container)
        elif frame_name == "clients" and self.clients_frame is None:
            self.clients_frame = ClientsFrame(self.content_container)
        elif frame_name == "projects" and self.projects_frame is None:
            self.projects_frame = ProjectsFrame(self.content_container)
        elif frame_name == "boards" and self.boards_frame is None:
            self.boards_frame = BoardsFrame(self.content_container)
        elif frame_name == "finances" and self.finances_frame is None:
            self.finances_frame = FinancesFrame(self.content_container)
        elif frame_name == "timesheet" and self.timesheet_frame is None:
            self.timesheet_frame = TimesheetFrame(self.content_container)
        elif frame_name == "reports" and self.reports_frame is None:
            self.reports_frame = ReportsFrame(self.content_container)
        
        # Define o frame atual
        if frame_name == "dashboard":
            self.current_frame = self.dashboard_frame
        elif frame_name == "clients":
            self.current_frame = self.clients_frame
        elif frame_name == "projects":
            self.current_frame = self.projects_frame
        elif frame_name == "boards":
            self.current_frame = self.boards_frame
        elif frame_name == "finances":
            self.current_frame = self.finances_frame
        elif frame_name == "timesheet":
            self.current_frame = self.timesheet_frame
        elif frame_name == "reports":
            self.current_frame = self.reports_frame
        
        # Atualiza os botões de navegação
        self._update_nav_buttons(frame_name)
        
        # Remove o indicador de carregamento
        loading_frame.destroy()
        
        # Exibe o frame atual
        if self.current_frame:
            self.current_frame.show()
        
        # Atualiza dados se o frame tiver método refresh
        if self.current_frame and hasattr(self.current_frame, 'refresh'):
            self.current_frame.refresh()
    
    def _show_help(self):
        """Exibe a janela de ajuda"""
        if self.help_window is None:
            self.help_window = HelpWindow(self.root)
        self.help_window.show()
    
    def _logout(self):
        """Realiza logout e volta para a tela de login"""
        auth_manager.logout()
        self.root.destroy()
        self.show_login()
    
    def _on_closing(self):
        """Chamado quando a janela é fechada"""
        self.logger.info("Aplicação sendo fechada")
        auth_manager.logout()
        self.root.destroy()
    
    def show_login(self):
        """Exibe a janela de login"""
        login_window = LoginWindow(on_success=self._on_login_success)
        login_window.show()
    
    def _on_login_success(self):
        """Chamado quando o login é realizado com sucesso"""
        # Pré-inicializa o dashboard em segundo plano
        self.dashboard_frame = Dashboard(self.content_container)
        
        # Inicia o pré-carregamento dos frames mais utilizados em segundo plano
        self._preload_common_frames()
        
        self.root.deiconify()  # Mostra a janela principal
        self.show_frame("dashboard")  # Mostra o dashboard por padrão
    
    def _preload_common_frames(self):
        """Pré-carrega os frames mais utilizados em segundo plano"""
        import threading
        
        def preload():
            # Pré-carrega os frames mais comuns em segundo plano
            # para melhorar a experiência do usuário
            try:
                self.clients_frame = ClientsFrame(self.content_container)
                self.projects_frame = ProjectsFrame(self.content_container)
            except Exception as e:
                self.logger.error(f"Erro ao pré-carregar frames: {e}")
        
        # Inicia o pré-carregamento em uma thread separada
        preload_thread = threading.Thread(target=preload)
        preload_thread.daemon = True
        preload_thread.start()
    
    def run(self):
        """Inicia a aplicação"""
        # Esconde a janela principal inicialmente
        self.root.withdraw()
        
        # Mostra a tela de login
        self.show_login()
        
        # Inicia o loop principal
        self.root.mainloop()