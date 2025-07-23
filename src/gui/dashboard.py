import customtkinter as ctk
import threading
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from ..database.connection import db_manager
from ..database.models import Project, Transaction, TimeEntry, TransactionType, ProjectStatus
from ..auth.auth_manager import auth_manager

class Dashboard:
    """Dashboard principal da aplicação"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.stats_frame = None
        self.charts_frame = None
        self.recent_frame = None
        self.loading_indicators = {}
        
        # Sistema de cache para dados
        self.cache = {
            "stats": {
                "data": None,
                "timestamp": None,
                "valid_time": 300  # 5 minutos em segundos
            },
            "activities": {
                "data": None,
                "timestamp": None,
                "valid_time": 300  # 5 minutos em segundos
            },
            "projects": {
                "data": None,
                "timestamp": None,
                "valid_time": 300  # 5 minutos em segundos
            }
        }
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets do dashboard"""
        self.frame = ctk.CTkScrollableFrame(self.parent)
        self.frame.pack(fill="both", expand=True)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            self.frame,
            text="📊 Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Frame de estatísticas
        self._create_stats_section()
        
        # Frame de atividades recentes
        self._create_recent_activities()
        
        # Frame de projetos ativos
        self._create_active_projects()
    
    def _create_stats_section(self):
        """Cria a seção de estatísticas"""
        self.stats_frame = ctk.CTkFrame(self.frame)
        self.stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Título da seção
        stats_title = ctk.CTkLabel(
            self.stats_frame,
            text="Resumo Financeiro",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        stats_title.grid(row=0, column=0, columnspan=4, pady=(15, 10))
        
        # Cards de estatísticas
        self.total_receivable_card = self._create_stat_card(
            self.stats_frame, "💰 A Receber", "R$ 0,00", "#2196F3"
        )
        self.total_receivable_card.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.monthly_income_card = self._create_stat_card(
            self.stats_frame, "📈 Recebido (Mês)", "R$ 0,00", "#4CAF50"
        )
        self.monthly_income_card.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        self.monthly_expenses_card = self._create_stat_card(
            self.stats_frame, "📉 Despesas (Mês)", "R$ 0,00", "#FF5722"
        )
        self.monthly_expenses_card.grid(row=1, column=2, padx=10, pady=10, sticky="ew")
        
        self.monthly_hours_card = self._create_stat_card(
            self.stats_frame, "⏰ Horas (Mês)", "0h", "#9C27B0"
        )
        self.monthly_hours_card.grid(row=1, column=3, padx=10, pady=10, sticky="ew")
    
    def _create_stat_card(self, parent, title, value, color):
        """Cria um card de estatística"""
        card = ctk.CTkFrame(parent, fg_color=color)
        card.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        )
        title_label.grid(row=0, column=0, pady=(15, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        value_label.grid(row=1, column=0, pady=(0, 15))
        
        # Armazena o label do valor para atualização posterior
        card.value_label = value_label
        
        # Adiciona um indicador de carregamento (inicialmente oculto)
        loading_label = ctk.CTkLabel(
            card,
            text="Carregando...",
            font=ctk.CTkFont(size=10),
            text_color="white"
        )
        loading_label.grid(row=2, column=0, pady=(0, 5))
        loading_label.grid_remove()  # Inicialmente oculto
        
        # Armazena o indicador de carregamento
        card.loading_label = loading_label
        
        return card
    
    def _create_recent_activities(self):
        """Cria a seção de atividades recentes"""
        self.recent_frame = ctk.CTkFrame(self.frame)
        self.recent_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        self.recent_frame.grid_columnconfigure(0, weight=1)
        
        # Título
        recent_title = ctk.CTkLabel(
            self.recent_frame,
            text="📋 Atividades Recentes",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        recent_title.grid(row=0, column=0, pady=(15, 10), sticky="w", padx=15)
        
        # Lista de atividades
        self.activities_list = ctk.CTkScrollableFrame(self.recent_frame, height=200)
        self.activities_list.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.activities_list.grid_columnconfigure(0, weight=1)
        
        # Indicador de carregamento para atividades
        self.loading_indicators["activities"] = ctk.CTkLabel(
            self.activities_list,
            text="Carregando atividades...",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.loading_indicators["activities"].grid(row=0, column=0, pady=20)
        self.loading_indicators["activities"].grid_remove()  # Inicialmente oculto
    
    def _create_active_projects(self):
        """Cria a seção de projetos ativos"""
        self.projects_frame = ctk.CTkFrame(self.frame)
        self.projects_frame.grid(row=3, column=0, sticky="ew")
        self.projects_frame.grid_columnconfigure(0, weight=1)
        
        # Título
        projects_title = ctk.CTkLabel(
            self.projects_frame,
            text="🚀 Projetos Ativos",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        projects_title.grid(row=0, column=0, pady=(15, 10), sticky="w", padx=15)
        
        # Lista de projetos
        self.projects_list = ctk.CTkScrollableFrame(self.projects_frame, height=200)
        self.projects_list.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.projects_list.grid_columnconfigure(0, weight=1)
        
        # Indicador de carregamento para projetos
        self.loading_indicators["projects"] = ctk.CTkLabel(
            self.projects_list,
            text="Carregando projetos...",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.loading_indicators["projects"].grid(row=0, column=0, pady=20)
        self.loading_indicators["projects"].grid_remove()  # Inicialmente oculto
    
    def _show_loading(self, section):
        """Exibe o indicador de carregamento para a seção especificada"""
        if section == "stats":
            for card in [self.total_receivable_card, self.monthly_income_card, 
                         self.monthly_expenses_card, self.monthly_hours_card]:
                card.loading_label.grid()  # Exibe o indicador de carregamento
        elif section in self.loading_indicators:
            # Limpa a lista antes de mostrar o indicador
            if section == "activities":
                for widget in self.activities_list.winfo_children():
                    if widget != self.loading_indicators["activities"]:
                        widget.destroy()
            elif section == "projects":
                for widget in self.projects_list.winfo_children():
                    if widget != self.loading_indicators["projects"]:
                        widget.destroy()
            
            self.loading_indicators[section].grid()  # Exibe o indicador
        
        # Atualiza a UI
        self.frame.update()
    
    def _hide_loading(self, section):
        """Esconde o indicador de carregamento para a seção especificada"""
        if section == "stats":
            for card in [self.total_receivable_card, self.monthly_income_card, 
                         self.monthly_expenses_card, self.monthly_hours_card]:
                card.loading_label.grid_remove()  # Esconde o indicador de carregamento
        elif section in self.loading_indicators:
            self.loading_indicators[section].grid_remove()  # Esconde o indicador
    
    def _update_statistics_async(self):
        """Atualiza as estatísticas do dashboard de forma assíncrona"""
        # Verifica se há dados em cache válidos
        if self._is_cache_valid("stats"):
            # Usa dados do cache
            self.frame.after(0, lambda: self._update_stats_ui(*self.cache["stats"]["data"]))
            return
        
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            # Data atual e início do mês
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Total a receber (projetos ativos - total recebido)
            total_budget = session.query(func.sum(Project.budget)).filter(
                Project.user_id == user.id,
                Project.status.in_([ProjectStatus.ATIVO, ProjectStatus.PROPOSTA])
            ).scalar() or 0
            
            total_received = session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user.id,
                Transaction.type == TransactionType.RECEITA
            ).scalar() or 0
            
            total_receivable = total_budget - total_received
            
            # Recebido no mês
            monthly_income = session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user.id,
                Transaction.type == TransactionType.RECEITA,
                Transaction.date >= month_start
            ).scalar() or 0
            
            # Despesas no mês
            monthly_expenses = session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user.id,
                Transaction.type == TransactionType.DESPESA,
                Transaction.date >= month_start
            ).scalar() or 0
            
            # Horas trabalhadas no mês
            monthly_minutes = session.query(func.sum(TimeEntry.duration_minutes)).filter(
                TimeEntry.user_id == user.id,
                TimeEntry.date >= month_start
            ).scalar() or 0
            
            monthly_hours = monthly_minutes / 60 if monthly_minutes else 0
            
            # Armazena os dados no cache
            self._update_cache("stats", (total_receivable, monthly_income, monthly_expenses, monthly_hours))
            
            # Atualiza os cards na thread principal
            self.frame.after(0, lambda: self._update_stats_ui(
                total_receivable, monthly_income, monthly_expenses, monthly_hours
            ))
            
        except Exception as e:
            print(f"Erro ao carregar estatísticas: {e}")
        finally:
            session.close()
    
    def _update_stats_ui(self, total_receivable, monthly_income, monthly_expenses, monthly_hours):
        """Atualiza a UI com as estatísticas carregadas"""
        self.total_receivable_card.value_label.configure(
            text=f"R$ {total_receivable:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        )
        
        self.monthly_income_card.value_label.configure(
            text=f"R$ {monthly_income:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        )
        
        self.monthly_expenses_card.value_label.configure(
            text=f"R$ {monthly_expenses:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        )
        
        self.monthly_hours_card.value_label.configure(
            text=f"{monthly_hours:.1f}h"
        )
        
        # Esconde o indicador de carregamento
        self._hide_loading("stats")
    
    def _update_recent_activities_async(self):
        """Atualiza as atividades recentes de forma assíncrona"""
        # Verifica se há dados em cache válidos
        if self._is_cache_valid("activities"):
            # Usa dados do cache
            self.frame.after(0, lambda: self._update_activities_ui(*self.cache["activities"]["data"]))
            return
        
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            # Busca as transações mais recentes
            recent_transactions = session.query(Transaction).filter(
                Transaction.user_id == user.id
            ).order_by(Transaction.date.desc()).limit(5).all()
            
            # Busca os registros de tempo mais recentes
            recent_time_entries = session.query(TimeEntry).filter(
                TimeEntry.user_id == user.id
            ).order_by(TimeEntry.date.desc()).limit(5).all()
            
            # Armazena os dados no cache
            self._update_cache("activities", (recent_transactions, recent_time_entries))
            
            # Atualiza a UI na thread principal
            self.frame.after(0, lambda: self._update_activities_ui(
                recent_transactions, recent_time_entries
            ))
            
        except Exception as e:
            print(f"Erro ao carregar atividades recentes: {e}")
        finally:
            session.close()
    
    def _update_activities_ui(self, recent_transactions, recent_time_entries):
        """Atualiza a UI com as atividades recentes carregadas"""
        # Limpa a lista de atividades
        for widget in self.activities_list.winfo_children():
            if widget != self.loading_indicators["activities"]:
                widget.destroy()
        
        # Adiciona as transações recentes
        row = 0
        for transaction in recent_transactions:
            activity_frame = ctk.CTkFrame(self.activities_list, fg_color="transparent")
            activity_frame.grid(row=row, column=0, sticky="ew", pady=5)
            activity_frame.grid_columnconfigure(1, weight=1)
            
            icon = "💰" if transaction.type == TransactionType.RECEITA else "💸"
            icon_label = ctk.CTkLabel(
                activity_frame,
                text=icon,
                font=ctk.CTkFont(size=16)
            )
            icon_label.grid(row=0, column=0, padx=(0, 10))
            
            desc_label = ctk.CTkLabel(
                activity_frame,
                text=f"{transaction.description}",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            desc_label.grid(row=0, column=1, sticky="w")
            
            date_label = ctk.CTkLabel(
                activity_frame,
                text=transaction.date.strftime("%d/%m/%Y"),
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            date_label.grid(row=0, column=2, padx=10)
            
            row += 1
        
        # Adiciona os registros de tempo recentes
        for entry in recent_time_entries:
            activity_frame = ctk.CTkFrame(self.activities_list, fg_color="transparent")
            activity_frame.grid(row=row, column=0, sticky="ew", pady=5)
            activity_frame.grid_columnconfigure(1, weight=1)
            
            icon_label = ctk.CTkLabel(
                activity_frame,
                text="⏱️",
                font=ctk.CTkFont(size=16)
            )
            icon_label.grid(row=0, column=0, padx=(0, 10))
            
            desc_label = ctk.CTkLabel(
                activity_frame,
                text=f"{entry.description}",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            desc_label.grid(row=0, column=1, sticky="w")
            
            date_label = ctk.CTkLabel(
                activity_frame,
                text=entry.date.strftime("%d/%m/%Y"),
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            date_label.grid(row=0, column=2, padx=10)
            
            row += 1
        
        if row == 0:
            no_data_label = ctk.CTkLabel(
                self.activities_list,
                text="Nenhuma atividade recente",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            no_data_label.grid(row=0, column=0, pady=20)
        
        # Esconde o indicador de carregamento
        self._hide_loading("activities")
    
    def _update_active_projects_async(self):
        """Atualiza os projetos ativos de forma assíncrona"""
        # Verifica se há dados em cache válidos
        if self._is_cache_valid("projects"):
            # Usa dados do cache
            self.frame.after(0, lambda: self._update_projects_ui(self.cache["projects"]["data"]))
            return
        
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            # Busca projetos ativos com relacionamentos carregados
            from sqlalchemy.orm import joinedload
            active_projects = session.query(Project).options(
                joinedload(Project.client)
            ).filter(
                Project.user_id == user.id,
                Project.status == ProjectStatus.ATIVO
            ).all()
            
            # Armazena os dados no cache
            self._update_cache("projects", active_projects)
            
            # Atualiza a UI na thread principal
            self.frame.after(0, lambda: self._update_projects_ui(active_projects))
            
        except Exception as e:
            print(f"Erro ao carregar projetos ativos: {e}")
        finally:
            session.close()
    
    def _update_projects_ui(self, active_projects):
        """Atualiza a UI com os projetos ativos carregados"""
        # Limpa a lista de projetos
        for widget in self.projects_list.winfo_children():
            if widget != self.loading_indicators["projects"]:
                widget.destroy()
        
        # Adiciona os projetos ativos
        for i, project in enumerate(active_projects):
            project_frame = ctk.CTkFrame(self.projects_list)
            project_frame.grid(row=i, column=0, sticky="ew", pady=5, padx=5)
            project_frame.grid_columnconfigure(0, weight=1)
            
            # Nome do projeto
            name_label = ctk.CTkLabel(
                project_frame,
                text=project.name,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            name_label.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))
            
            # Cliente
            client_label = ctk.CTkLabel(
                project_frame,
                text=f"Cliente: {project.client.name}",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            client_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))
            
            # Orçamento
            if project.budget:
                budget_text = f"R$ {project.budget:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                budget_label = ctk.CTkLabel(
                    project_frame,
                    text=budget_text,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#2196F3"
                )
                budget_label.grid(row=0, column=1, rowspan=2, padx=15, pady=10)
        
        if not active_projects:
            no_data_label = ctk.CTkLabel(
                self.projects_list,
                text="Nenhum projeto ativo",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            no_data_label.grid(row=0, column=0, pady=20)
        
        # Esconde o indicador de carregamento
        self._hide_loading("projects")
    
    def show(self):
        """Exibe o dashboard"""
        self.frame.pack(fill="both", expand=True)
    
    def hide(self):
        """Esconde o dashboard"""
        self.frame.pack_forget()
    
    def refresh(self):
        """Atualiza os dados do dashboard de forma assíncrona"""
        # Exibe os indicadores de carregamento
        self._show_loading("stats")
        self._show_loading("activities")
        self._show_loading("projects")
        
        # Atualiza as estatísticas em uma thread separada
        stats_thread = threading.Thread(target=self._update_statistics_async)
        stats_thread.daemon = True
        stats_thread.start()
        
        # Atualiza as atividades recentes em uma thread separada
        activities_thread = threading.Thread(target=self._update_recent_activities_async)
        activities_thread.daemon = True
        activities_thread.start()
        
        # Atualiza os projetos ativos em uma thread separada
        projects_thread = threading.Thread(target=self._update_active_projects_async)
        projects_thread.daemon = True
        projects_thread.start()
    
    def _is_cache_valid(self, cache_key):
        """Verifica se o cache para a chave especificada é válido"""
        cache_entry = self.cache.get(cache_key)
        if not cache_entry or cache_entry["data"] is None or cache_entry["timestamp"] is None:
            return False
        
        # Verifica se o cache ainda é válido com base no tempo
        now = datetime.now().timestamp()
        return (now - cache_entry["timestamp"]) < cache_entry["valid_time"]
    
    def _update_cache(self, cache_key, data):
        """Atualiza o cache com novos dados"""
        if cache_key in self.cache:
            self.cache[cache_key]["data"] = data
            self.cache[cache_key]["timestamp"] = datetime.now().timestamp()
    
    def force_refresh(self):
        """Força a atualização dos dados, ignorando o cache"""
        # Limpa o cache
        for key in self.cache:
            self.cache[key]["data"] = None
            self.cache[key]["timestamp"] = None
        
        # Atualiza os dados
        self.refresh()