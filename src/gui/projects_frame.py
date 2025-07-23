import customtkinter as ctk
import tkinter.messagebox as messagebox
import webbrowser
import threading
import time
from datetime import datetime
from sqlalchemy.orm import Session
from ..database.connection import db_manager
from ..database.models import Project, Client, ProjectStatus
from ..auth.auth_manager import auth_manager

class ProjectsFrame:
    """Frame para gestão de projetos"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.projects_list = None
        self.form_frame = None
        self.selected_project = None
        
        # Campos do formulário
        self.name_entry = None
        self.client_combo = None
        self.description_text = None
        self.budget_entry = None
        self.status_combo = None
        self.start_date_entry = None
        self.end_date_entry = None
        
        # Indicadores de carregamento
        self.projects_loading_indicator = None
        self.clients_loading_indicator = None
        self.is_projects_loading = False
        self.is_clients_loading = False
        
        # Cache de dados
        self.cache = {
            "projects": {
                "data": None,
                "timestamp": None,
                "valid_time": 300  # 5 minutos em segundos
            },
            "clients": {
                "data": None,
                "timestamp": None,
                "valid_time": 300  # 5 minutos em segundos
            }
        }
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets do frame de projetos"""
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(fill="both", expand=True)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # Lista de projetos (lado esquerdo)
        self._create_projects_list()
        
        # Formulário (lado direito)
        self._create_form()
    
    def _create_projects_list(self):
        """Cria a lista de projetos"""
        # Frame da lista
        list_frame = ctk.CTkFrame(self.frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_rowconfigure(2, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            list_frame,
            text="📁 Projetos",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        # Botão novo projeto
        new_btn = ctk.CTkButton(
            list_frame,
            text="+ Novo Projeto",
            command=self._new_project,
            width=200
        )
        new_btn.grid(row=1, column=0, pady=(0, 10), padx=15)
        
        # Lista scrollável
        self.projects_list = ctk.CTkScrollableFrame(list_frame, width=250)
        self.projects_list.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.projects_list.grid_columnconfigure(0, weight=1)
        
        # Indicador de carregamento (não adicionado ao grid ainda)
        self.projects_loading_indicator = ctk.CTkLabel(
            self.projects_list,
            text="Carregando projetos...",
            text_color="gray"
        )
    
    def _create_form(self):
        """Cria o formulário de projeto"""
        self.form_frame = ctk.CTkScrollableFrame(self.frame)
        self.form_frame.grid(row=0, column=1, sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)
        
        # Título do formulário
        self.form_title = ctk.CTkLabel(
            self.form_frame,
            text="Dados do Projeto",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.form_title.grid(row=0, column=0, pady=(15, 20), sticky="w")
        
        # Nome
        name_label = ctk.CTkLabel(self.form_frame, text="Nome do Projeto:*")
        name_label.grid(row=1, column=0, sticky="w", pady=(10, 5))
        
        self.name_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Nome do projeto"
        )
        self.name_entry.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        # Cliente
        client_label = ctk.CTkLabel(self.form_frame, text="Cliente:*")
        client_label.grid(row=3, column=0, sticky="w", pady=(10, 5))
        
        self.client_combo = ctk.CTkComboBox(
            self.form_frame,
            values=["Carregando..."]
        )
        self.client_combo.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        
        # Descrição
        description_label = ctk.CTkLabel(self.form_frame, text="Descrição:")
        description_label.grid(row=5, column=0, sticky="w", pady=(10, 5))
        
        self.description_text = ctk.CTkTextbox(
            self.form_frame,
            height=100
        )
        self.description_text.grid(row=6, column=0, sticky="ew", pady=(0, 10))
        
        # Orçamento
        budget_label = ctk.CTkLabel(self.form_frame, text="Orçamento (R$):")
        budget_label.grid(row=7, column=0, sticky="w", pady=(10, 5))
        
        self.budget_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="0,00"
        )
        self.budget_entry.grid(row=8, column=0, sticky="ew", pady=(0, 10))
        
        # Status
        status_label = ctk.CTkLabel(self.form_frame, text="Status:")
        status_label.grid(row=9, column=0, sticky="w", pady=(10, 5))
        
        self.status_combo = ctk.CTkComboBox(
            self.form_frame,
            values=["Proposta", "Ativo", "Concluído", "Cancelado", "Pausado"]
        )
        self.status_combo.set("Proposta")
        self.status_combo.grid(row=10, column=0, sticky="ew", pady=(0, 10))
        
        # Datas
        dates_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        dates_frame.grid(row=11, column=0, sticky="ew", pady=(10, 0))
        dates_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Data de início
        start_label = ctk.CTkLabel(dates_frame, text="Data de Início:")
        start_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.start_date_entry = ctk.CTkEntry(
            dates_frame,
            placeholder_text="DD/MM/AAAA"
        )
        self.start_date_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        
        # Data de fim
        end_label = ctk.CTkLabel(dates_frame, text="Data de Fim:")
        end_label.grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        self.end_date_entry = ctk.CTkEntry(
            dates_frame,
            placeholder_text="DD/MM/AAAA"
        )
        self.end_date_entry.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        # Contrato
        contract_label = ctk.CTkLabel(self.form_frame, text="Contrato (Google Drive):")
        contract_label.grid(row=12, column=0, sticky="w", pady=(20, 5))
        
        contract_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        contract_frame.grid(row=13, column=0, sticky="ew", pady=(0, 10))
        contract_frame.grid_columnconfigure(0, weight=1)
        
        # Nome do arquivo
        self.contract_name_entry = ctk.CTkEntry(
            contract_frame,
            placeholder_text="Nome do arquivo (ex: Contrato_Cliente_2024.pdf)"
        )
        self.contract_name_entry.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Link do Google Drive
        self.contract_link_entry = ctk.CTkEntry(
            contract_frame,
            placeholder_text="Link do Google Drive (https://drive.google.com/...)"
        )
        self.contract_link_entry.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        self.contract_link_entry.bind("<KeyRelease>", self._on_contract_link_change)
        
        # Botão para abrir contrato
        self.open_contract_btn = ctk.CTkButton(
            contract_frame,
            text="📄 Abrir Contrato",
            command=self._open_contract,
            height=30,
            fg_color="#1976D2",
            hover_color="#1565C0"
        )
        self.open_contract_btn.grid(row=2, column=0, sticky="ew")
        self.open_contract_btn.configure(state="disabled")
        
        # Botões
        buttons_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        buttons_frame.grid(row=14, column=0, sticky="ew", pady=(20, 20))
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Salvar",
            command=self._save_project
        )
        self.save_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.delete_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Excluir",
            command=self._delete_project,
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
    
    def _is_cache_valid(self, cache_key):
        """Verifica se o cache é válido"""
        cache = self.cache[cache_key]
        if not cache["data"] or not cache["timestamp"]:
            return False
        
        # Verifica se o cache ainda é válido
        current_time = time.time()
        return (current_time - cache["timestamp"]) < cache["valid_time"]
    
    def _update_cache(self, cache_key, data):
        """Atualiza o cache com novos dados"""
        self.cache[cache_key]["data"] = data
        self.cache[cache_key]["timestamp"] = time.time()
    
    def _show_clients_loading(self):
        """Exibe o indicador de carregamento de clientes"""
        if not self.is_clients_loading:
            self.client_combo.configure(values=["Carregando..."])
            self.client_combo.set("Carregando...")
            self.is_clients_loading = True
    
    def _hide_clients_loading(self):
        """Esconde o indicador de carregamento de clientes"""
        self.is_clients_loading = False
    
    def _load_clients_combo(self):
        """Carrega os clientes no combobox de forma assíncrona"""
        self._show_clients_loading()
        
        # Inicia o carregamento em uma thread separada
        load_thread = threading.Thread(target=self._load_clients_async)
        load_thread.daemon = True
        load_thread.start()
    
    def _load_clients_async(self):
        """Carrega os clientes em uma thread separada"""
        user = auth_manager.get_current_user()
        if not user:
            self.frame.after(0, self._hide_clients_loading)
            return
        
        # Verifica se o cache é válido
        if self._is_cache_valid("clients"):
            self.frame.after(0, lambda: self._update_clients_ui(self.cache["clients"]["data"]))
            return
        
        session = db_manager.get_session()
        try:
            clients = session.query(Client).filter(
                Client.user_id == user.id,
                Client.is_active == True
            ).order_by(Client.name).all()
            
            # Atualiza o cache
            self._update_cache("clients", clients)
            
            # Atualiza a UI na thread principal
            self.frame.after(0, lambda: self._update_clients_ui(clients))
            
        except Exception as e:
            self.frame.after(0, lambda: print(f"Erro ao carregar clientes: {e}"))
        finally:
            session.close()
    
    def _update_clients_ui(self, clients):
        """Atualiza a UI com os clientes carregados"""
        client_names = [client.name for client in clients]
        
        if client_names:
            self.client_combo.configure(values=client_names)
            self.client_combo.set(client_names[0])
        else:
            self.client_combo.configure(values=["Nenhum cliente cadastrado"])
            self.client_combo.set("Nenhum cliente cadastrado")
        
        # Armazena referência dos clientes
        self.clients_data = {client.name: client for client in clients}
        
        self._hide_clients_loading()
    
    def _show_projects_loading(self):
        """Exibe o indicador de carregamento de projetos"""
        if not self.is_projects_loading:
            # Limpa a lista atual
            for widget in self.projects_list.winfo_children():
                widget.destroy()
            
            self.projects_loading_indicator = ctk.CTkLabel(
                self.projects_list,
                text="Carregando projetos...",
                text_color="gray"
            )
            self.projects_loading_indicator.grid(row=0, column=0, pady=20)
            self.is_projects_loading = True
    
    def _hide_projects_loading(self):
        """Esconde o indicador de carregamento de projetos"""
        if self.is_projects_loading:
            try:
                if self.projects_loading_indicator.winfo_exists():
                    self.projects_loading_indicator.grid_forget()
            except tk.TclError:
                pass  # Widget já foi destruído
            self.is_projects_loading = False
    
    def _load_projects(self):
        """Carrega a lista de projetos de forma assíncrona"""
        self._show_projects_loading()
        
        # Inicia o carregamento em uma thread separada
        load_thread = threading.Thread(target=self._load_projects_async)
        load_thread.daemon = True
        load_thread.start()
    
    def _load_projects_async(self):
        """Carrega a lista de projetos em uma thread separada"""
        user = auth_manager.get_current_user()
        if not user:
            self.frame.after(0, self._hide_projects_loading)
            return
        
        # Verifica se o cache é válido
        if self._is_cache_valid("projects"):
            self.frame.after(0, lambda: self._update_projects_ui(self.cache["projects"]["data"]))
            return
        
        session = db_manager.get_session()
        try:
            from sqlalchemy.orm import joinedload
            projects = session.query(Project).options(
                joinedload(Project.client)
            ).filter(
                Project.user_id == user.id
            ).order_by(Project.created_at.desc()).all()
            
            # Atualiza o cache
            self._update_cache("projects", projects)
            
            # Atualiza a UI na thread principal
            self.frame.after(0, lambda: self._update_projects_ui(projects))
                
        except Exception as e:
            self.frame.after(0, lambda: messagebox.showerror("Erro", f"Erro ao carregar projetos: {e}"))
        finally:
            session.close()
    
    def _update_projects_ui(self, projects):
        """Atualiza a UI com os projetos carregados"""
        # Limpa a lista atual
        for widget in self.projects_list.winfo_children():
            widget.destroy()
        
        for i, project in enumerate(projects):
            # Cor baseada no status
            status_colors = {
                ProjectStatus.PROPOSTA: "#FF9800",
                ProjectStatus.ATIVO: "#4CAF50",
                ProjectStatus.CONCLUIDO: "#2196F3",
                ProjectStatus.CANCELADO: "#F44336",
                ProjectStatus.PAUSADO: "#9E9E9E"
            }
            
            color = status_colors.get(project.status, "#2196F3")
            
            project_btn = ctk.CTkButton(
                self.projects_list,
                text=f"{project.name}\n{project.client.name}\n{project.status.value.title()}",
                command=lambda p=project: self._select_project(p),
                height=80,
                anchor="w",
                fg_color=color
            )
            project_btn.grid(row=i, column=0, sticky="ew", pady=2)
        
        if not projects:
            no_projects_label = ctk.CTkLabel(
                self.projects_list,
                text="Nenhum projeto cadastrado",
                text_color="gray"
            )
            no_projects_label.grid(row=0, column=0, pady=20)
        
        self._hide_projects_loading()
    
    def _select_project(self, project):
        """Seleciona um projeto e carrega seus dados no formulário"""
        self.selected_project = project
        
        # Preenche o formulário
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, project.name)
        
        self.client_combo.set(project.client.name)
        
        self.description_text.delete("1.0", 'end')
        if project.description:
            self.description_text.insert("1.0", project.description)
        
        self.budget_entry.delete(0, 'end')
        if project.budget:
            self.budget_entry.insert(0, f"{project.budget:.2f}".replace('.', ','))
        
        self.status_combo.set(project.status.value.title())
        
        self.start_date_entry.delete(0, 'end')
        if project.start_date:
            self.start_date_entry.insert(0, project.start_date.strftime("%d/%m/%Y"))
        
        self.end_date_entry.delete(0, 'end')
        if project.end_date:
            self.end_date_entry.insert(0, project.end_date.strftime("%d/%m/%Y"))
        
        # Contrato
        self.contract_name_entry.delete(0, 'end')
        if hasattr(project, 'contract_file_name') and project.contract_file_name:
            self.contract_name_entry.insert(0, project.contract_file_name)
        
        self.contract_link_entry.delete(0, 'end')
        if hasattr(project, 'contract_drive_link') and project.contract_drive_link:
            self.contract_link_entry.insert(0, project.contract_drive_link)
            self.open_contract_btn.configure(state="normal")
        else:
            self.open_contract_btn.configure(state="disabled")
        
        # Atualiza título e habilita botão de excluir
        self.form_title.configure(text=f"Editando: {project.name}")
        self.delete_btn.configure(state="normal")
    
    def _new_project(self):
        """Prepara o formulário para um novo projeto"""
        self.selected_project = None
        self._clear_form()
        self.form_title.configure(text="Novo Projeto")
        self.delete_btn.configure(state="disabled")
        self.name_entry.focus()
    
    def _clear_form(self):
        """Limpa o formulário"""
        self.name_entry.delete(0, 'end')
        self.description_text.delete("1.0", 'end')
        self.budget_entry.delete(0, 'end')
        self.status_combo.set("Proposta")
        self.start_date_entry.delete(0, 'end')
        self.end_date_entry.delete(0, 'end')
        self.contract_name_entry.delete(0, 'end')
        self.contract_link_entry.delete(0, 'end')
        self.open_contract_btn.configure(state="disabled")
    
    def _parse_date(self, date_str):
        """Converte string de data para datetime"""
        if not date_str.strip():
            return None
        try:
            return datetime.strptime(date_str.strip(), "%d/%m/%Y")
        except ValueError:
            return None
    
    def _save_project(self):
        """Salva o projeto"""
        name = self.name_entry.get().strip()
        client_name = self.client_combo.get()
        
        if not name:
            messagebox.showerror("Erro", "O nome do projeto é obrigatório.")
            return
        
        if not hasattr(self, 'clients_data') or client_name not in self.clients_data:
            messagebox.showerror("Erro", "Selecione um cliente válido.")
            return
        
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            if self.selected_project:
                # Atualiza projeto existente
                project = session.query(Project).filter(
                    Project.id == self.selected_project.id
                ).first()
                
                if not project:
                    messagebox.showerror("Erro", "Projeto não encontrado.")
                    return
            else:
                # Cria novo projeto
                project = Project(user_id=user.id)
                session.add(project)
            
            # Atualiza dados
            project.name = name
            project.client_id = self.clients_data[client_name].id
            project.description = self.description_text.get("1.0", 'end').strip() or None
            
            # Orçamento
            budget_str = self.budget_entry.get().strip().replace(',', '.')
            if budget_str:
                try:
                    project.budget = float(budget_str)
                except ValueError:
                    messagebox.showerror("Erro", "Valor do orçamento inválido.")
                    return
            else:
                project.budget = None
            
            # Status
            status_map = {
                "Proposta": ProjectStatus.PROPOSTA,
                "Ativo": ProjectStatus.ATIVO,
                "Concluído": ProjectStatus.CONCLUIDO,
                "Cancelado": ProjectStatus.CANCELADO,
                "Pausado": ProjectStatus.PAUSADO
            }
            project.status = status_map[self.status_combo.get()]
            
            # Datas
            project.start_date = self._parse_date(self.start_date_entry.get())
            project.end_date = self._parse_date(self.end_date_entry.get())
            
            # Contrato
            contract_name = self.contract_name_entry.get().strip()
            contract_link = self.contract_link_entry.get().strip()
            
            if contract_name and contract_link:
                project.contract_file_name = contract_name
                project.contract_drive_link = contract_link
                if not self.selected_project:  # Novo projeto
                    project.contract_uploaded_at = datetime.now()
            elif not contract_name and not contract_link:
                project.contract_file_name = None
                project.contract_drive_link = None
                project.contract_uploaded_at = None
            
            session.commit()
            
            messagebox.showinfo("Sucesso", "Projeto salvo com sucesso!")
            self._load_projects()
            
            if not self.selected_project:
                self._clear_form()
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar projeto: {e}")
        finally:
            session.close()
    
    def _delete_project(self):
        """Exclui o projeto selecionado"""
        if not self.selected_project:
            return
        
        # Confirma exclusão
        result = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o projeto '{self.selected_project.name}'?\n\n"
            "Esta ação excluirá também todas as transações e registros de tempo associados.\n"
            "Esta ação não pode ser desfeita."
        )
        
        if not result:
            return
        
        session = db_manager.get_session()
        try:
            project = session.query(Project).filter(
                Project.id == self.selected_project.id
            ).first()
            
            if project:
                session.delete(project)
                session.commit()
                
                messagebox.showinfo("Sucesso", "Projeto excluído com sucesso!")
                self._load_projects()
                self._clear_form()
                self.selected_project = None
                self.form_title.configure(text="Dados do Projeto")
                self.delete_btn.configure(state="disabled")
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir projeto: {e}")
        finally:
            session.close()
    
    def _open_contract(self):
        """Abre o link do contrato no navegador"""
        link = self.contract_link_entry.get().strip()
        if link:
            try:
                webbrowser.open(link)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir o link: {e}")
    
    def _on_contract_link_change(self, event=None):
        """Habilita/desabilita o botão de abrir contrato baseado no conteúdo do link"""
        link = self.contract_link_entry.get().strip()
        if link and (link.startswith("http://") or link.startswith("https://")):
            self.open_contract_btn.configure(state="normal")
        else:
            self.open_contract_btn.configure(state="disabled")
    
    def show(self):
        """Exibe o frame de projetos"""
        self.frame.pack(fill="both", expand=True)
    
    def hide(self):
        """Esconde o frame de projetos"""
        self.frame.pack_forget()
    
    def refresh(self):
        """Atualiza os dados do frame"""
        self._load_clients_combo()
        self._load_projects()
    
    def force_refresh(self):
        """Força a atualização dos dados, ignorando o cache"""
        # Limpa o cache
        self.cache["projects"]["data"] = None
        self.cache["projects"]["timestamp"] = None
        self.cache["clients"]["data"] = None
        self.cache["clients"]["timestamp"] = None
        
        # Recarrega os dados
        self.refresh()