import customtkinter as ctk
import tkinter.messagebox as messagebox
import threading
from sqlalchemy.orm import Session
from ..database.connection import db_manager
from ..database.models import Client
from ..auth.auth_manager import auth_manager

class ClientsFrame:
    """Frame para gestão de clientes"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.clients_list = None
        self.form_frame = None
        self.selected_client = None
        
        # Campos do formulário
        self.name_entry = None
        self.email_entry = None
        self.phone_entry = None
        self.company_entry = None
        self.address_text = None
        self.notes_text = None
        
        # Indicadores de carregamento
        self.loading_indicator = None
        self.is_loading = False
        
        # Cache de dados
        self.clients_cache = {
            "data": None,
            "timestamp": None,
            "valid_time": 300  # 5 minutos em segundos
        }
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets do frame de clientes"""
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(fill="both", expand=True)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # Lista de clientes (lado esquerdo)
        self._create_clients_list()
        
        # Formulário (lado direito)
        self._create_form()
    
    def _create_clients_list(self):
        """Cria a lista de clientes"""
        # Frame da lista
        list_frame = ctk.CTkFrame(self.frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_rowconfigure(2, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            list_frame,
            text="👥 Clientes",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        # Botão novo cliente
        new_btn = ctk.CTkButton(
            list_frame,
            text="+ Novo Cliente",
            command=self._new_client,
            width=200
        )
        new_btn.grid(row=1, column=0, pady=(0, 10), padx=15)
        
        # Lista scrollável
        self.clients_list = ctk.CTkScrollableFrame(list_frame, width=250)
        self.clients_list.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.clients_list.grid_columnconfigure(0, weight=1)
        
        # Indicador de carregamento
        self.loading_indicator = ctk.CTkLabel(
            self.clients_list,
            text="Carregando clientes...",
            text_color="gray"
        )
        # Não adicionamos ao grid ainda - será adicionado quando necessário
    
    def _create_form(self):
        """Cria o formulário de cliente"""
        self.form_frame = ctk.CTkScrollableFrame(self.frame)
        self.form_frame.grid(row=0, column=1, sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)
        
        # Título do formulário
        self.form_title = ctk.CTkLabel(
            self.form_frame,
            text="Dados do Cliente",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.form_title.grid(row=0, column=0, pady=(15, 20), sticky="w")
        
        # Nome
        name_label = ctk.CTkLabel(self.form_frame, text="Nome:*")
        name_label.grid(row=1, column=0, sticky="w", pady=(10, 5))
        
        self.name_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Nome do cliente"
        )
        self.name_entry.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        # Email
        email_label = ctk.CTkLabel(self.form_frame, text="Email:")
        email_label.grid(row=3, column=0, sticky="w", pady=(10, 5))
        
        self.email_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="email@exemplo.com"
        )
        self.email_entry.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        
        # Telefone
        phone_label = ctk.CTkLabel(self.form_frame, text="Telefone:")
        phone_label.grid(row=5, column=0, sticky="w", pady=(10, 5))
        
        self.phone_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="(11) 99999-9999"
        )
        self.phone_entry.grid(row=6, column=0, sticky="ew", pady=(0, 10))
        
        # Empresa
        company_label = ctk.CTkLabel(self.form_frame, text="Empresa:")
        company_label.grid(row=7, column=0, sticky="w", pady=(10, 5))
        
        self.company_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Nome da empresa"
        )
        self.company_entry.grid(row=8, column=0, sticky="ew", pady=(0, 10))
        
        # Endereço
        address_label = ctk.CTkLabel(self.form_frame, text="Endereço:")
        address_label.grid(row=9, column=0, sticky="w", pady=(10, 5))
        
        self.address_text = ctk.CTkTextbox(
            self.form_frame,
            height=80
        )
        self.address_text.grid(row=10, column=0, sticky="ew", pady=(0, 10))
        
        # Observações
        notes_label = ctk.CTkLabel(self.form_frame, text="Observações:")
        notes_label.grid(row=11, column=0, sticky="w", pady=(10, 5))
        
        self.notes_text = ctk.CTkTextbox(
            self.form_frame,
            height=100
        )
        self.notes_text.grid(row=12, column=0, sticky="ew", pady=(0, 20))
        
        # Botões
        buttons_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        buttons_frame.grid(row=13, column=0, sticky="ew", pady=(0, 20))
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Salvar",
            command=self._save_client
        )
        self.save_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.delete_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Excluir",
            command=self._delete_client,
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
    
    def _show_loading(self):
        """Exibe o indicador de carregamento"""
        if not self.is_loading:
            # Limpa a lista atual
            for widget in self.clients_list.winfo_children():
                widget.destroy()
            
            self.loading_indicator = ctk.CTkLabel(
                self.clients_list,
                text="Carregando clientes...",
                text_color="gray"
            )
            self.loading_indicator.grid(row=0, column=0, pady=20)
            self.is_loading = True
    
    def _hide_loading(self):
        """Esconde o indicador de carregamento"""
        if self.is_loading:
            try:
                if self.loading_indicator.winfo_exists():
                    self.loading_indicator.grid_forget()
            except tk.TclError:
                pass  # Widget já foi destruído
            self.is_loading = False
    
    def _is_cache_valid(self, cache_key):
        """Verifica se o cache é válido"""
        import time
        
        cache = self.clients_cache
        if not cache["data"] or not cache["timestamp"]:
            return False
        
        # Verifica se o cache ainda é válido
        current_time = time.time()
        return (current_time - cache["timestamp"]) < cache["valid_time"]
    
    def _update_cache(self, data):
        """Atualiza o cache com novos dados"""
        import time
        
        self.clients_cache["data"] = data
        self.clients_cache["timestamp"] = time.time()
    
    def _load_clients(self):
        """Carrega a lista de clientes de forma assíncrona"""
        self._show_loading()
        
        # Inicia o carregamento em uma thread separada
        load_thread = threading.Thread(target=self._load_clients_async)
        load_thread.daemon = True
        load_thread.start()
    
    def _load_clients_async(self):
        """Carrega a lista de clientes em uma thread separada"""
        user = auth_manager.get_current_user()
        if not user:
            self.frame.after(0, self._hide_loading)
            return
        
        # Verifica se o cache é válido
        if self._is_cache_valid("data"):
            self.frame.after(0, lambda: self._update_clients_ui(self.clients_cache["data"]))
            return
        
        session = db_manager.get_session()
        try:
            clients = session.query(Client).filter(
                Client.user_id == user.id,
                Client.is_active == True
            ).order_by(Client.name).all()
            
            # Atualiza o cache
            self._update_cache(clients)
            
            # Atualiza a UI na thread principal
            self.frame.after(0, lambda: self._update_clients_ui(clients))
                
        except Exception as e:
            self.frame.after(0, lambda: messagebox.showerror("Erro", f"Erro ao carregar clientes: {e}"))
        finally:
            session.close()
    
    def _update_clients_ui(self, clients):
        """Atualiza a UI com os clientes carregados"""
        # Limpa a lista atual
        for widget in self.clients_list.winfo_children():
            widget.destroy()
        
        for i, client in enumerate(clients):
            client_btn = ctk.CTkButton(
                self.clients_list,
                text=f"{client.name}\n{client.company or 'Sem empresa'}",
                command=lambda c=client: self._select_client(c),
                height=60,
                anchor="w"
            )
            client_btn.grid(row=i, column=0, sticky="ew", pady=2)
        
        if not clients:
            no_clients_label = ctk.CTkLabel(
                self.clients_list,
                text="Nenhum cliente cadastrado",
                text_color="gray"
            )
            no_clients_label.grid(row=0, column=0, pady=20)
        
        self._hide_loading()
    
    def _select_client(self, client):
        """Seleciona um cliente e carrega seus dados no formulário"""
        self.selected_client = client
        
        # Preenche o formulário
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, client.name)
        
        self.email_entry.delete(0, 'end')
        if client.email:
            self.email_entry.insert(0, client.email)
        
        self.phone_entry.delete(0, 'end')
        if client.phone:
            self.phone_entry.insert(0, client.phone)
        
        self.company_entry.delete(0, 'end')
        if client.company:
            self.company_entry.insert(0, client.company)
        
        self.address_text.delete("1.0", 'end')
        if client.address:
            self.address_text.insert("1.0", client.address)
        
        self.notes_text.delete("1.0", 'end')
        if client.notes:
            self.notes_text.insert("1.0", client.notes)
        
        # Atualiza título e habilita botão de excluir
        self.form_title.configure(text=f"Editando: {client.name}")
        self.delete_btn.configure(state="normal")
    
    def _new_client(self):
        """Prepara o formulário para um novo cliente"""
        self.selected_client = None
        self._clear_form()
        self.form_title.configure(text="Novo Cliente")
        self.delete_btn.configure(state="disabled")
        self.name_entry.focus()
    
    def _clear_form(self):
        """Limpa o formulário"""
        self.name_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.phone_entry.delete(0, 'end')
        self.company_entry.delete(0, 'end')
        self.address_text.delete("1.0", 'end')
        self.notes_text.delete("1.0", 'end')
    
    def _save_client(self):
        """Salva o cliente"""
        name = self.name_entry.get().strip()
        
        if not name:
            messagebox.showerror("Erro", "O nome do cliente é obrigatório.")
            return
        
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            if self.selected_client:
                # Atualiza cliente existente
                client = session.query(Client).filter(
                    Client.id == self.selected_client.id
                ).first()
                
                if not client:
                    messagebox.showerror("Erro", "Cliente não encontrado.")
                    return
            else:
                # Cria novo cliente
                client = Client(user_id=user.id)
                session.add(client)
            
            # Atualiza dados
            client.name = name
            client.email = self.email_entry.get().strip() or None
            client.phone = self.phone_entry.get().strip() or None
            client.company = self.company_entry.get().strip() or None
            client.address = self.address_text.get("1.0", 'end').strip() or None
            client.notes = self.notes_text.get("1.0", 'end').strip() or None
            
            session.commit()
            
            messagebox.showinfo("Sucesso", "Cliente salvo com sucesso!")
            self._load_clients()
            
            if not self.selected_client:
                self._clear_form()
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar cliente: {e}")
        finally:
            session.close()
    
    def _delete_client(self):
        """Exclui o cliente selecionado"""
        if not self.selected_client:
            return
        
        # Confirma exclusão
        result = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o cliente '{self.selected_client.name}'?\n\n"
            "Esta ação não pode ser desfeita."
        )
        
        if not result:
            return
        
        session = db_manager.get_session()
        try:
            client = session.query(Client).filter(
                Client.id == self.selected_client.id
            ).first()
            
            if client:
                # Marca como inativo ao invés de deletar
                client.is_active = False
                session.commit()
                
                messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
                self._load_clients()
                self._clear_form()
                self.selected_client = None
                self.form_title.configure(text="Dados do Cliente")
                self.delete_btn.configure(state="disabled")
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir cliente: {e}")
        finally:
            session.close()
    
    def show(self):
        """Exibe o frame de clientes"""
        self.frame.pack(fill="both", expand=True)
    
    def hide(self):
        """Esconde o frame de clientes"""
        self.frame.pack_forget()
    
    def refresh(self):
        """Atualiza os dados do frame"""
        self._load_clients()
    
    def force_refresh(self):
        """Força a atualização dos dados, ignorando o cache"""
        # Limpa o cache
        self.clients_cache["data"] = None
        self.clients_cache["timestamp"] = None
        
        # Recarrega os dados
        self._load_clients()