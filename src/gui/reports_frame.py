import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from datetime import datetime, date
import os
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database.connection import db_manager
from ..database.models import Project, Transaction, TimeEntry, TransactionType, ProjectStatus
from ..auth.auth_manager import auth_manager
from config import Config

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class ReportsFrame:
    """Frame para geração de relatórios"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        
        # Campos de filtro
        self.project_combo = None
        self.start_date_entry = None
        self.end_date_entry = None
        self.report_type_combo = None
        
        # Preview
        self.preview_text = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets do frame de relatórios"""
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(fill="both", expand=True)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            self.frame,
            text="📊 Relatórios",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 20))
        
        # Painel de controles (lado esquerdo)
        self._create_controls_panel()
        
        # Preview (lado direito)
        self._create_preview_panel()
    
    def _create_controls_panel(self):
        """Cria o painel de controles"""
        controls_frame = ctk.CTkFrame(self.frame)
        controls_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        controls_frame.grid_rowconfigure(8, weight=1)
        
        # Título do painel
        controls_title = ctk.CTkLabel(
            controls_frame,
            text="⚙️ Configurações do Relatório",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        controls_title.grid(row=0, column=0, pady=(15, 20), padx=15, sticky="w")
        
        # Tipo de relatório
        type_label = ctk.CTkLabel(controls_frame, text="Tipo de Relatório:*")
        type_label.grid(row=1, column=0, sticky="w", padx=15, pady=(10, 5))
        
        self.report_type_combo = ctk.CTkComboBox(
            controls_frame,
            values=[
                "Relatório de Projeto",
                "Relatório Financeiro",
                "Relatório de Horas",
                "Fatura de Projeto",
                "Resumo Geral"
            ],
            command=self._on_report_type_change,
            width=250
        )
        self.report_type_combo.set("Relatório de Projeto")
        self.report_type_combo.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))
        
        # Projeto
        project_label = ctk.CTkLabel(controls_frame, text="Projeto:")
        project_label.grid(row=3, column=0, sticky="w", padx=15, pady=(10, 5))
        
        self.project_combo = ctk.CTkComboBox(
            controls_frame,
            values=["Todos os Projetos"],
            width=250
        )
        self.project_combo.set("Todos os Projetos")
        self.project_combo.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 10))
        
        # Período
        period_label = ctk.CTkLabel(controls_frame, text="Período:")
        period_label.grid(row=5, column=0, sticky="w", padx=15, pady=(10, 5))
        
        # Datas
        dates_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        dates_frame.grid(row=6, column=0, sticky="ew", padx=15, pady=(0, 10))
        dates_frame.grid_columnconfigure((0, 1), weight=1)
        
        start_label = ctk.CTkLabel(dates_frame, text="De:")
        start_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.start_date_entry = ctk.CTkEntry(
            dates_frame,
            placeholder_text="DD/MM/AAAA"
        )
        # Primeiro dia do mês atual
        first_day = date.today().replace(day=1)
        self.start_date_entry.insert(0, first_day.strftime("%d/%m/%Y"))
        self.start_date_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        
        end_label = ctk.CTkLabel(dates_frame, text="Até:")
        end_label.grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        self.end_date_entry = ctk.CTkEntry(
            dates_frame,
            placeholder_text="DD/MM/AAAA"
        )
        # Data atual
        self.end_date_entry.insert(0, date.today().strftime("%d/%m/%Y"))
        self.end_date_entry.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        buttons_frame.grid(row=7, column=0, sticky="ew", padx=15, pady=(20, 0))
        buttons_frame.grid_columnconfigure(0, weight=1)
        
        preview_btn = ctk.CTkButton(
            buttons_frame,
            text="👁️ Visualizar",
            command=self._generate_preview,
            height=40
        )
        preview_btn.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        if REPORTLAB_AVAILABLE:
            export_btn = ctk.CTkButton(
                buttons_frame,
                text="📄 Exportar PDF",
                command=self._export_pdf,
                height=40,
                fg_color="#4CAF50",
                hover_color="#45a049"
            )
            export_btn.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        else:
            no_pdf_label = ctk.CTkLabel(
                buttons_frame,
                text="⚠️ ReportLab não instalado\nExportação PDF indisponível",
                text_color="orange",
                font=ctk.CTkFont(size=12)
            )
            no_pdf_label.grid(row=1, column=0, pady=(0, 10))
        
        # Atalhos rápidos
        shortcuts_label = ctk.CTkLabel(
            controls_frame,
            text="🚀 Atalhos Rápidos",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        shortcuts_label.grid(row=9, column=0, sticky="w", padx=15, pady=(20, 10))
        
        shortcuts_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        shortcuts_frame.grid(row=10, column=0, sticky="ew", padx=15, pady=(0, 15))
        shortcuts_frame.grid_columnconfigure(0, weight=1)
        
        month_btn = ctk.CTkButton(
            shortcuts_frame,
            text="📅 Relatório do Mês",
            command=self._quick_month_report,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        month_btn.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        year_btn = ctk.CTkButton(
            shortcuts_frame,
            text="📆 Relatório do Ano",
            command=self._quick_year_report,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        year_btn.grid(row=1, column=0, sticky="ew")
    
    def _create_preview_panel(self):
        """Cria o painel de preview"""
        preview_frame = ctk.CTkFrame(self.frame)
        preview_frame.grid(row=1, column=1, sticky="nsew")
        preview_frame.grid_rowconfigure(1, weight=1)
        
        # Título do preview
        preview_title = ctk.CTkLabel(
            preview_frame,
            text="👁️ Visualização do Relatório",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        preview_title.grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        # Área de texto para preview
        self.preview_text = ctk.CTkTextbox(
            preview_frame,
            font=ctk.CTkFont(family="Courier", size=12)
        )
        self.preview_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Texto inicial
        initial_text = (
            "📊 DEVFLOW - RELATÓRIOS\n"
            "=" * 50 + "\n\n"
            "Selecione o tipo de relatório e clique em 'Visualizar'\n"
            "para gerar uma prévia do conteúdo.\n\n"
            "Tipos de relatório disponíveis:\n"
            "• Relatório de Projeto - Detalhes de um projeto específico\n"
            "• Relatório Financeiro - Receitas e despesas\n"
            "• Relatório de Horas - Controle de tempo trabalhado\n"
            "• Fatura de Projeto - Documento para cobrança\n"
            "• Resumo Geral - Visão geral de todos os dados\n\n"
            "💡 Dica: Use os atalhos rápidos para relatórios\n"
            "    mensais e anuais."
        )
        self.preview_text.insert("1.0", initial_text)
        self.preview_text.configure(state="disabled")
    
    def _on_report_type_change(self, value):
        """Chamado quando o tipo de relatório muda"""
        if value == "Fatura de Projeto":
            # Para faturas, é obrigatório selecionar um projeto
            self.project_combo.configure(state="normal")
            if self.project_combo.get() == "Todos os Projetos":
                messagebox.showinfo(
                    "Informação",
                    "Para gerar uma fatura, você deve selecionar um projeto específico."
                )
        else:
            self.project_combo.configure(state="normal")
    
    def _load_projects_combo(self):
        """Carrega os projetos no combobox"""
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            projects = session.query(Project).filter(
                Project.user_id == user.id
            ).order_by(Project.name).all()
            
            project_names = ["Todos os Projetos"] + [project.name for project in projects]
            self.project_combo.configure(values=project_names)
            
            # Armazena referência dos projetos
            self.projects_data = {project.name: project for project in projects}
            
        except Exception as e:
            print(f"Erro ao carregar projetos: {e}")
        finally:
            session.close()
    
    def _parse_date(self, date_str):
        """Converte string de data para date"""
        try:
            return datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
        except ValueError:
            return None
    
    def _quick_month_report(self):
        """Gera relatório rápido do mês atual"""
        today = date.today()
        first_day = today.replace(day=1)
        
        self.start_date_entry.delete(0, 'end')
        self.start_date_entry.insert(0, first_day.strftime("%d/%m/%Y"))
        
        self.end_date_entry.delete(0, 'end')
        self.end_date_entry.insert(0, today.strftime("%d/%m/%Y"))
        
        self.report_type_combo.set("Resumo Geral")
        self.project_combo.set("Todos os Projetos")
        
        self._generate_preview()
    
    def _quick_year_report(self):
        """Gera relatório rápido do ano atual"""
        today = date.today()
        first_day = today.replace(month=1, day=1)
        
        self.start_date_entry.delete(0, 'end')
        self.start_date_entry.insert(0, first_day.strftime("%d/%m/%Y"))
        
        self.end_date_entry.delete(0, 'end')
        self.end_date_entry.insert(0, today.strftime("%d/%m/%Y"))
        
        self.report_type_combo.set("Resumo Geral")
        self.project_combo.set("Todos os Projetos")
        
        self._generate_preview()
    
    def _generate_preview(self):
        """Gera a visualização do relatório"""
        report_type = self.report_type_combo.get()
        project_name = self.project_combo.get()
        start_date = self._parse_date(self.start_date_entry.get())
        end_date = self._parse_date(self.end_date_entry.get())
        
        if not start_date or not end_date:
            messagebox.showerror("Erro", "Datas inválidas. Use o formato DD/MM/AAAA.")
            return
        
        if start_date > end_date:
            messagebox.showerror("Erro", "A data de início deve ser anterior à data de fim.")
            return
        
        user = auth_manager.get_current_user()
        if not user:
            return
        
        try:
            if report_type == "Relatório de Projeto":
                content = self._generate_project_report(user, project_name, start_date, end_date)
            elif report_type == "Relatório Financeiro":
                content = self._generate_financial_report(user, project_name, start_date, end_date)
            elif report_type == "Relatório de Horas":
                content = self._generate_hours_report(user, project_name, start_date, end_date)
            elif report_type == "Fatura de Projeto":
                content = self._generate_invoice(user, project_name, start_date, end_date)
            elif report_type == "Resumo Geral":
                content = self._generate_summary_report(user, project_name, start_date, end_date)
            else:
                content = "Tipo de relatório não implementado."
            
            # Atualiza o preview
            self.preview_text.configure(state="normal")
            self.preview_text.delete("1.0", 'end')
            self.preview_text.insert("1.0", content)
            self.preview_text.configure(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
    
    def _generate_project_report(self, user, project_name, start_date, end_date):
        """Gera relatório de projeto"""
        session = db_manager.get_session()
        try:
            content = []
            content.append("📊 RELATÓRIO DE PROJETO")
            content.append("=" * 50)
            content.append(f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
            content.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
            content.append("")
            
            # Filtro de projetos
            query = session.query(Project).filter(Project.user_id == user.id)
            
            if project_name != "Todos os Projetos" and hasattr(self, 'projects_data') and project_name in self.projects_data:
                projects = [self.projects_data[project_name]]
                content.append(f"Projeto: {project_name}")
            else:
                projects = query.all()
                content.append("Projeto: Todos os Projetos")
            
            content.append("")
            
            for project in projects:
                content.append(f"📁 {project.name}")
                content.append("-" * 30)
                content.append(f"Cliente: {project.client.name}")
                content.append(f"Status: {project.status.value.title()}")
                
                if project.description:
                    content.append(f"Descrição: {project.description}")
                
                if project.budget:
                    content.append(f"Orçamento: R$ {project.budget:.2f}".replace('.', ','))
                
                if project.start_date:
                    content.append(f"Data de Início: {project.start_date.strftime('%d/%m/%Y')}")
                
                if project.end_date:
                    content.append(f"Data de Fim: {project.end_date.strftime('%d/%m/%Y')}")
                
                # Transações do projeto no período
                transactions = session.query(Transaction).filter(
                    Transaction.user_id == user.id,
                    Transaction.project_id == project.id,
                    Transaction.date.between(start_date, end_date)
                ).all()
                
                if transactions:
                    content.append("\n💰 Transações:")
                    total_income = 0
                    total_expense = 0
                    
                    for trans in transactions:
                        type_symbol = "📈" if trans.type == TransactionType.RECEITA else "📉"
                        amount_text = f"R$ {trans.amount:.2f}".replace('.', ',')
                        content.append(f"  {type_symbol} {trans.description} - {amount_text} ({trans.date.strftime('%d/%m/%Y')})")
                        
                        if trans.type == TransactionType.RECEITA:
                            total_income += trans.amount
                        else:
                            total_expense += trans.amount
                    
                    content.append(f"\n  Total Receitas: R$ {total_income:.2f}".replace('.', ','))
                    content.append(f"  Total Despesas: R$ {total_expense:.2f}".replace('.', ','))
                    content.append(f"  Saldo: R$ {(total_income - total_expense):.2f}".replace('.', ','))
                
                # Horas trabalhadas no período
                time_entries = session.query(TimeEntry).filter(
                    TimeEntry.user_id == user.id,
                    TimeEntry.project_id == project.id,
                    TimeEntry.date.between(start_date, end_date)
                ).all()
                
                if time_entries:
                    content.append("\n⏰ Horas Trabalhadas:")
                    total_minutes = 0
                    
                    for entry in time_entries:
                        hours = entry.duration_minutes // 60
                        minutes = entry.duration_minutes % 60
                        content.append(f"  📝 {entry.description} - {hours}h {minutes}m ({entry.date.strftime('%d/%m/%Y')})")
                        total_minutes += entry.duration_minutes
                    
                    total_hours = total_minutes // 60
                    total_mins = total_minutes % 60
                    content.append(f"\n  Total de Horas: {total_hours}h {total_mins}m")
                
                content.append("\n" + "=" * 50 + "\n")
            
            return "\n".join(content)
            
        finally:
            session.close()
    
    def _generate_financial_report(self, user, project_name, start_date, end_date):
        """Gera relatório financeiro"""
        session = db_manager.get_session()
        try:
            content = []
            content.append("💰 RELATÓRIO FINANCEIRO")
            content.append("=" * 50)
            content.append(f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
            content.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
            content.append("")
            
            # Query base
            query = session.query(Transaction).filter(
                Transaction.user_id == user.id,
                Transaction.date.between(start_date, end_date)
            )
            
            # Filtro de projeto
            if project_name != "Todos os Projetos" and hasattr(self, 'projects_data') and project_name in self.projects_data:
                query = query.filter(Transaction.project_id == self.projects_data[project_name].id)
                content.append(f"Projeto: {project_name}")
            else:
                content.append("Projeto: Todos os Projetos")
            
            content.append("")
            
            # Receitas
            income_transactions = query.filter(Transaction.type == TransactionType.RECEITA).all()
            content.append("📈 RECEITAS")
            content.append("-" * 20)
            
            total_income = 0
            if income_transactions:
                for trans in income_transactions:
                    amount_text = f"R$ {trans.amount:.2f}".replace('.', ',')
                    project_text = trans.project.name if trans.project else "Geral"
                    content.append(f"  {trans.description} - {amount_text} ({project_text}) - {trans.date.strftime('%d/%m/%Y')}")
                    total_income += trans.amount
            else:
                content.append("  Nenhuma receita no período")
            
            content.append(f"\nTotal de Receitas: R$ {total_income:.2f}".replace('.', ','))
            content.append("")
            
            # Despesas
            expense_transactions = query.filter(Transaction.type == TransactionType.DESPESA).all()
            content.append("📉 DESPESAS")
            content.append("-" * 20)
            
            total_expense = 0
            if expense_transactions:
                for trans in expense_transactions:
                    amount_text = f"R$ {trans.amount:.2f}".replace('.', ',')
                    project_text = trans.project.name if trans.project else "Geral"
                    content.append(f"  {trans.description} - {amount_text} ({project_text}) - {trans.date.strftime('%d/%m/%Y')}")
                    total_expense += trans.amount
            else:
                content.append("  Nenhuma despesa no período")
            
            content.append(f"\nTotal de Despesas: R$ {total_expense:.2f}".replace('.', ','))
            content.append("")
            
            # Resumo
            balance = total_income - total_expense
            content.append("📊 RESUMO")
            content.append("-" * 20)
            content.append(f"Total de Receitas: R$ {total_income:.2f}".replace('.', ','))
            content.append(f"Total de Despesas: R$ {total_expense:.2f}".replace('.', ','))
            content.append(f"Saldo do Período: R$ {balance:.2f}".replace('.', ','))
            
            return "\n".join(content)
            
        finally:
            session.close()
    
    def _generate_hours_report(self, user, project_name, start_date, end_date):
        """Gera relatório de horas"""
        session = db_manager.get_session()
        try:
            content = []
            content.append("⏰ RELATÓRIO DE HORAS")
            content.append("=" * 50)
            content.append(f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
            content.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
            content.append("")
            
            # Query base
            query = session.query(TimeEntry).filter(
                TimeEntry.user_id == user.id,
                TimeEntry.date.between(start_date, end_date)
            )
            
            # Filtro de projeto
            if project_name != "Todos os Projetos" and hasattr(self, 'projects_data') and project_name in self.projects_data:
                query = query.filter(TimeEntry.project_id == self.projects_data[project_name].id)
                content.append(f"Projeto: {project_name}")
            else:
                content.append("Projeto: Todos os Projetos")
            
            content.append("")
            
            # Entradas de tempo
            time_entries = query.order_by(TimeEntry.date.desc(), TimeEntry.start_time.desc()).all()
            
            if time_entries:
                # Agrupa por projeto
                projects_hours = {}
                total_minutes = 0
                
                for entry in time_entries:
                    project_name_key = entry.project.name
                    if project_name_key not in projects_hours:
                        projects_hours[project_name_key] = []
                    projects_hours[project_name_key].append(entry)
                    total_minutes += entry.duration_minutes
                
                # Exibe por projeto
                for proj_name, entries in projects_hours.items():
                    content.append(f"📁 {proj_name}")
                    content.append("-" * 30)
                    
                    project_minutes = 0
                    for entry in entries:
                        hours = entry.duration_minutes // 60
                        minutes = entry.duration_minutes % 60
                        time_range = f"{entry.start_time.strftime('%H:%M')} - {entry.end_time.strftime('%H:%M')}"
                        content.append(f"  📝 {entry.description} - {hours}h {minutes}m ({entry.date.strftime('%d/%m/%Y')} | {time_range})")
                        project_minutes += entry.duration_minutes
                    
                    proj_hours = project_minutes // 60
                    proj_mins = project_minutes % 60
                    content.append(f"\n  Subtotal: {proj_hours}h {proj_mins}m")
                    content.append("")
                
                # Total geral
                total_hours = total_minutes // 60
                total_mins = total_minutes % 60
                content.append("📊 RESUMO")
                content.append("-" * 20)
                content.append(f"Total de Horas Trabalhadas: {total_hours}h {total_mins}m")
                content.append(f"Número de Registros: {len(time_entries)}")
                
                if total_minutes > 0:
                    avg_per_day = total_minutes / max(1, (end_date - start_date).days + 1)
                    avg_hours = int(avg_per_day // 60)
                    avg_mins = int(avg_per_day % 60)
                    content.append(f"Média por Dia: {avg_hours}h {avg_mins}m")
            else:
                content.append("Nenhuma entrada de tempo encontrada no período.")
            
            return "\n".join(content)
            
        finally:
            session.close()
    
    def _generate_invoice(self, user, project_name, start_date, end_date):
        """Gera fatura de projeto"""
        if project_name == "Todos os Projetos":
            return "❌ ERRO: Para gerar uma fatura, selecione um projeto específico."
        
        if not hasattr(self, 'projects_data') or project_name not in self.projects_data:
            return "❌ ERRO: Projeto não encontrado."
        
        project = self.projects_data[project_name]
        
        session = db_manager.get_session()
        try:
            content = []
            content.append("🧾 FATURA")
            content.append("=" * 50)
            content.append(f"Data de Emissão: {datetime.now().strftime('%d/%m/%Y')}")
            content.append(f"Período de Serviços: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
            content.append("")
            
            # Dados do projeto
            content.append("📋 DADOS DO PROJETO")
            content.append("-" * 25)
            content.append(f"Projeto: {project.name}")
            content.append(f"Cliente: {project.client.name}")
            
            if project.client.email:
                content.append(f"Email: {project.client.email}")
            
            if project.client.phone:
                content.append(f"Telefone: {project.client.phone}")
            
            content.append("")
            
            # Serviços prestados (horas trabalhadas)
            time_entries = session.query(TimeEntry).filter(
                TimeEntry.user_id == user.id,
                TimeEntry.project_id == project.id,
                TimeEntry.date.between(start_date, end_date)
            ).order_by(TimeEntry.date).all()
            
            content.append("🔧 SERVIÇOS PRESTADOS")
            content.append("-" * 25)
            
            total_minutes = 0
            if time_entries:
                for entry in time_entries:
                    hours = entry.duration_minutes // 60
                    minutes = entry.duration_minutes % 60
                    content.append(f"  {entry.date.strftime('%d/%m/%Y')} - {entry.description} ({hours}h {minutes}m)")
                    total_minutes += entry.duration_minutes
            else:
                content.append("  Nenhum serviço registrado no período")
            
            total_hours = total_minutes // 60
            total_mins = total_minutes % 60
            content.append(f"\nTotal de Horas: {total_hours}h {total_mins}m")
            content.append("")
            
            # Valores
            content.append("💰 VALORES")
            content.append("-" * 15)
            
            if project.budget:
                content.append(f"Valor do Projeto: R$ {project.budget:.2f}".replace('.', ','))
                
                # Calcula valor por hora se houver horas trabalhadas
                if total_minutes > 0:
                    hourly_rate = project.budget / (total_minutes / 60)
                    content.append(f"Valor por Hora: R$ {hourly_rate:.2f}".replace('.', ','))
                    
                    # Valor proporcional às horas trabalhadas
                    proportional_value = (total_minutes / 60) * hourly_rate
                    content.append(f"Valor Proporcional: R$ {proportional_value:.2f}".replace('.', ','))
            else:
                content.append("Valor do projeto não definido")
            
            content.append("")
            
            # Observações
            content.append("📝 OBSERVAÇÕES")
            content.append("-" * 15)
            content.append("Esta fatura refere-se aos serviços de desenvolvimento")
            content.append("prestados no período especificado.")
            content.append("")
            content.append("Prazo de pagamento: 30 dias")
            content.append("")
            content.append("Obrigado pela preferência!")
            
            return "\n".join(content)
            
        finally:
            session.close()
    
    def _generate_summary_report(self, user, project_name, start_date, end_date):
        """Gera resumo geral"""
        session = db_manager.get_session()
        try:
            content = []
            content.append("📊 RESUMO GERAL")
            content.append("=" * 50)
            content.append(f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
            content.append(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
            content.append("")
            
            # Projetos
            projects_query = session.query(Project).filter(Project.user_id == user.id)
            if project_name != "Todos os Projetos" and hasattr(self, 'projects_data') and project_name in self.projects_data:
                projects = [self.projects_data[project_name]]
            else:
                projects = projects_query.all()
            
            content.append("📁 PROJETOS")
            content.append("-" * 15)
            content.append(f"Total de Projetos: {len(projects)}")
            
            # Status dos projetos
            status_count = {}
            for project in projects:
                status = project.status.value.title()
                status_count[status] = status_count.get(status, 0) + 1
            
            for status, count in status_count.items():
                content.append(f"  {status}: {count}")
            
            content.append("")
            
            # Finanças
            transactions_query = session.query(Transaction).filter(
                Transaction.user_id == user.id,
                Transaction.date.between(start_date, end_date)
            )
            
            if project_name != "Todos os Projetos" and hasattr(self, 'projects_data') and project_name in self.projects_data:
                transactions_query = transactions_query.filter(Transaction.project_id == self.projects_data[project_name].id)
            
            income_total = transactions_query.filter(Transaction.type == TransactionType.RECEITA).with_entities(func.sum(Transaction.amount)).scalar() or 0
            expense_total = transactions_query.filter(Transaction.type == TransactionType.DESPESA).with_entities(func.sum(Transaction.amount)).scalar() or 0
            
            content.append("💰 FINANCEIRO")
            content.append("-" * 15)
            content.append(f"Total de Receitas: R$ {income_total:.2f}".replace('.', ','))
            content.append(f"Total de Despesas: R$ {expense_total:.2f}".replace('.', ','))
            content.append(f"Saldo: R$ {(income_total - expense_total):.2f}".replace('.', ','))
            content.append("")
            
            # Horas
            time_query = session.query(TimeEntry).filter(
                TimeEntry.user_id == user.id,
                TimeEntry.date.between(start_date, end_date)
            )
            
            if project_name != "Todos os Projetos" and hasattr(self, 'projects_data') and project_name in self.projects_data:
                time_query = time_query.filter(TimeEntry.project_id == self.projects_data[project_name].id)
            
            total_minutes = time_query.with_entities(func.sum(TimeEntry.duration_minutes)).scalar() or 0
            total_entries = time_query.count()
            
            total_hours = total_minutes // 60
            total_mins = total_minutes % 60
            
            content.append("⏰ TEMPO")
            content.append("-" * 10)
            content.append(f"Total de Horas: {total_hours}h {total_mins}m")
            content.append(f"Número de Registros: {total_entries}")
            
            if total_minutes > 0:
                days_in_period = (end_date - start_date).days + 1
                avg_per_day = total_minutes / days_in_period
                avg_hours = int(avg_per_day // 60)
                avg_mins = int(avg_per_day % 60)
                content.append(f"Média por Dia: {avg_hours}h {avg_mins}m")
            
            content.append("")
            
            # Produtividade
            content.append("📈 PRODUTIVIDADE")
            content.append("-" * 20)
            
            if total_minutes > 0 and income_total > 0:
                hourly_income = income_total / (total_minutes / 60)
                content.append(f"Receita por Hora: R$ {hourly_income:.2f}".replace('.', ','))
            
            if total_entries > 0:
                days_worked = len(set(entry.date for entry in time_query.all()))
                content.append(f"Dias Trabalhados: {days_worked}")
                
                if days_worked > 0:
                    avg_hours_per_workday = total_minutes / (days_worked * 60)
                    content.append(f"Média de Horas por Dia Trabalhado: {avg_hours_per_workday:.1f}h")
            
            return "\n".join(content)
            
        finally:
            session.close()
    
    def _export_pdf(self):
        """Exporta o relatório para PDF"""
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Erro", "ReportLab não está instalado. Instale com: pip install reportlab")
            return
        
        # Gera o conteúdo primeiro
        self._generate_preview()
        
        # Pega o conteúdo do preview
        content = self.preview_text.get("1.0", 'end').strip()
        
        if not content or "Selecione o tipo de relatório" in content:
            messagebox.showerror("Erro", "Gere uma visualização do relatório primeiro.")
            return
        
        # Diálogo para salvar arquivo
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Salvar Relatório PDF"
        )
        
        if not filename:
            return
        
        try:
            # Cria o PDF
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Estilo personalizado
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Centralizado
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Courier'
            )
            
            # Converte o conteúdo
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    if line.startswith('📊') or line.startswith('💰') or line.startswith('⏰') or line.startswith('🧾'):
                        # Títulos
                        story.append(Paragraph(line, title_style))
                    else:
                        # Texto normal
                        story.append(Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), normal_style))
                else:
                    story.append(Spacer(1, 12))
            
            # Gera o PDF
            doc.build(story)
            
            messagebox.showinfo("Sucesso", f"Relatório exportado com sucesso!\n\nArquivo: {filename}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar PDF: {e}")
    
    def show(self):
        """Exibe o frame de relatórios"""
        self.frame.grid(row=0, column=0, sticky="nsew")
    
    def hide(self):
        """Esconde o frame de relatórios"""
        self.frame.grid_remove()
    
    def refresh(self):
        """Atualiza os dados do frame"""
        self._load_projects_combo()