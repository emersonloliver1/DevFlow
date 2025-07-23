import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from ..database.connection import db_manager
from ..database.models import TimeEntry, Project, Task, Board, BoardColumn
from ..auth.auth_manager import auth_manager

class TimesheetFrame:
    """Frame para controle de tempo"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.entries_list = None
        self.form_frame = None
        self.selected_entry = None
        self.timer_running = False
        self.timer_start_time = None
        self.timer_project_id = None
        
        # Campos do formulário
        self.project_combo = None
        self.task_combo = None
        self.description_entry = None
        self.date_entry = None
        self.start_time_entry = None
        self.end_time_entry = None
        self.duration_entry = None
        
        # Timer
        self.timer_frame = None
        self.timer_label = None
        self.timer_project_combo = None
        self.timer_task_combo = None
        self.timer_description_entry = None
        
        # Filtros
        self.filter_project_combo = None
        self.filter_date_combo = None
        
        # Estatísticas
        self.stats_frame = None
        
        self._create_widgets()
        self._update_timer_display()
    
    def _create_widgets(self):
        """Cria os widgets do frame de timesheet"""
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(fill="both", expand=True)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)
        
        # Timer (topo)
        self._create_timer_section()
        
        # Estatísticas
        self._create_stats_section()
        
        # Lista de entradas (lado esquerdo)
        self._create_entries_list()
        
        # Formulário (lado direito)
        self._create_form()
    
    def _create_timer_section(self):
        """Cria a seção do timer"""
        self.timer_frame = ctk.CTkFrame(self.frame)
        self.timer_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 10))
        self.timer_frame.grid_columnconfigure(1, weight=1)
        
        # Título
        timer_title = ctk.CTkLabel(
            self.timer_frame,
            text="⏱️ Timer",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        timer_title.grid(row=0, column=0, columnspan=3, pady=(15, 10))
        
        # Display do timer
        self.timer_label = ctk.CTkLabel(
            self.timer_frame,
            text="00:00:00",
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color="#2196F3",
            corner_radius=8,
            height=60,
            width=150
        )
        self.timer_label.grid(row=1, column=0, padx=15, pady=(0, 15))
        
        # Controles do timer
        timer_controls = ctk.CTkFrame(self.timer_frame, fg_color="transparent")
        timer_controls.grid(row=1, column=1, sticky="ew", padx=15, pady=(0, 15))
        timer_controls.grid_columnconfigure((0, 1), weight=1)
        
        # Projeto para o timer
        self.timer_project_combo = ctk.CTkComboBox(
            timer_controls,
            values=["Selecione um projeto"],
            width=200,
            command=self._on_timer_project_change
        )
        self.timer_project_combo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        # Tarefa kanban para o timer
        self.timer_task_combo = ctk.CTkComboBox(
            timer_controls,
            values=["Selecione uma tarefa (opcional)"],
            width=200
        )
        self.timer_task_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        # Descrição para o timer
        self.timer_description_entry = ctk.CTkEntry(
            timer_controls,
            placeholder_text="Descrição da atividade"
        )
        self.timer_description_entry.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Botões do timer
        self.start_btn = ctk.CTkButton(
            timer_controls,
            text="▶️ Iniciar",
            command=self._start_timer,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.start_btn.grid(row=3, column=0, padx=(0, 5), sticky="ew")
        
        self.stop_btn = ctk.CTkButton(
            timer_controls,
            text="⏹️ Parar",
            command=self._stop_timer,
            fg_color="#F44336",
            hover_color="#da190b",
            state="disabled"
        )
        self.stop_btn.grid(row=3, column=1, padx=(5, 0), sticky="ew")
    
    def _create_stats_section(self):
        """Cria a seção de estatísticas"""
        self.stats_frame = ctk.CTkFrame(self.frame)
        self.stats_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 10))
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Título
        stats_title = ctk.CTkLabel(
            self.stats_frame,
            text="📊 Estatísticas de Tempo",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        stats_title.grid(row=0, column=0, columnspan=4, pady=(10, 5))
        
        # Cards de estatísticas
        self.today_hours_label = ctk.CTkLabel(
            self.stats_frame,
            text="Hoje\n0h 0m",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#4CAF50",
            corner_radius=8,
            height=50
        )
        self.today_hours_label.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="ew")
        
        self.week_hours_label = ctk.CTkLabel(
            self.stats_frame,
            text="Esta Semana\n0h 0m",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2196F3",
            corner_radius=8,
            height=50
        )
        self.week_hours_label.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="ew")
        
        self.month_hours_label = ctk.CTkLabel(
            self.stats_frame,
            text="Este Mês\n0h 0m",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#FF9800",
            corner_radius=8,
            height=50
        )
        self.month_hours_label.grid(row=1, column=2, padx=5, pady=(0, 10), sticky="ew")
        
        self.total_hours_label = ctk.CTkLabel(
            self.stats_frame,
            text="Total\n0h 0m",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#9C27B0",
            corner_radius=8,
            height=50
        )
        self.total_hours_label.grid(row=1, column=3, padx=5, pady=(0, 10), sticky="ew")
    
    def _create_entries_list(self):
        """Cria a lista de entradas de tempo"""
        # Frame da lista
        list_frame = ctk.CTkFrame(self.frame)
        list_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_rowconfigure(3, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            list_frame,
            text="⏰ Registros de Tempo",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        # Filtros
        filters_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        filters_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        filters_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.filter_project_combo = ctk.CTkComboBox(
            filters_frame,
            values=["Todos os Projetos"],
            command=self._apply_filters
        )
        self.filter_project_combo.set("Todos os Projetos")
        self.filter_project_combo.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Filtro de data
        today = date.today()
        date_options = [
            "Hoje",
            "Esta Semana",
            "Este Mês",
            "Todos"
        ]
        
        self.filter_date_combo = ctk.CTkComboBox(
            filters_frame,
            values=date_options,
            command=self._apply_filters
        )
        self.filter_date_combo.set("Hoje")
        self.filter_date_combo.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # Botão nova entrada
        new_btn = ctk.CTkButton(
            list_frame,
            text="+ Nova Entrada",
            command=self._new_entry,
            width=200
        )
        new_btn.grid(row=2, column=0, pady=(0, 10), padx=15)
        
        # Lista scrollável
        self.entries_list = ctk.CTkScrollableFrame(list_frame, width=300)
        self.entries_list.grid(row=3, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.entries_list.grid_columnconfigure(0, weight=1)
    
    def _create_form(self):
        """Cria o formulário de entrada de tempo"""
        self.form_frame = ctk.CTkScrollableFrame(self.frame)
        self.form_frame.grid(row=2, column=1, sticky="nsew")
        self.form_frame.grid_columnconfigure(0, weight=1)
        
        # Título do formulário
        self.form_title = ctk.CTkLabel(
            self.form_frame,
            text="Nova Entrada de Tempo",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.form_title.grid(row=0, column=0, pady=(15, 20), sticky="w")
        
        # Projeto
        project_label = ctk.CTkLabel(self.form_frame, text="Projeto:*")
        project_label.grid(row=1, column=0, sticky="w", pady=(10, 5))
        
        self.project_combo = ctk.CTkComboBox(
            self.form_frame,
            values=["Carregando..."],
            command=self._on_form_project_change
        )
        self.project_combo.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        # Tarefa kanban
        task_label = ctk.CTkLabel(self.form_frame, text="Tarefa Kanban (opcional):")
        task_label.grid(row=3, column=0, sticky="w", pady=(10, 5))
        
        self.task_combo = ctk.CTkComboBox(
            self.form_frame,
            values=["Nenhuma tarefa selecionada"],
            command=self._on_task_selected
        )
        self.task_combo.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        
        # Descrição
        description_label = ctk.CTkLabel(self.form_frame, text="Descrição:*")
        description_label.grid(row=5, column=0, sticky="w", pady=(10, 5))
        
        self.description_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Descrição da atividade"
        )
        self.description_entry.grid(row=6, column=0, sticky="ew", pady=(0, 10))
        
        # Data
        date_label = ctk.CTkLabel(self.form_frame, text="Data:*")
        date_label.grid(row=7, column=0, sticky="w", pady=(10, 5))
        
        self.date_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="DD/MM/AAAA"
        )
        # Preenche com data atual
        self.date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.date_entry.grid(row=8, column=0, sticky="ew", pady=(0, 10))
        
        # Horários
        time_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        time_frame.grid(row=9, column=0, sticky="ew", pady=(10, 0))
        time_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Hora de início
        start_label = ctk.CTkLabel(time_frame, text="Hora de Início:*")
        start_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.start_time_entry = ctk.CTkEntry(
            time_frame,
            placeholder_text="HH:MM"
        )
        self.start_time_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        
        # Hora de fim
        end_label = ctk.CTkLabel(time_frame, text="Hora de Fim:*")
        end_label.grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        self.end_time_entry = ctk.CTkEntry(
            time_frame,
            placeholder_text="HH:MM"
        )
        self.end_time_entry.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        # Duração (calculada automaticamente)
        duration_label = ctk.CTkLabel(self.form_frame, text="Duração:")
        duration_label.grid(row=10, column=0, sticky="w", pady=(10, 5))
        
        self.duration_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Calculado automaticamente",
            state="disabled"
        )
        self.duration_entry.grid(row=11, column=0, sticky="ew", pady=(0, 10))
        
        # Bind para calcular duração automaticamente
        self.start_time_entry.bind('<KeyRelease>', self._calculate_duration)
        self.end_time_entry.bind('<KeyRelease>', self._calculate_duration)
        
        # Botões
        buttons_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        buttons_frame.grid(row=12, column=0, sticky="ew", pady=(20, 20))
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Salvar",
            command=self._save_entry
        )
        self.save_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.delete_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Excluir",
            command=self._delete_entry,
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
    
    def _calculate_duration(self, event=None):
        """Calcula a duração baseada nos horários de início e fim"""
        start_time = self.start_time_entry.get().strip()
        end_time = self.end_time_entry.get().strip()
        
        if not start_time or not end_time:
            return
        
        try:
            start = datetime.strptime(start_time, "%H:%M")
            end = datetime.strptime(end_time, "%H:%M")
            
            # Se o horário de fim for menor que o de início, assume que é no dia seguinte
            if end < start:
                end += timedelta(days=1)
            
            duration = end - start
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            
            self.duration_entry.configure(state="normal")
            self.duration_entry.delete(0, 'end')
            self.duration_entry.insert(0, f"{hours}h {minutes}m")
            self.duration_entry.configure(state="disabled")
            
        except ValueError:
            self.duration_entry.configure(state="normal")
            self.duration_entry.delete(0, 'end')
            self.duration_entry.configure(state="disabled")
    
    def _start_timer(self):
        """Inicia o timer"""
        project_name = self.timer_project_combo.get()
        description = self.timer_description_entry.get().strip()
        
        if project_name == "Selecione um projeto" or not hasattr(self, 'projects_data') or project_name not in self.projects_data:
            messagebox.showerror("Erro", "Selecione um projeto válido.")
            return
        
        if not description:
            messagebox.showerror("Erro", "Digite uma descrição para a atividade.")
            return
        
        self.timer_running = True
        self.timer_start_time = datetime.now()
        self.timer_project_id = self.projects_data[project_name].id
        
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.timer_project_combo.configure(state="disabled")
        self.timer_task_combo.configure(state="disabled")
        self.timer_description_entry.configure(state="disabled")
        
        # Inicia a atualização do display
        self._update_timer_display()
    
    def _stop_timer(self):
        """Para o timer e salva a entrada"""
        if not self.timer_running:
            return
        
        end_time = datetime.now()
        duration = end_time - self.timer_start_time
        
        # Salva a entrada automaticamente
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            entry = TimeEntry(
                user_id=user.id,
                project_id=self.timer_project_id,
                description=self.timer_description_entry.get().strip(),
                date=self.timer_start_time,  # Usar datetime completo
                start_time=self.timer_start_time,  # Usar datetime completo
                end_time=end_time,  # Usar datetime completo
                duration_minutes=int(duration.total_seconds() // 60)
            )
            
            session.add(entry)
            session.commit()
            
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            
            messagebox.showinfo(
                "Timer Parado",
                f"Entrada de tempo salva com sucesso!\n\n"
                f"Duração: {hours}h {minutes}m"
            )
            
            self._load_entries()
            self._update_stats()
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar entrada: {e}")
        finally:
            session.close()
        
        # Reset do timer
        self.timer_running = False
        self.timer_start_time = None
        self.timer_project_id = None
        
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.timer_project_combo.configure(state="normal")
        self.timer_task_combo.configure(state="normal")
        self.timer_description_entry.configure(state="normal")
        self.timer_description_entry.delete(0, 'end')
        
        self.timer_label.configure(text="00:00:00")
    
    def _update_timer_display(self):
        """Atualiza o display do timer"""
        if self.timer_running and self.timer_start_time:
            elapsed = datetime.now() - self.timer_start_time
            hours = elapsed.seconds // 3600
            minutes = (elapsed.seconds % 3600) // 60
            seconds = elapsed.seconds % 60
            
            self.timer_label.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Agenda próxima atualização
        if hasattr(self, 'frame') and self.frame.winfo_exists():
            self.frame.after(1000, self._update_timer_display)
    
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
            
            project_names = [project.name for project in projects]
            
            if project_names:
                # Atualiza comboboxes
                self.project_combo.configure(values=project_names)
                self.project_combo.set(project_names[0])
                
                timer_values = ["Selecione um projeto"] + project_names
                self.timer_project_combo.configure(values=timer_values)
                
                filter_projects = ["Todos os Projetos"] + project_names
                self.filter_project_combo.configure(values=filter_projects)
            else:
                self.project_combo.configure(values=["Nenhum projeto cadastrado"])
                self.timer_project_combo.configure(values=["Nenhum projeto cadastrado"])
                self.filter_project_combo.configure(values=["Nenhum projeto cadastrado"])
            
            # Armazena referência dos projetos
            self.projects_data = {project.name: project for project in projects}
            
            # Carrega tarefas para o primeiro projeto se houver
            if projects:
                self._load_tasks_for_project(projects[0].id)
            
        except Exception as e:
            print(f"Erro ao carregar projetos: {e}")
        finally:
            session.close()
    
    def _load_tasks_for_project(self, project_id):
        """Carrega as tarefas kanban para um projeto específico"""
        session = db_manager.get_session()
        try:
            # Busca boards do projeto
            boards = session.query(Board).filter(Board.project_id == project_id).all()
            
            tasks = []
            for board in boards:
                for column in board.columns:
                    for task in column.tasks:
                        tasks.append(task)
            
            if tasks:
                task_options = ["Nenhuma tarefa selecionada"] + [f"{task.title} ({task.column.name})" for task in tasks]
                if hasattr(self, 'task_combo'):
                    self.task_combo.configure(values=task_options)
                    self.task_combo.set("Nenhuma tarefa selecionada")
                if hasattr(self, 'timer_task_combo'):
                    self.timer_task_combo.configure(values=task_options)
                    self.timer_task_combo.set("Selecione uma tarefa (opcional)")
            else:
                empty_options = ["Nenhuma tarefa disponível"]
                if hasattr(self, 'task_combo'):
                    self.task_combo.configure(values=empty_options)
                    self.task_combo.set("Nenhuma tarefa disponível")
                if hasattr(self, 'timer_task_combo'):
                    self.timer_task_combo.configure(values=empty_options)
                    self.timer_task_combo.set("Nenhuma tarefa disponível")
            
            # Armazena referência das tarefas
            self.tasks_data = {f"{task.title} ({task.column.name})": task for task in tasks}
            
        except Exception as e:
            print(f"Erro ao carregar tarefas: {e}")
        finally:
            session.close()
    
    def _on_timer_project_change(self, value=None):
        """Chamado quando o projeto do timer é alterado"""
        project_name = self.timer_project_combo.get()
        if hasattr(self, 'projects_data') and project_name in self.projects_data:
            project = self.projects_data[project_name]
            self._load_tasks_for_project(project.id)
    
    def _on_form_project_change(self, value=None):
        """Chamado quando o projeto do formulário é alterado"""
        project_name = self.project_combo.get()
        if hasattr(self, 'projects_data') and project_name in self.projects_data:
            project = self.projects_data[project_name]
            self._load_tasks_for_project(project.id)
    
    def _on_task_selected(self, value=None):
        """Chamado quando uma tarefa é selecionada"""
        task_key = self.task_combo.get()
        if hasattr(self, 'tasks_data') and task_key in self.tasks_data:
            task = self.tasks_data[task_key]
            # Preenche a descrição automaticamente com o título da tarefa
            self.description_entry.delete(0, 'end')
            self.description_entry.insert(0, task.title)
    
    def _load_entries(self):
        """Carrega a lista de entradas de tempo"""
        # Limpa a lista atual
        for widget in self.entries_list.winfo_children():
            widget.destroy()
        
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            query = session.query(TimeEntry).filter(
                TimeEntry.user_id == user.id
            )
            
            # Aplica filtros
            filter_project = self.filter_project_combo.get()
            if filter_project != "Todos os Projetos" and hasattr(self, 'projects_data') and filter_project in self.projects_data:
                query = query.filter(TimeEntry.project_id == self.projects_data[filter_project].id)
            
            filter_date = self.filter_date_combo.get()
            today = date.today()
            
            if filter_date == "Hoje":
                query = query.filter(TimeEntry.date == today)
            elif filter_date == "Esta Semana":
                start_week = today - timedelta(days=today.weekday())
                end_week = start_week + timedelta(days=6)
                query = query.filter(TimeEntry.date.between(start_week, end_week))
            elif filter_date == "Este Mês":
                start_month = today.replace(day=1)
                if today.month == 12:
                    end_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    end_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
                query = query.filter(TimeEntry.date.between(start_month, end_month))
            
            entries = query.order_by(TimeEntry.date.desc(), TimeEntry.start_time.desc()).all()
            
            for i, entry in enumerate(entries):
                # Texto da entrada
                duration_text = f"{entry.duration_minutes // 60}h {entry.duration_minutes % 60}m"
                date_text = entry.date.strftime("%d/%m/%Y")
                time_text = f"{entry.start_time.strftime('%H:%M')} - {entry.end_time.strftime('%H:%M')}"
                
                entry_btn = ctk.CTkButton(
                    self.entries_list,
                    text=f"{entry.project.name}\n{entry.description}\n{date_text} | {time_text} | {duration_text}",
                    command=lambda e=entry: self._select_entry(e),
                    height=80,
                    anchor="w",
                    fg_color="#2196F3"
                )
                entry_btn.grid(row=i, column=0, sticky="ew", pady=2)
            
            if not entries:
                no_entries_label = ctk.CTkLabel(
                    self.entries_list,
                    text="Nenhuma entrada encontrada",
                    text_color="gray"
                )
                no_entries_label.grid(row=0, column=0, pady=20)
            
            # Atualiza estatísticas
            self._update_stats()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar entradas: {e}")
        finally:
            session.close()
    
    def _update_stats(self):
        """Atualiza as estatísticas de tempo"""
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            today = date.today()
            
            # Hoje
            today_entries = session.query(TimeEntry).filter(
                TimeEntry.user_id == user.id,
                TimeEntry.date == today
            ).all()
            today_minutes = sum(entry.duration_minutes for entry in today_entries)
            
            # Esta semana
            start_week = today - timedelta(days=today.weekday())
            end_week = start_week + timedelta(days=6)
            week_entries = session.query(TimeEntry).filter(
                TimeEntry.user_id == user.id,
                TimeEntry.date.between(start_week, end_week)
            ).all()
            week_minutes = sum(entry.duration_minutes for entry in week_entries)
            
            # Este mês
            start_month = today.replace(day=1)
            if today.month == 12:
                end_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            month_entries = session.query(TimeEntry).filter(
                TimeEntry.user_id == user.id,
                TimeEntry.date.between(start_month, end_month)
            ).all()
            month_minutes = sum(entry.duration_minutes for entry in month_entries)
            
            # Total
            total_entries = session.query(TimeEntry).filter(
                TimeEntry.user_id == user.id
            ).all()
            total_minutes = sum(entry.duration_minutes for entry in total_entries)
            
            # Atualiza labels
            def format_time(minutes):
                hours = minutes // 60
                mins = minutes % 60
                return f"{hours}h {mins}m"
            
            self.today_hours_label.configure(text=f"Hoje\n{format_time(today_minutes)}")
            self.week_hours_label.configure(text=f"Esta Semana\n{format_time(week_minutes)}")
            self.month_hours_label.configure(text=f"Este Mês\n{format_time(month_minutes)}")
            self.total_hours_label.configure(text=f"Total\n{format_time(total_minutes)}")
            
        except Exception as e:
            print(f"Erro ao atualizar estatísticas: {e}")
        finally:
            session.close()
    
    def _apply_filters(self, value=None):
        """Aplica os filtros selecionados"""
        self._load_entries()
    
    def _select_entry(self, entry):
        """Seleciona uma entrada e carrega seus dados no formulário"""
        self.selected_entry = entry
        
        # Preenche o formulário
        self.project_combo.set(entry.project.name)
        
        self.description_entry.delete(0, 'end')
        self.description_entry.insert(0, entry.description)
        
        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, entry.date.strftime("%d/%m/%Y"))
        
        self.start_time_entry.delete(0, 'end')
        self.start_time_entry.insert(0, entry.start_time.strftime("%H:%M"))
        
        self.end_time_entry.delete(0, 'end')
        self.end_time_entry.insert(0, entry.end_time.strftime("%H:%M"))
        
        # Calcula duração
        self._calculate_duration()
        
        # Atualiza título e habilita botão de excluir
        self.form_title.configure(text=f"Editando: {entry.description}")
        self.delete_btn.configure(state="normal")
    
    def _new_entry(self):
        """Prepara o formulário para uma nova entrada"""
        self.selected_entry = None
        self._clear_form()
        self.form_title.configure(text="Nova Entrada de Tempo")
        self.delete_btn.configure(state="disabled")
        self.description_entry.focus()
    
    def _clear_form(self):
        """Limpa o formulário"""
        if hasattr(self, 'projects_data') and self.projects_data:
            self.project_combo.set(list(self.projects_data.keys())[0])
        if hasattr(self, 'task_combo'):
            self.task_combo.set("Nenhuma tarefa selecionada")
        self.description_entry.delete(0, 'end')
        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.start_time_entry.delete(0, 'end')
        self.end_time_entry.delete(0, 'end')
        self.duration_entry.configure(state="normal")
        self.duration_entry.delete(0, 'end')
        self.duration_entry.configure(state="disabled")
    
    def _parse_date(self, date_str):
        """Converte string de data para date"""
        try:
            return datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
        except ValueError:
            return None
    
    def _parse_time(self, time_str):
        """Converte string de hora para time"""
        try:
            return datetime.strptime(time_str.strip(), "%H:%M").time()
        except ValueError:
            return None
    
    def _save_entry(self):
        """Salva a entrada de tempo"""
        project_name = self.project_combo.get()
        description = self.description_entry.get().strip()
        date_str = self.date_entry.get().strip()
        start_time_str = self.start_time_entry.get().strip()
        end_time_str = self.end_time_entry.get().strip()
        
        if not hasattr(self, 'projects_data') or project_name not in self.projects_data:
            messagebox.showerror("Erro", "Selecione um projeto válido.")
            return
        
        if not description:
            messagebox.showerror("Erro", "A descrição é obrigatória.")
            return
        
        entry_date = self._parse_date(date_str)
        if not entry_date:
            messagebox.showerror("Erro", "Data inválida. Use o formato DD/MM/AAAA.")
            return
        
        start_time = self._parse_time(start_time_str)
        if not start_time:
            messagebox.showerror("Erro", "Hora de início inválida. Use o formato HH:MM.")
            return
        
        end_time = self._parse_time(end_time_str)
        if not end_time:
            messagebox.showerror("Erro", "Hora de fim inválida. Use o formato HH:MM.")
            return
        
        # Calcula duração
        start_datetime = datetime.combine(entry_date, start_time)
        end_datetime = datetime.combine(entry_date, end_time)
        
        if end_datetime <= start_datetime:
            # Assume que terminou no dia seguinte
            end_datetime += timedelta(days=1)
        
        duration_minutes = int((end_datetime - start_datetime).total_seconds() // 60)
        
        if duration_minutes <= 0:
            messagebox.showerror("Erro", "A duração deve ser maior que zero.")
            return
        
        user = auth_manager.get_current_user()
        if not user:
            return
        
        session = db_manager.get_session()
        try:
            if self.selected_entry:
                # Atualiza entrada existente
                entry = session.query(TimeEntry).filter(
                    TimeEntry.id == self.selected_entry.id
                ).first()
                
                if not entry:
                    messagebox.showerror("Erro", "Entrada não encontrada.")
                    return
            else:
                # Cria nova entrada
                entry = TimeEntry(user_id=user.id)
                session.add(entry)
            
            # Atualiza dados - convertendo para datetime com timezone
            entry.project_id = self.projects_data[project_name].id
            entry.description = description
            entry.date = start_datetime  # Usar datetime completo para o campo date
            entry.start_time = start_datetime  # Usar datetime completo
            entry.end_time = end_datetime  # Usar datetime completo
            entry.duration_minutes = duration_minutes
            
            session.commit()
            
            messagebox.showinfo("Sucesso", "Entrada de tempo salva com sucesso!")
            self._load_entries()
            self._update_statistics()
            
            if not self.selected_entry:
                self._clear_form()
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar entrada: {e}")
        finally:
            session.close()
    
    def _delete_entry(self):
        """Exclui a entrada selecionada"""
        if not self.selected_entry:
            return
        
        # Confirma exclusão
        result = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a entrada '{self.selected_entry.description}'?\n\n"
            "Esta ação não pode ser desfeita."
        )
        
        if not result:
            return
        
        session = db_manager.get_session()
        try:
            entry = session.query(TimeEntry).filter(
                TimeEntry.id == self.selected_entry.id
            ).first()
            
            if entry:
                session.delete(entry)
                session.commit()
                
                messagebox.showinfo("Sucesso", "Entrada excluída com sucesso!")
                self._load_entries()
                self._clear_form()
                self.selected_entry = None
                self.form_title.configure(text="Nova Entrada de Tempo")
                self.delete_btn.configure(state="disabled")
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir entrada: {e}")
        finally:
            session.close()
    
    def show(self):
        """Exibe o frame de timesheet"""
        self.frame.pack(fill="both", expand=True)
    
    def hide(self):
        """Esconde o frame de timesheet"""
        self.frame.pack_forget()
    
    def refresh(self):
        """Atualiza os dados do frame"""
        self._load_projects_combo()
        self._load_entries()