import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime, date
from sqlalchemy.orm import Session
from ..database.connection import db_manager
from ..database.models import Transaction, Project, TransactionType
from ..auth.auth_manager import auth_manager

class FinancesFrame:
    """Frame para gestão financeira"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.transactions_list = None
        self.form_frame = None
        self.selected_transaction = None
        
        # Campos do formulário
        self.type_combo = None
        self.description_entry = None
        self.amount_entry = None
        self.project_combo = None
        self.date_entry = None
        self.category_entry = None
        
        # Filtros
        self.filter_type_combo = None
        self.filter_project_combo = None
        self.filter_month_combo = None
        
        # Estatísticas
        self.stats_frame = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets do frame de finanças"""
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(fill="both", expand=True)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        
        # Estatísticas (topo)
        self._create_stats_section()
        
        # Lista de transações (lado esquerdo)
        self._create_transactions_list()
        
        # Formulário (lado direito)
        self._create_form()
    
    def _create_stats_section(self):
        """Cria a seção de estatísticas"""
        self.stats_frame = ctk.CTkFrame(self.frame)
        self.stats_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 10))
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Título
        stats_title = ctk.CTkLabel(
            self.stats_frame,
            text="💰 Resumo Financeiro",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        stats_title.grid(row=0, column=0, columnspan=4, pady=(15, 10))
        
        # Cards de estatísticas
        self.total_income_label = ctk.CTkLabel(
            self.stats_frame,
            text="Receitas\nR$ 0,00",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4CAF50",
            corner_radius=8,
            height=60
        )
        self.total_income_label.grid(row=1, column=0, padx=5, pady=(0, 15), sticky="ew")
        
        self.total_expense_label = ctk.CTkLabel(
            self.stats_frame,
            text="Despesas\nR$ 0,00",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#F44336",
            corner_radius=8,
            height=60
        )
        self.total_expense_label.grid(row=1, column=1, padx=5, pady=(0, 15), sticky="ew")
        
        self.balance_label = ctk.CTkLabel(
            self.stats_frame,
            text="Saldo\nR$ 0,00",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2196F3",
            corner_radius=8,
            height=60
        )
        self.balance_label.grid(row=1, column=2, padx=5, pady=(0, 15), sticky="ew")
        
        self.pending_label = ctk.CTkLabel(
            self.stats_frame,
            text="A Receber\nR$ 0,00",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#FF9800",
            corner_radius=8,
            height=60
        )
        self.pending_label.grid(row=1, column=3, padx=5, pady=(0, 15), sticky="ew")
    
    def _create_transactions_list(self):
        """Cria a lista de transações"""
        # Frame da lista
        list_frame = ctk.CTkFrame(self.frame)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_rowconfigure(3, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            list_frame,
            text="💳 Transações",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        # Filtros
        filters_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        filters_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        filters_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.filter_type_combo = ctk.CTkComboBox(
            filters_frame,
            values=["Todos", "Receita", "Despesa"],
            command=self._apply_filters,
            width=80
        )
        self.filter_type_combo.set("Todos")
        self.filter_type_combo.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.filter_project_combo = ctk.CTkComboBox(
            filters_frame,
            values=["Todos os Projetos"],
            command=self._apply_filters,
            width=120
        )
        self.filter_project_combo.set("Todos os Projetos")
        self.filter_project_combo.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Mês atual
        current_month = datetime.now().strftime("%m/%Y")
        months = ["Todos os Meses", current_month]
        
        self.filter_month_combo = ctk.CTkComboBox(
            filters_frame,
            values=months,
            command=self._apply_filters,
            width=100
        )
        self.filter_month_combo.set(current_month)
        self.filter_month_combo.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        
        # Botão nova transação
        new_btn = ctk.CTkButton(
            list_frame,
            text="+ Nova Transação",
            command=self._new_transaction,
            width=200
        )
        new_btn.grid(row=2, column=0, pady=(0, 10), padx=15)
        
        # Lista scrollável
        self.transactions_list = ctk.CTkScrollableFrame(list_frame, width=300)
        self.transactions_list.grid(row=3, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.transactions_list.grid_columnconfigure(0, weight=1)
    
    def _create_form(self):
        """Cria o formulário de transação"""
        self.form_frame = ctk.CTkScrollableFrame(self.frame)
        self.form_frame.grid(row=1, column=1, sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)
        
        # Título do formulário
        self.form_title = ctk.CTkLabel(
            self.form_frame,
            text="Nova Transação",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.form_title.grid(row=0, column=0, pady=(15, 20), sticky="w")
        
        # Tipo
        type_label = ctk.CTkLabel(self.form_frame, text="Tipo:*")
        type_label.grid(row=1, column=0, sticky="w", pady=(10, 5))
        
        self.type_combo = ctk.CTkComboBox(
            self.form_frame,
            values=["Receita", "Despesa"],
            command=self._on_type_change
        )
        self.type_combo.set("Receita")
        self.type_combo.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        # Descrição
        description_label = ctk.CTkLabel(self.form_frame, text="Descrição:*")
        description_label.grid(row=3, column=0, sticky="w", pady=(10, 5))
        
        self.description_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Descrição da transação"
        )
        self.description_entry.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        
        # Valor
        amount_label = ctk.CTkLabel(self.form_frame, text="Valor (R$):*")
        amount_label.grid(row=5, column=0, sticky="w", pady=(10, 5))
        
        self.amount_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="0,00"
        )
        self.amount_entry.grid(row=6, column=0, sticky="ew", pady=(0, 10))
        
        # Projeto
        project_label = ctk.CTkLabel(self.form_frame, text="Projeto:")
        project_label.grid(row=7, column=0, sticky="w", pady=(10, 5))
        
        self.project_combo = ctk.CTkComboBox(
            self.form_frame,
            values=["Geral (sem projeto)"]
        )
        self.project_combo.set("Geral (sem projeto)")
        self.project_combo.grid(row=8, column=0, sticky="ew", pady=(0, 10))
        
        # Data
        date_label = ctk.CTkLabel(self.form_frame, text="Data:*")
        date_label.grid(row=9, column=0, sticky="w", pady=(10, 5))
        
        self.date_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="DD/MM/AAAA"
        )
        # Preenche com data atual
        self.date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.date_entry.grid(row=10, column=0, sticky="ew", pady=(0, 10))
        
        # Categoria
        category_label = ctk.CTkLabel(self.form_frame, text="Categoria:")
        category_label.grid(row=11, column=0, sticky="w", pady=(10, 5))
        
        self.category_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Ex: Software, Hardware, Marketing"
        )
        self.category_entry.grid(row=12, column=0, sticky="ew", pady=(0, 10))
        
        # Botões
        buttons_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        buttons_frame.grid(row=13, column=0, sticky="ew", pady=(20, 20))
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Salvar",
            command=self._save_transaction
        )
        self.save_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.delete_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Excluir",
            command=self._delete_transaction,
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        )
        self.delete_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.clear_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Limpar",
            command=self._clear_form,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.clear_btn.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        
        # Inicialmente desabilita botão de excluir
        self.delete_btn.configure(state="disabled")
    
    def _on_type_change(self, value):
        """Chamado quando o tipo de transação muda"""
        if value == "Receita":
            self.project_combo.configure(state="normal")
        else:
            # Para despesas, projeto é opcional
            pass
    
    def _load_projects_combo(self):
        """Carrega os projetos nos comboboxes"""
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            projects = session.query(Project).filter(
                Project.user_id == user.id
            ).order_by(Project.name).all()
            
            project_names = ["Geral (sem projeto)"] + [project.name for project in projects]
            
            # Atualiza comboboxes
            self.project_combo.configure(values=project_names)
            
            filter_projects = ["Todos os Projetos"] + [project.name for project in projects]
            self.filter_project_combo.configure(values=filter_projects)
            
            # Armazena referência dos projetos
            self.projects_data = {project.name: project for project in projects}
            
        except Exception as e:
            print(f"Erro ao carregar projetos: {e}")
        finally:
            session.close()
    
    def _load_transactions(self):
        """Carrega a lista de transações"""
        # Limpa a lista atual
        for widget in self.transactions_list.winfo_children():
            widget.destroy()
        
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            query = session.query(Transaction).filter(
                Transaction.user_id == user.id
            )
            
            # Aplica filtros
            filter_type = self.filter_type_combo.get()
            if filter_type != "Todos":
                transaction_type = TransactionType.RECEITA if filter_type == "Receita" else TransactionType.DESPESA
                query = query.filter(Transaction.type == transaction_type)
            
            filter_project = self.filter_project_combo.get()
            if filter_project != "Todos os Projetos":
                if filter_project in self.projects_data:
                    query = query.filter(Transaction.project_id == self.projects_data[filter_project].id)
                else:
                    query = query.filter(Transaction.project_id.is_(None))
            
            filter_month = self.filter_month_combo.get()
            if filter_month != "Todos os Meses":
                try:
                    month, year = filter_month.split('/')
                    query = query.filter(
                        Transaction.date.between(
                            date(int(year), int(month), 1),
                            date(int(year), int(month), 31)
                        )
                    )
                except:
                    pass
            
            transactions = query.order_by(Transaction.date.desc()).all()
            
            for i, transaction in enumerate(transactions):
                # Cor baseada no tipo
                color = "#4CAF50" if transaction.type == TransactionType.RECEITA else "#F44336"
                
                # Texto da transação
                project_text = transaction.project.name if transaction.project else "Geral"
                amount_text = f"R$ {transaction.amount:.2f}".replace('.', ',')
                date_text = transaction.date.strftime("%d/%m/%Y")
                
                transaction_btn = ctk.CTkButton(
                    self.transactions_list,
                    text=f"{transaction.description}\n{project_text}\n{amount_text} - {date_text}",
                    command=lambda t=transaction: self._select_transaction(t),
                    height=80,
                    anchor="w",
                    fg_color=color
                )
                transaction_btn.grid(row=i, column=0, sticky="ew", pady=2)
            
            if not transactions:
                no_transactions_label = ctk.CTkLabel(
                    self.transactions_list,
                    text="Nenhuma transação encontrada",
                    text_color="gray"
                )
                no_transactions_label.grid(row=0, column=0, pady=20)
            
            # Atualiza estatísticas
            self._update_stats()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar transações: {e}")
        finally:
            session.close()
    
    def _update_stats(self):
        """Atualiza as estatísticas financeiras"""
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            # Filtro de mês atual
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Receitas do mês
            total_income = session.query(Transaction).filter(
                Transaction.user_id == user.id,
                Transaction.type == TransactionType.RECEITA,
                Transaction.date.between(
                    date(current_year, current_month, 1),
                    date(current_year, current_month, 31)
                )
            ).with_entities(Transaction.amount).all()
            
            income_sum = sum(t.amount for t in total_income if t.amount)
            
            # Despesas do mês
            total_expense = session.query(Transaction).filter(
                Transaction.user_id == user.id,
                Transaction.type == TransactionType.DESPESA,
                Transaction.date.between(
                    date(current_year, current_month, 1),
                    date(current_year, current_month, 31)
                )
            ).with_entities(Transaction.amount).all()
            
            expense_sum = sum(t.amount for t in total_expense if t.amount)
            
            # Saldo
            balance = income_sum - expense_sum
            
            # A receber (projetos ativos sem pagamento total)
            pending = 0  # Implementar lógica mais complexa se necessário
            
            # Atualiza labels
            self.total_income_label.configure(
                text=f"Receitas\nR$ {income_sum:.2f}".replace('.', ',')
            )
            
            self.total_expense_label.configure(
                text=f"Despesas\nR$ {expense_sum:.2f}".replace('.', ',')
            )
            
            balance_color = "#4CAF50" if balance >= 0 else "#F44336"
            self.balance_label.configure(
                text=f"Saldo\nR$ {balance:.2f}".replace('.', ','),
                fg_color=balance_color
            )
            
            self.pending_label.configure(
                text=f"A Receber\nR$ {pending:.2f}".replace('.', ',')
            )
            
        except Exception as e:
            print(f"Erro ao atualizar estatísticas: {e}")
        finally:
            session.close()
    
    def _apply_filters(self, value=None):
        """Aplica os filtros selecionados"""
        self._load_transactions()
    
    def _select_transaction(self, transaction):
        """Seleciona uma transação e carrega seus dados no formulário"""
        self.selected_transaction = transaction
        
        # Preenche o formulário
        self.type_combo.set("Receita" if transaction.type == TransactionType.RECEITA else "Despesa")
        
        self.description_entry.delete(0, 'end')
        self.description_entry.insert(0, transaction.description)
        
        self.amount_entry.delete(0, 'end')
        self.amount_entry.insert(0, f"{transaction.amount:.2f}".replace('.', ','))
        
        if transaction.project:
            self.project_combo.set(transaction.project.name)
        else:
            self.project_combo.set("Geral (sem projeto)")
        
        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, transaction.date.strftime("%d/%m/%Y"))
        
        self.category_entry.delete(0, 'end')
        if transaction.category:
            self.category_entry.insert(0, transaction.category)
        
        # Atualiza título e habilita botão de excluir
        self.form_title.configure(text=f"Editando: {transaction.description}")
        self.delete_btn.configure(state="normal")
    
    def _new_transaction(self):
        """Prepara o formulário para uma nova transação"""
        self.selected_transaction = None
        self._clear_form()
        self.form_title.configure(text="Nova Transação")
        self.delete_btn.configure(state="disabled")
        self.description_entry.focus()
    
    def _clear_form(self):
        """Limpa o formulário"""
        self.type_combo.set("Receita")
        self.description_entry.delete(0, 'end')
        self.amount_entry.delete(0, 'end')
        self.project_combo.set("Geral (sem projeto)")
        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.category_entry.delete(0, 'end')
    
    def _parse_date(self, date_str):
        """Converte string de data para date"""
        try:
            return datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
        except ValueError:
            return None
    
    def _save_transaction(self):
        """Salva a transação"""
        description = self.description_entry.get().strip()
        amount_str = self.amount_entry.get().strip().replace(',', '.')
        date_str = self.date_entry.get().strip()
        
        if not description:
            messagebox.showerror("Erro", "A descrição é obrigatória.")
            return
        
        if not amount_str:
            messagebox.showerror("Erro", "O valor é obrigatório.")
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Erro", "O valor deve ser maior que zero.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido.")
            return
        
        transaction_date = self._parse_date(date_str)
        if not transaction_date:
            messagebox.showerror("Erro", "Data inválida. Use o formato DD/MM/AAAA.")
            return
        
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            if self.selected_transaction:
                # Atualiza transação existente
                transaction = session.query(Transaction).filter(
                    Transaction.id == self.selected_transaction.id
                ).first()
                
                if not transaction:
                    messagebox.showerror("Erro", "Transação não encontrada.")
                    return
            else:
                # Cria nova transação
                transaction = Transaction(user_id=user.id)
                session.add(transaction)
            
            # Atualiza dados
            transaction.type = TransactionType.RECEITA if self.type_combo.get() == "Receita" else TransactionType.DESPESA
            transaction.description = description
            transaction.amount = amount
            transaction.date = transaction_date
            transaction.category = self.category_entry.get().strip() or None
            
            # Projeto
            project_name = self.project_combo.get()
            if project_name != "Geral (sem projeto)" and hasattr(self, 'projects_data') and project_name in self.projects_data:
                transaction.project_id = self.projects_data[project_name].id
            else:
                transaction.project_id = None
            
            session.commit()
            
            messagebox.showinfo("Sucesso", "Transação salva com sucesso!")
            self._load_transactions()
            
            if not self.selected_transaction:
                self._clear_form()
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar transação: {e}")
        finally:
            session.close()
    
    def _delete_transaction(self):
        """Exclui a transação selecionada"""
        if not self.selected_transaction:
            return
        
        # Confirma exclusão
        result = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a transação '{self.selected_transaction.description}'?\n\n"
            "Esta ação não pode ser desfeita."
        )
        
        if not result:
            return
        
        session = db_manager.get_session()
        try:
            transaction = session.query(Transaction).filter(
                Transaction.id == self.selected_transaction.id
            ).first()
            
            if transaction:
                session.delete(transaction)
                session.commit()
                
                messagebox.showinfo("Sucesso", "Transação excluída com sucesso!")
                self._load_transactions()
                self._clear_form()
                self.selected_transaction = None
                self.form_title.configure(text="Nova Transação")
                self.delete_btn.configure(state="disabled")
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir transação: {e}")
        finally:
            session.close()
    
    def show(self):
        """Exibe o frame de finanças"""
        self.frame.pack(fill="both", expand=True)
    
    def hide(self):
        """Esconde o frame de finanças"""
        self.frame.pack_forget()
    
    def refresh(self):
        """Atualiza os dados do frame"""
        self._load_projects_combo()
        self._load_transactions()