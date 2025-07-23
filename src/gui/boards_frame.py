import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from datetime import datetime, date
from sqlalchemy.orm import Session
from ..database.connection import db_manager
from ..database.models import Project, Board, BoardColumn, Task, TaskPriority
from ..auth.auth_manager import auth_manager

class BoardsFrame:
    """Frame para gestão de quadros kanban"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.boards_list = None
        self.kanban_frame = None
        self.selected_board = None
        self.columns_frames = {}
        self.task_widgets = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets do frame de quadros"""
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(fill="both", expand=True)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # Lista de quadros (lado esquerdo)
        self._create_boards_list()
        
        # Área do kanban (lado direito)
        self._create_kanban_area()
    
    def _create_boards_list(self):
        """Cria a lista de quadros"""
        # Frame da lista
        list_frame = ctk.CTkFrame(self.frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_rowconfigure(2, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            list_frame,
            text="📋 Quadros",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        # Botão criar quadro
        new_btn = ctk.CTkButton(
            list_frame,
            text="+ Criar Quadro",
            command=self._create_board_dialog,
            width=200
        )
        new_btn.grid(row=1, column=0, pady=(0, 10), padx=15)
        
        # Lista scrollável
        self.boards_list = ctk.CTkScrollableFrame(list_frame, width=250)
        self.boards_list.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.boards_list.grid_columnconfigure(0, weight=1)
    
    def _create_kanban_area(self):
        """Cria a área principal do kanban"""
        self.kanban_frame = ctk.CTkScrollableFrame(self.frame, orientation="horizontal")
        self.kanban_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        
        # Mensagem inicial
        self.welcome_label = ctk.CTkLabel(
            self.kanban_frame,
            text="Selecione um quadro para começar",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        self.welcome_label.grid(row=0, column=0, padx=50, pady=50)
    
    def _load_boards(self):
        """Carrega a lista de quadros"""
        # Limpa a lista atual
        for widget in self.boards_list.winfo_children():
            widget.destroy()
        
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            boards = session.query(Board).filter(
                Board.user_id == user.id
            ).order_by(Board.created_at.desc()).all()
            
            for i, board in enumerate(boards):
                board_btn = ctk.CTkButton(
                    self.boards_list,
                    text=f"{board.name}\n{board.project.name}",
                    command=lambda b=board: self._select_board(b),
                    height=80,
                    anchor="w"
                )
                board_btn.grid(row=i, column=0, sticky="ew", pady=2)
            
            if not boards:
                no_boards_label = ctk.CTkLabel(
                    self.boards_list,
                    text="Nenhum quadro criado\nCrie um quadro a partir\nde um projeto existente",
                    text_color="gray",
                    justify="center"
                )
                no_boards_label.grid(row=0, column=0, pady=20)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar quadros: {e}")
        finally:
            session.close()
    
    def _create_board_dialog(self):
        """Abre diálogo para criar novo quadro"""
        dialog = ctk.CTkToplevel(self.frame)
        dialog.title("Criar Novo Quadro")
        dialog.geometry("400x300")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Centraliza o diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        # Nome do quadro
        name_label = ctk.CTkLabel(dialog, text="Nome do Quadro:")
        name_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        
        name_entry = ctk.CTkEntry(dialog, placeholder_text="Ex: Quadro de Tarefas - Projeto X")
        name_entry.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Projeto
        project_label = ctk.CTkLabel(dialog, text="Projeto:")
        project_label.grid(row=2, column=0, sticky="w", padx=20, pady=(10, 5))
        
        project_combo = ctk.CTkComboBox(dialog, values=["Carregando..."])
        project_combo.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Carrega projetos
        self._load_projects_combo(project_combo)
        
        # Descrição
        desc_label = ctk.CTkLabel(dialog, text="Descrição (opcional):")
        desc_label.grid(row=4, column=0, sticky="w", padx=20, pady=(10, 5))
        
        desc_text = ctk.CTkTextbox(dialog, height=80)
        desc_text.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Botões
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 20))
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="gray"
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        create_btn = ctk.CTkButton(
            buttons_frame,
            text="Criar",
            command=lambda: self._create_board(dialog, name_entry, project_combo, desc_text)
        )
        create_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
        dialog.grid_columnconfigure(0, weight=1)
        name_entry.focus()
    
    def _load_projects_combo(self, combo):
        """Carrega projetos no combobox"""
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            projects = session.query(Project).filter(
                Project.user_id == user.id
            ).order_by(Project.name).all()
            
            if projects:
                project_names = [f"{project.name} ({project.client.name})" for project in projects]
                combo.configure(values=project_names)
                combo.set(project_names[0])
                # Armazena referência dos projetos
                self.projects_data = {f"{project.name} ({project.client.name})": project for project in projects}
            else:
                combo.configure(values=["Nenhum projeto disponível"])
                combo.set("Nenhum projeto disponível")
                self.projects_data = {}
                
        except Exception as e:
            print(f"Erro ao carregar projetos: {e}")
        finally:
            session.close()
    
    def _create_board(self, dialog, name_entry, project_combo, desc_text):
        """Cria um novo quadro"""
        name = name_entry.get().strip()
        project_key = project_combo.get()
        description = desc_text.get("1.0", 'end').strip()
        
        if not name:
            messagebox.showerror("Erro", "O nome do quadro é obrigatório.")
            return
        
        if not hasattr(self, 'projects_data') or project_key not in self.projects_data:
            messagebox.showerror("Erro", "Selecione um projeto válido.")
            return
        
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            project = self.projects_data[project_key]
            
            # Cria o quadro
            board = Board(
                user_id=user.id,
                project_id=project.id,
                name=name,
                description=description if description else None
            )
            session.add(board)
            session.flush()  # Para obter o ID do board
            
            # Cria as colunas padrão
            default_columns = [
                {"name": "A Fazer", "color": "#FF9800", "position": 0},
                {"name": "Em Progresso", "color": "#2196F3", "position": 1},
                {"name": "Em Revisão", "color": "#9C27B0", "position": 2},
                {"name": "Concluído", "color": "#4CAF50", "position": 3}
            ]
            
            for col_data in default_columns:
                column = BoardColumn(
                    board_id=board.id,
                    name=col_data["name"],
                    color=col_data["color"],
                    position=col_data["position"]
                )
                session.add(column)
            
            session.commit()
            messagebox.showinfo("Sucesso", "Quadro criado com sucesso!")
            dialog.destroy()
            self._load_boards()
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao criar quadro: {e}")
        finally:
            session.close()
    
    def _select_board(self, board):
        """Seleciona um quadro e exibe o kanban"""
        self.selected_board = board
        self._load_kanban()
    
    def _load_kanban(self):
        """Carrega o quadro kanban"""
        # Limpa a área do kanban
        for widget in self.kanban_frame.winfo_children():
            widget.destroy()
        
        if not self.selected_board:
            return
        
        session = db_manager.get_session()
        try:
            # Carrega o board com suas colunas
            board = session.query(Board).filter(Board.id == self.selected_board.id).first()
            
            if not board:
                return
            
            # Título do quadro
            title_frame = ctk.CTkFrame(self.kanban_frame, fg_color="transparent")
            title_frame.grid(row=0, column=0, columnspan=len(board.columns), sticky="ew", padx=10, pady=(10, 20))
            
            title_label = ctk.CTkLabel(
                title_frame,
                text=f"📋 {board.name}",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            title_label.grid(row=0, column=0, sticky="w")
            
            project_label = ctk.CTkLabel(
                title_frame,
                text=f"Projeto: {board.project.name}",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            project_label.grid(row=1, column=0, sticky="w")
            
            # Colunas do kanban
            self.columns_frames = {}
            self.task_widgets = {}
            
            for i, column in enumerate(board.columns):
                self._create_column(column, i + 1)  # +1 porque row 0 é o título
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar quadro: {e}")
        finally:
            session.close()
    
    def _create_column(self, column, col_position):
        """Cria uma coluna do kanban"""
        # Frame da coluna
        column_frame = ctk.CTkFrame(self.kanban_frame, width=300)
        column_frame.grid(row=1, column=col_position, sticky="nsew", padx=5, pady=10)
        column_frame.grid_rowconfigure(2, weight=1)
        column_frame.grid_propagate(False)
        
        # Header da coluna
        header_frame = ctk.CTkFrame(column_frame, fg_color=column.color, height=40)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        header_frame.grid_propagate(False)
        
        column_title = ctk.CTkLabel(
            header_frame,
            text=column.name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        column_title.grid(row=0, column=0, padx=10, pady=10)
        
        # Botão adicionar tarefa
        add_task_btn = ctk.CTkButton(
            column_frame,
            text="+ Adicionar Tarefa",
            command=lambda c=column: self._add_task_dialog(c),
            height=30,
            fg_color="transparent",
            border_width=2,
            border_color=column.color
        )
        add_task_btn.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # Área das tarefas
        tasks_frame = ctk.CTkScrollableFrame(column_frame)
        tasks_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(0, 5))
        tasks_frame.grid_columnconfigure(0, weight=1)
        
        self.columns_frames[column.id] = tasks_frame
        self.task_widgets[column.id] = []
        
        # Carrega as tarefas
        self._load_tasks(column)
    
    def _load_tasks(self, column):
        """Carrega as tarefas de uma coluna"""
        tasks_frame = self.columns_frames[column.id]
        
        # Limpa tarefas existentes
        for widget in tasks_frame.winfo_children():
            widget.destroy()
        
        session = db_manager.get_session()
        try:
            tasks = session.query(Task).filter(
                Task.column_id == column.id
            ).order_by(Task.position).all()
            
            for i, task in enumerate(tasks):
                self._create_task_widget(task, tasks_frame, i)
                
        except Exception as e:
            print(f"Erro ao carregar tarefas: {e}")
        finally:
            session.close()
    
    def _create_task_widget(self, task, parent, row):
        """Cria o widget de uma tarefa"""
        # Cores de prioridade
        priority_colors = {
            TaskPriority.LOW: "#4CAF50",
            TaskPriority.MEDIUM: "#FF9800", 
            TaskPriority.HIGH: "#F44336"
        }
        
        task_frame = ctk.CTkFrame(parent, fg_color="#333333")
        task_frame.grid(row=row, column=0, sticky="ew", pady=2)
        task_frame.grid_columnconfigure(0, weight=1)
        
        # Barra de prioridade
        priority_frame = ctk.CTkFrame(
            task_frame, 
            height=4, 
            fg_color=priority_colors.get(task.priority, "#FF9800")
        )
        priority_frame.grid(row=0, column=0, sticky="ew")
        priority_frame.grid_propagate(False)
        
        # Título da tarefa
        title_label = ctk.CTkLabel(
            task_frame,
            text=task.title,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(8, 4))
        
        # Descrição (se houver)
        if task.description:
            desc_label = ctk.CTkLabel(
                task_frame,
                text=task.description[:100] + ("..." if len(task.description) > 100 else ""),
                font=ctk.CTkFont(size=10),
                text_color="gray",
                anchor="w",
                wraplength=250
            )
            desc_label.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 4))
        
        # Footer com informações
        footer_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        footer_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 8))
        footer_frame.grid_columnconfigure(0, weight=1)
        
        # Prioridade
        priority_text = task.priority.value.title()
        priority_label = ctk.CTkLabel(
            footer_frame,
            text=f"🔥 {priority_text}",
            font=ctk.CTkFont(size=9),
            text_color=priority_colors.get(task.priority, "#FF9800")
        )
        priority_label.grid(row=0, column=0, sticky="w")
        
        # Horas estimadas (se houver)
        if task.estimated_hours:
            hours_label = ctk.CTkLabel(
                footer_frame,
                text=f"⏱️ {task.estimated_hours}h",
                font=ctk.CTkFont(size=9),
                text_color="gray"
            )
            hours_label.grid(row=0, column=1, sticky="e")
        
        # Bind para editar tarefa
        def on_task_click(event, t=task):
            self._edit_task_dialog(t)
        
        task_frame.bind("<Button-1>", on_task_click)
        for child in task_frame.winfo_children():
            child.bind("<Button-1>", on_task_click)
    
    def _add_task_dialog(self, column):
        """Abre diálogo para adicionar nova tarefa"""
        self._task_dialog(column, None)
    
    def _edit_task_dialog(self, task):
        """Abre diálogo para editar tarefa"""
        session = db_manager.get_session()
        try:
            column = session.query(BoardColumn).filter(BoardColumn.id == task.column_id).first()
            self._task_dialog(column, task)
        finally:
            session.close()
    
    def _task_dialog(self, column, task=None):
        """Diálogo para criar/editar tarefa"""
        is_edit = task is not None
        title = "Editar Tarefa" if is_edit else "Nova Tarefa"
        
        dialog = ctk.CTkToplevel(self.frame)
        dialog.title(title)
        dialog.geometry("400x500")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Centraliza o diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"400x500+{x}+{y}")
        
        # Título da tarefa
        title_label = ctk.CTkLabel(dialog, text="Título da Tarefa:")
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        
        title_entry = ctk.CTkEntry(dialog, placeholder_text="Ex: Implementar funcionalidade X")
        title_entry.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Descrição
        desc_label = ctk.CTkLabel(dialog, text="Descrição:")
        desc_label.grid(row=2, column=0, sticky="w", padx=20, pady=(10, 5))
        
        desc_text = ctk.CTkTextbox(dialog, height=100)
        desc_text.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Prioridade
        priority_label = ctk.CTkLabel(dialog, text="Prioridade:")
        priority_label.grid(row=4, column=0, sticky="w", padx=20, pady=(10, 5))
        
        priority_combo = ctk.CTkComboBox(
            dialog,
            values=["Baixa", "Média", "Alta"]
        )
        priority_combo.set("Média")
        priority_combo.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Horas estimadas
        hours_label = ctk.CTkLabel(dialog, text="Horas Estimadas:")
        hours_label.grid(row=6, column=0, sticky="w", padx=20, pady=(10, 5))
        
        hours_entry = ctk.CTkEntry(dialog, placeholder_text="Ex: 2.5")
        hours_entry.grid(row=7, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Responsável
        assigned_label = ctk.CTkLabel(dialog, text="Responsável:")
        assigned_label.grid(row=8, column=0, sticky="w", padx=20, pady=(10, 5))
        
        assigned_entry = ctk.CTkEntry(dialog, placeholder_text="Nome do responsável")
        assigned_entry.grid(row=9, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Preenche campos se for edição
        if is_edit:
            title_entry.insert(0, task.title)
            if task.description:
                desc_text.insert("1.0", task.description)
            if task.priority == TaskPriority.LOW:
                priority_combo.set("Baixa")
            elif task.priority == TaskPriority.HIGH:
                priority_combo.set("Alta")
            else:
                priority_combo.set("Média")
            if task.estimated_hours:
                hours_entry.insert(0, str(task.estimated_hours))
            if task.assigned_to:
                assigned_entry.insert(0, task.assigned_to)
        
        # Botões
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.grid(row=10, column=0, sticky="ew", padx=20, pady=(0, 20))
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="gray"
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        if is_edit:
            delete_btn = ctk.CTkButton(
                buttons_frame,
                text="Excluir",
                command=lambda: self._delete_task(task, dialog),
                fg_color="#d32f2f"
            )
            delete_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="Salvar",
            command=lambda: self._save_task(
                dialog, column, task, title_entry, desc_text, 
                priority_combo, hours_entry, assigned_entry
            )
        )
        save_btn.grid(row=0, column=2 if is_edit else 1, padx=(5, 0) if is_edit else (5, 0), sticky="ew")
        
        dialog.grid_columnconfigure(0, weight=1)
        title_entry.focus()
    
    def _save_task(self, dialog, column, task, title_entry, desc_text, priority_combo, hours_entry, assigned_entry):
        """Salva a tarefa"""
        title = title_entry.get().strip()
        description = desc_text.get("1.0", 'end').strip()
        priority_text = priority_combo.get()
        hours_text = hours_entry.get().strip()
        assigned = assigned_entry.get().strip()
        
        if not title:
            messagebox.showerror("Erro", "O título da tarefa é obrigatório.")
            return
        
        # Converte prioridade
        priority_map = {
            "Baixa": TaskPriority.LOW,
            "Média": TaskPriority.MEDIUM,
            "Alta": TaskPriority.HIGH
        }
        priority = priority_map.get(priority_text, TaskPriority.MEDIUM)
        
        # Converte horas
        estimated_hours = None
        if hours_text:
            try:
                estimated_hours = float(hours_text.replace(',', '.'))
            except ValueError:
                messagebox.showerror("Erro", "Valor de horas inválido.")
                return
        
        session = db_manager.get_session()
        try:
            if task:
                # Edita tarefa existente
                task_obj = session.query(Task).filter(Task.id == task.id).first()
                if not task_obj:
                    messagebox.showerror("Erro", "Tarefa não encontrada.")
                    return
            else:
                # Cria nova tarefa
                # Obtém a próxima posição
                max_position = session.query(Task.position).filter(
                    Task.column_id == column.id
                ).order_by(Task.position.desc()).first()
                
                next_position = (max_position[0] + 1) if max_position and max_position[0] else 0
                
                task_obj = Task(
                    column_id=column.id,
                    position=next_position
                )
                session.add(task_obj)
            
            # Atualiza dados
            task_obj.title = title
            task_obj.description = description if description else None
            task_obj.priority = priority
            task_obj.estimated_hours = estimated_hours
            task_obj.assigned_to = assigned if assigned else None
            
            session.commit()
            messagebox.showinfo("Sucesso", "Tarefa salva com sucesso!")
            dialog.destroy()
            self._load_kanban()  # Recarrega o quadro
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar tarefa: {e}")
        finally:
            session.close()
    
    def _delete_task(self, task, dialog):
        """Exclui uma tarefa"""
        result = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a tarefa '{task.title}'?\n\nEsta ação não pode ser desfeita."
        )
        
        if not result:
            return
        
        session = db_manager.get_session()
        try:
            task_obj = session.query(Task).filter(Task.id == task.id).first()
            if task_obj:
                session.delete(task_obj)
                session.commit()
                messagebox.showinfo("Sucesso", "Tarefa excluída com sucesso!")
                dialog.destroy()
                self._load_kanban()
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir tarefa: {e}")
        finally:
            session.close()
    
    def show(self):
        """Exibe o frame de quadros"""
        self.frame.grid(row=0, column=0, sticky="nsew")
    
    def hide(self):
        """Esconde o frame de quadros"""
        self.frame.grid_remove()
    
    def refresh(self):
        """Atualiza os dados do frame"""
        self._load_boards()
        if self.selected_board:
            self._load_kanban()