import customtkinter as ctk
import tkinter.messagebox as messagebox
import webbrowser

class HelpWindow:
    """Janela de ajuda do sistema DevFlow"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.content_frame = None
        self.current_section = None
        
    def show(self):
        """Exibe a janela de ajuda"""
        if self.window is not None:
            self.window.lift()
            self.window.focus()
            return
            
        self._create_window()
        self._create_widgets()
        self._show_welcome_section()
        
    def _create_window(self):
        """Cria a janela principal de ajuda"""
        self.window = ctk.CTkToplevel()
        self.window.title("📚 DevFlow - Central de Ajuda")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        # Centraliza a janela
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Configura o grid
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Evento de fechamento
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def _create_widgets(self):
        """Cria os widgets da janela"""
        # Menu lateral
        self._create_sidebar()
        
        # Área de conteúdo
        self._create_content_area()
        
    def _create_sidebar(self):
        """Cria o menu lateral com as seções"""
        sidebar = ctk.CTkFrame(self.window, width=250)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        sidebar.grid_propagate(False)
        
        # Título
        title_label = ctk.CTkLabel(
            sidebar,
            text="📚 Central de Ajuda",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 30), padx=20)
        
        # Botões do menu
        menu_items = [
            ("🏠 Bem-vindo", self._show_welcome_section),
            ("🚀 Primeiros Passos", self._show_getting_started),
            ("🎨 Interface Moderna", self._show_modern_interface),
            ("⌨️ Atalhos de Teclado", self._show_keyboard_shortcuts),
            ("👥 Gerenciar Clientes", self._show_clients_help),
            ("📁 Gerenciar Projetos", self._show_projects_help),
            ("📋 Quadros Kanban", self._show_boards_help),
            ("💰 Controle Financeiro", self._show_finances_help),
            ("⏰ Controle de Tempo", self._show_timesheet_help),
            ("📊 Relatórios", self._show_reports_help),
            ("📄 Contratos", self._show_contracts_help),
            ("🔧 Configurações", self._show_settings_help),
            ("❓ FAQ", self._show_faq),
            ("📞 Suporte", self._show_support)
        ]
        
        for i, (text, command) in enumerate(menu_items):
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                anchor="w",
                height=35,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray20")
            )
            btn.grid(row=i+1, column=0, sticky="ew", padx=15, pady=2)
            
    def _create_content_area(self):
        """Cria a área de conteúdo principal"""
        self.content_frame = ctk.CTkScrollableFrame(self.window)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
    def _clear_content(self):
        """Limpa o conteúdo atual"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def _add_title(self, text, row=0):
        """Adiciona um título à seção"""
        title = ctk.CTkLabel(
            self.content_frame,
            text=text,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=row, column=0, sticky="w", pady=(0, 20), padx=20)
        return row + 1
        
    def _add_subtitle(self, text, row):
        """Adiciona um subtítulo à seção"""
        subtitle = ctk.CTkLabel(
            self.content_frame,
            text=text,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        subtitle.grid(row=row, column=0, sticky="w", pady=(20, 10), padx=20)
        return row + 1
        
    def _add_text(self, text, row):
        """Adiciona texto normal à seção"""
        text_label = ctk.CTkLabel(
            self.content_frame,
            text=text,
            font=ctk.CTkFont(size=14),
            justify="left",
            wraplength=700
        )
        text_label.grid(row=row, column=0, sticky="w", pady=(0, 10), padx=20)
        return row + 1
        
    def _add_step_list(self, steps, row):
        """Adiciona uma lista de passos numerados"""
        for i, step in enumerate(steps, 1):
            step_text = f"{i}. {step}"
            step_label = ctk.CTkLabel(
                self.content_frame,
                text=step_text,
                font=ctk.CTkFont(size=14),
                justify="left",
                wraplength=650
            )
            step_label.grid(row=row, column=0, sticky="w", pady=(0, 8), padx=40)
            row += 1
        return row
        
    def _add_tip_box(self, tip_text, row):
        """Adiciona uma caixa de dica"""
        tip_frame = ctk.CTkFrame(self.content_frame, fg_color=("#E3F2FD", "#1E3A8A"))
        tip_frame.grid(row=row, column=0, sticky="ew", pady=(10, 20), padx=20)
        tip_frame.grid_columnconfigure(0, weight=1)
        
        tip_label = ctk.CTkLabel(
            tip_frame,
            text=f"💡 Dica: {tip_text}",
            font=ctk.CTkFont(size=14),
            justify="left",
            wraplength=650
        )
        tip_label.grid(row=0, column=0, sticky="w", pady=15, padx=15)
        return row + 1
        
    def _show_welcome_section(self):
        """Mostra a seção de boas-vindas"""
        self._clear_content()
        row = 0
        
        row = self._add_title("🏠 Bem-vindo ao DevFlow!", row)
        
        welcome_text = (
            "O DevFlow v2.0 é sua solução completa para gerenciamento de projetos freelance com interface moderna e intuitiva. "
            "Com ele você pode controlar clientes, projetos, finanças, tempo trabalhado e muito mais!"
        )
        row = self._add_text(welcome_text, row)
        
        row = self._add_subtitle("✨ Novidades da versão 2.0:", row)
        
        new_features = [
            "🎨 Interface moderna com tema escuro/claro",
            "⌨️ Atalhos de teclado para maior produtividade",
            "📱 Design responsivo e intuitivo",
            "🚀 Performance otimizada",
            "🎯 Navegação aprimorada com sidebar colapsável",
            "📊 Cabeçalho informativo com data/hora",
            "⚡ Barra de status em tempo real"
        ]
        
        for feature in new_features:
            row = self._add_text(feature, row)
        
        row = self._add_subtitle("🎯 Funcionalidades principais:", row)
        
        features = [
            "👥 Gerenciar informações completas de clientes",
            "📁 Organizar projetos com status e orçamentos",
            "📋 Gerenciar tarefas com quadros kanban visuais",
            "💰 Controlar receitas e despesas",
            "⏰ Registrar tempo trabalhado com cronômetro",
            "📊 Gerar relatórios detalhados",
            "📄 Anexar contratos via Google Drive",
            "🔒 Sistema seguro com autenticação"
        ]
        
        for feature in features:
            row = self._add_text(feature, row)
            
        row = self._add_tip_box(
            "Para começar, clique em '🚀 Primeiros Passos' no menu lateral! Ou explore a nova '🎨 Interface Moderna' para conhecer as novidades.",
            row
        )
    
    def _show_modern_interface(self):
        """Mostra informações sobre a interface moderna"""
        self._clear_content()
        row = 0
        
        row = self._add_title("🎨 Interface Moderna - DevFlow v2.0", row)
        
        intro_text = (
            "O DevFlow v2.0 apresenta uma interface completamente renovada, "
            "focada na produtividade e experiência do usuário."
        )
        row = self._add_text(intro_text, row)
        
        row = self._add_subtitle("🌙 Temas Escuro e Claro", row)
        
        theme_text = (
            "Alterne entre tema escuro e claro conforme sua preferência. "
            "O tema escuro reduz o cansaço visual durante longas sessões de trabalho."
        )
        row = self._add_text(theme_text, row)
        
        theme_steps = [
            "Clique no botão 🌙/☀️ no cabeçalho superior direito",
            "Ou use o atalho Ctrl+T para alternar rapidamente",
            "O tema será aplicado instantaneamente em toda a interface"
        ]
        row = self._add_step_list(theme_steps, row)
        
        row = self._add_subtitle("📱 Sidebar Colapsável", row)
        
        sidebar_text = (
            "A barra lateral pode ser colapsada para maximizar o espaço de trabalho. "
            "Ideal para telas menores ou quando você precisa de mais espaço."
        )
        row = self._add_text(sidebar_text, row)
        
        sidebar_steps = [
            "Clique no botão ◀/▶ no cabeçalho superior direito",
            "Ou use o atalho Ctrl+B para colapsar/expandir",
            "No modo colapsado, apenas os ícones ficam visíveis"
        ]
        row = self._add_step_list(sidebar_steps, row)
        
        row = self._add_subtitle("📊 Cabeçalho Informativo", row)
        
        header_text = (
            "O novo cabeçalho exibe informações importantes em tempo real:"
        )
        row = self._add_text(header_text, row)
        
        header_features = [
            "🚀 Logo e versão do DevFlow",
            "📅 Data e hora atual",
            "👤 Informações do usuário logado",
            "🌙 Controle de tema",
            "◀ Controle da sidebar"
        ]
        
        for feature in header_features:
            row = self._add_text(feature, row)
        
        row = self._add_subtitle("⚡ Barra de Status", row)
        
        status_text = (
            "A barra inferior mostra o status do sistema e dicas úteis:"
        )
        row = self._add_text(status_text, row)
        
        status_features = [
            "✅ Status operacional do sistema",
            "💡 Dicas de atalhos de teclado",
            "📊 Informações de performance"
        ]
        
        for feature in status_features:
            row = self._add_text(feature, row)
        
        row = self._add_tip_box(
            "A interface se adapta automaticamente ao seu tema preferido e mantém suas configurações!",
            row
        )
    
    def _show_keyboard_shortcuts(self):
        """Mostra os atalhos de teclado disponíveis"""
        self._clear_content()
        row = 0
        
        row = self._add_title("⌨️ Atalhos de Teclado", row)
        
        intro_text = (
            "Use estes atalhos para navegar mais rapidamente pelo DevFlow e "
            "aumentar sua produtividade."
        )
        row = self._add_text(intro_text, row)
        
        row = self._add_subtitle("🎨 Controles de Interface", row)
        
        interface_shortcuts = [
            "F11 - Alternar tela cheia",
            "Ctrl+T - Alternar tema (escuro/claro)",
            "Ctrl+B - Colapsar/expandir sidebar",
            "Esc - Fechar janelas modais"
        ]
        
        for shortcut in interface_shortcuts:
            row = self._add_text(f"• {shortcut}", row)
        
        row = self._add_subtitle("🚀 Navegação Rápida", row)
        
        nav_text = (
            "Em breve: atalhos para navegação rápida entre módulos serão adicionados."
        )
        row = self._add_text(nav_text, row)
        
        row = self._add_subtitle("⏰ Timesheet", row)
        
        timesheet_shortcuts = [
            "Ctrl+Enter - Salvar entrada de tempo",
            "Ctrl+N - Nova entrada",
            "Ctrl+S - Iniciar/parar timer",
            "Delete - Excluir entrada selecionada"
        ]
        
        for shortcut in timesheet_shortcuts:
            row = self._add_text(f"• {shortcut}", row)
        
        row = self._add_subtitle("📋 Geral", row)
        
        general_shortcuts = [
            "Ctrl+R - Atualizar dados",
            "Ctrl+F - Buscar/filtrar",
            "Ctrl+P - Imprimir/exportar",
            "F1 - Abrir ajuda"
        ]
        
        for shortcut in general_shortcuts:
            row = self._add_text(f"• {shortcut}", row)
        
        row = self._add_tip_box(
            "Dica: Os atalhos são exibidos na barra de status inferior para referência rápida!",
            row
        )
        
    def _show_getting_started(self):
        """Mostra o guia de primeiros passos"""
        self._clear_content()
        row = 0
        
        row = self._add_title("🚀 Primeiros Passos", row)
        
        intro_text = (
            "Siga este guia passo a passo para configurar seu DevFlow e começar a gerenciar "
            "seus projetos de forma eficiente!"
        )
        row = self._add_text(intro_text, row)
        
        row = self._add_subtitle("📋 Configuração Inicial:", row)
        
        initial_steps = [
            "🔐 Faça login com suas credenciais",
            "👥 Cadastre seus primeiros clientes na aba 'Clientes'",
            "📁 Crie seu primeiro projeto na aba 'Projetos'",
            "📋 Crie quadros kanban para organizar tarefas na aba 'Quadros'",
            "💰 Configure categorias financeiras em 'Finanças'",
            "⏰ Comece a registrar tempo na aba 'Timesheet'"
        ]
        
        row = self._add_step_list(initial_steps, row)
        
        row = self._add_subtitle("🎯 Fluxo de Trabalho Recomendado:", row)
        
        workflow_steps = [
            "Cadastre o cliente antes de criar projetos",
            "Defina orçamento e prazos no projeto",
            "Crie quadros kanban e organize tarefas por colunas",
            "Anexe contratos via Google Drive",
            "Use o cronômetro para registrar tempo trabalhado (integrado com tarefas)",
            "Registre receitas e despesas relacionadas",
            "Gere relatórios para acompanhar o progresso"
        ]
        
        row = self._add_step_list(workflow_steps, row)
        
        row = self._add_tip_box(
            "Mantenha seus dados sempre atualizados para relatórios mais precisos!",
            row
        )
        
    def _show_clients_help(self):
        """Mostra ajuda sobre gerenciamento de clientes"""
        self._clear_content()
        row = 0
        
        row = self._add_title("👥 Gerenciar Clientes", row)
        
        intro_text = (
            "O módulo de clientes permite organizar todas as informações dos seus clientes "
            "de forma centralizada e eficiente."
        )
        row = self._add_text(intro_text, row)
        
        row = self._add_subtitle("➕ Como Cadastrar um Cliente:", row)
        
        add_steps = [
            "Clique no botão '+ Novo Cliente'",
            "Preencha o nome (obrigatório)",
            "Adicione email, telefone e empresa",
            "Inclua endereço completo se necessário",
            "Use o campo 'Observações' para notas importantes",
            "Clique em '💾 Salvar' para confirmar"
        ]
        
        row = self._add_step_list(add_steps, row)
        
        row = self._add_subtitle("✏️ Como Editar um Cliente:", row)
        
        edit_steps = [
            "Clique no cliente desejado na lista lateral",
            "Os dados aparecerão no formulário",
            "Modifique as informações necessárias",
            "Clique em '💾 Salvar' para confirmar as alterações"
        ]
        
        row = self._add_step_list(edit_steps, row)
        
        row = self._add_subtitle("🗑️ Como Excluir um Cliente:", row)
        
        delete_steps = [
            "Selecione o cliente na lista",
            "Clique no botão '🗑️ Excluir'",
            "Confirme a exclusão na janela que aparecer",
            "⚠️ ATENÇÃO: Isso excluirá também todos os projetos relacionados!"
        ]
        
        row = self._add_step_list(delete_steps, row)
        
        row = self._add_tip_box(
            "Mantenha os dados dos clientes sempre atualizados para facilitar o contato!",
            row
        )
        
    def _show_boards_help(self):
        """Mostra ajuda sobre quadros kanban"""
        self._clear_content()
        row = 0
        
        row = self._add_title("📋 Quadros Kanban", row)
        
        intro_text = (
            "Os quadros kanban permitem organizar tarefas dos seus projetos de forma visual, "
            "usando colunas para representar o status de cada atividade."
        )
        row = self._add_text(intro_text, row)
        
        row = self._add_subtitle("🎯 Como Funciona:", row)
        
        kanban_info = (
            "Cada quadro é baseado em um projeto e possui 4 colunas padrão:\n"
            "• 🟠 A Fazer: Tarefas planejadas\n"
            "• 🔵 Em Progresso: Tarefas sendo executadas\n"
            "• 🟣 Em Revisão: Tarefas aguardando validação\n"
            "• 🟢 Concluído: Tarefas finalizadas"
        )
        row = self._add_text(kanban_info, row)
        
        row = self._add_subtitle("📋 Como Criar um Quadro:", row)
        
        create_board_steps = [
            "Clique em '+ Criar Quadro'",
            "Digite o nome do quadro (ex: 'Tarefas - Site E-commerce')",
            "Selecione o projeto associado",
            "Adicione uma descrição opcional",
            "Clique em 'Criar'",
            "O quadro será criado com as 4 colunas padrão"
        ]
        
        row = self._add_step_list(create_board_steps, row)
        
        row = self._add_subtitle("➕ Como Adicionar Tarefas:", row)
        
        add_task_steps = [
            "Clique em '+ Adicionar Tarefa' na coluna desejada",
            "Digite o título da tarefa (obrigatório)",
            "Adicione uma descrição detalhada",
            "Defina a prioridade (Baixa, Média, Alta)",
            "Estime as horas necessárias (opcional)",
            "Defina um responsável (opcional)",
            "Clique em 'Salvar'"
        ]
        
        row = self._add_step_list(add_task_steps, row)
        
        row = self._add_subtitle("✏️ Como Editar/Mover Tarefas:", row)
        
        edit_task_steps = [
            "Clique sobre qualquer tarefa para editá-la",
            "Modifique os campos necessários",
            "Para mover entre colunas, edite a tarefa e mude o status",
            "Ou arraste e solte entre as colunas (em desenvolvimento)",
            "Use as cores de prioridade para organização visual"
        ]
        
        row = self._add_step_list(edit_task_steps, row)
        
        row = self._add_subtitle("⏰ Integração com Timesheet:", row)
        
        timesheet_integration = (
            "O sistema de quadros está integrado com o controle de tempo:\n"
            "• No cronômetro, você pode selecionar uma tarefa específica\n"
            "• No formulário manual, escolha tarefa + projeto\n"
            "• A descrição é preenchida automaticamente com o título da tarefa\n"
            "• Facilita o rastreamento preciso do tempo por atividade"
        )
        row = self._add_text(timesheet_integration, row)
        
        row = self._add_subtitle("🎨 Códigos de Cores:", row)
        
        color_codes = [
            "🔴 Prioridade Alta: Tarefas urgentes e importantes",
            "🟠 Prioridade Média: Tarefas importantes mas não urgentes", 
            "🟢 Prioridade Baixa: Tarefas de menor importância",
            "🟦 Coluna 'A Fazer': Cor laranja padrão",
            "🟦 Coluna 'Em Progresso': Cor azul padrão",
            "🟣 Coluna 'Em Revisão': Cor roxa padrão",
            "🟢 Coluna 'Concluído': Cor verde padrão"
        ]
        
        for color in color_codes:
            row = self._add_text(color, row)
        
        row = self._add_subtitle("📊 Benefícios do Kanban:", row)
        
        benefits = [
            "🎯 Visualização clara do progresso do projeto",
            "⚡ Identificação rápida de gargalos",
            "📈 Melhoria contínua do fluxo de trabalho",
            "👥 Comunicação clara com clientes sobre status",
            "⏰ Integração direta com controle de tempo",
            "🔄 Flexibilidade para reorganizar prioridades"
        ]
        
        for benefit in benefits:
            row = self._add_text(benefit, row)
            
        row = self._add_tip_box(
            "Use descrições claras nas tarefas e mantenha o quadro sempre atualizado para máxima eficiência!",
            row
        )
        
    def _show_projects_help(self):
        """Mostra ajuda sobre gerenciamento de projetos"""
        self._clear_content()
        row = 0
        
        row = self._add_title("📁 Gerenciar Projetos", row)
        
        intro_text = (
            "O módulo de projetos é o coração do DevFlow. Aqui você organiza todos os seus "
            "trabalhos, define orçamentos, prazos e anexa contratos."
        )
        row = self._add_text(intro_text, row)
        
        row = self._add_subtitle("➕ Como Criar um Projeto:", row)
        
        create_steps = [
            "Clique em '+ Novo Projeto'",
            "Digite o nome do projeto (obrigatório)",
            "Selecione o cliente na lista",
            "Adicione uma descrição detalhada",
            "Defina o orçamento em reais (R$)",
            "Escolha o status inicial (geralmente 'Proposta')",
            "Defina datas de início e fim (formato DD/MM/AAAA)",
            "Anexe o contrato via Google Drive (opcional)",
            "Clique em '💾 Salvar'"
        ]
        
        row = self._add_step_list(create_steps, row)
        
        row = self._add_subtitle("📄 Como Anexar Contratos:", row)
        
        contract_steps = [
            "Faça upload do contrato para o Google Drive",
            "Compartilhe o arquivo e copie o link",
            "No projeto, preencha o nome do arquivo",
            "Cole o link do Google Drive",
            "Clique em '📄 Abrir Contrato' para testar",
            "Salve o projeto"
        ]
        
        row = self._add_step_list(contract_steps, row)
        
        row = self._add_subtitle("🎨 Status dos Projetos:", row)
        
        status_info = [
            "🟠 Proposta: Projeto em negociação",
            "🟢 Ativo: Projeto em desenvolvimento",
            "🔵 Concluído: Projeto finalizado",
            "🔴 Cancelado: Projeto cancelado",
            "⚫ Pausado: Projeto temporariamente parado"
        ]
        
        for status in status_info:
            row = self._add_text(status, row)
            
        row = self._add_tip_box(
            "Use os status para organizar visualmente seus projetos na lista!",
            row
        )
        
    def _show_finances_help(self):
        """Mostra ajuda sobre controle financeiro"""
        self._clear_content()
        row = 0
        
        row = self._add_title("💰 Controle Financeiro", row)
        
        intro_text = (
            "O módulo financeiro permite controlar todas as receitas e despesas dos seus "
            "projetos, mantendo sua contabilidade organizada."
        )
        row = self._add_text(intro_text, row)
        
        row = self._add_subtitle("💵 Como Registrar uma Receita:", row)
        
        income_steps = [
            "Clique em '+ Nova Transação'",
            "Selecione 'Receita' no tipo",
            "Escolha o projeto relacionado",
            "Digite o valor recebido",
            "Adicione uma descrição (ex: 'Pagamento 1ª parcela')",
            "Defina a data do recebimento",
            "Escolha uma categoria (ex: 'Pagamento Cliente')",
            "Clique em '💾 Salvar'"
        ]
        
        row = self._add_step_list(income_steps, row)
        
        row = self._add_subtitle("💸 Como Registrar uma Despesa:", row)
        
        expense_steps = [
            "Clique em '+ Nova Transação'",
            "Selecione 'Despesa' no tipo",
            "Escolha o projeto (ou deixe em branco para despesa geral)",
            "Digite o valor gasto",
            "Descreva a despesa (ex: 'Compra de software')",
            "Defina a data da despesa",
            "Escolha uma categoria (ex: 'Software', 'Hardware')",
            "Clique em '💾 Salvar'"
        ]
        
        row = self._add_step_list(expense_steps, row)
        
        row = self._add_subtitle("📊 Visualizando o Resumo:", row)
        
        summary_text = (
            "O painel superior mostra automaticamente:\n"
            "• Total de receitas do mês\n"
            "• Total de despesas do mês\n"
            "• Lucro líquido (receitas - despesas)\n"
            "• Gráfico de evolução mensal"
        )
        row = self._add_text(summary_text, row)
        
        row = self._add_tip_box(
            "Categorize suas transações para ter relatórios mais detalhados!",
            row
        )
        
    def _show_timesheet_help(self):
        """Mostra ajuda sobre controle de tempo"""
        self._clear_content()
        row = 0
        
        row = self._add_title("⏰ Controle de Tempo", row)
        
        intro_text = (
            "O módulo de timesheet permite registrar o tempo trabalhado em cada projeto, "
            "seja usando o cronômetro em tempo real ou registrando manualmente. Agora integrado "
            "com os quadros kanban para rastreamento preciso por tarefa."
        )
        row = self._add_text(intro_text, row)
        
        row = self._add_subtitle("⏱️ Usando o Cronômetro:", row)
        
        timer_steps = [
            "Selecione o projeto no dropdown",
            "Escolha uma tarefa kanban (opcional) - a descrição será preenchida automaticamente",
            "Ou digite uma descrição manual da atividade",
            "Clique em '▶️ Iniciar' para começar a contar",
            "O cronômetro mostrará o tempo em tempo real",
            "Clique em '⏹️ Parar' para finalizar e salvar",
            "O registro será salvo automaticamente"
        ]
        
        row = self._add_step_list(timer_steps, row)
        
        row = self._add_subtitle("✏️ Registro Manual:", row)
        
        manual_steps = [
            "Clique em '+ Novo Registro'",
            "Selecione o projeto",
            "Escolha uma tarefa kanban (se disponível) - preenche descrição automaticamente",
            "Ou digite a descrição da atividade manualmente",
            "Defina a data (formato DD/MM/AAAA)",
            "Digite horário de início (HH:MM)",
            "Digite horário de fim (HH:MM)",
            "A duração será calculada automaticamente",
            "Clique em '💾 Salvar'"
        ]
        
        row = self._add_step_list(manual_steps, row)
        
        row = self._add_subtitle("📊 Visualizando Registros:", row)
        
        view_text = (
            "A lista mostra todos os registros com:\n"
            "• Data e horários\n"
            "• Projeto e descrição\n"
            "• Duração total\n"
            "• Botões para editar ou excluir"
        )
        row = self._add_text(view_text, row)
        
        row = self._add_tip_box(
            "Use descrições detalhadas para lembrar exatamente o que foi feito!",
            row
        )
        
    def _show_reports_help(self):
        """Mostra ajuda sobre relatórios"""
        self._clear_content()
        row = 0
        
        row = self._add_title("📊 Relatórios", row)
        
        intro_text = (
            "O módulo de relatórios gera análises detalhadas dos seus projetos, "
            "finanças e produtividade para ajudar na tomada de decisões."
        )
        row = self._add_text(intro_text, row)
        
        row = self._add_subtitle("📈 Tipos de Relatórios:", row)
        
        report_types = [
            "💰 Financeiro: Receitas, despesas e lucro por período",
            "⏰ Produtividade: Horas trabalhadas por projeto",
            "📁 Projetos: Status e progresso dos projetos",
            "👥 Clientes: Faturamento por cliente",
            "📅 Mensal: Resumo completo do mês"
        ]
        
        for report_type in report_types:
            row = self._add_text(report_type, row)
            
        row = self._add_subtitle("🔍 Como Gerar Relatórios:", row)
        
        generate_steps = [
            "Escolha o tipo de relatório desejado",
            "Defina o período (data inicial e final)",
            "Selecione filtros específicos (projeto, cliente, etc.)",
            "Clique em 'Gerar Relatório'",
            "Visualize os dados na tela",
            "Use 'Exportar PDF' para salvar o relatório"
        ]
        
        row = self._add_step_list(generate_steps, row)
        
        row = self._add_tip_box(
            "Gere relatórios mensais para acompanhar a evolução do seu negócio!",
            row
        )
        
    def _show_contracts_help(self):
        """Mostra ajuda sobre contratos"""
        self._clear_content()
        row = 0
        
        row = self._add_title("📄 Contratos", row)
        
        intro_text = (
            "O sistema permite anexar contratos aos projetos usando links do Google Drive, "
            "mantendo seus documentos organizados e acessíveis."
        )
        row = self._add_text(intro_text, row)
        
        row = self._add_subtitle("☁️ Preparando o Google Drive:", row)
        
        drive_steps = [
            "Faça upload do contrato para o Google Drive",
            "Clique com botão direito no arquivo",
            "Selecione 'Compartilhar'",
            "Altere para 'Qualquer pessoa com o link'",
            "Copie o link compartilhado"
        ]
        
        row = self._add_step_list(drive_steps, row)
        
        row = self._add_subtitle("🔗 Anexando ao Projeto:", row)
        
        attach_steps = [
            "Abra o projeto desejado",
            "Role até a seção 'Contrato (Google Drive)'",
            "Digite o nome do arquivo (ex: 'Contrato_Cliente_2024.pdf')",
            "Cole o link do Google Drive",
            "O botão '📄 Abrir Contrato' ficará ativo",
            "Teste clicando no botão",
            "Salve o projeto"
        ]
        
        row = self._add_step_list(attach_steps, row)
        
        row = self._add_subtitle("✅ Vantagens desta Solução:", row)
        
        advantages = [
            "🚀 Sem custos adicionais de armazenamento",
            "☁️ Backup automático pelo Google",
            "🌐 Acesso de qualquer lugar",
            "📱 Compatível com dispositivos móveis",
            "🔒 Controle de permissões pelo Google Drive"
        ]
        
        for advantage in advantages:
            row = self._add_text(advantage, row)
            
        row = self._add_tip_box(
            "Organize seus contratos em pastas no Google Drive para facilitar o gerenciamento!",
            row
        )
        
    def _show_settings_help(self):
        """Mostra ajuda sobre configurações"""
        self._clear_content()
        row = 0
        
        row = self._add_title("🔧 Configurações", row)
        
        intro_text = (
            "As configurações permitem personalizar o DevFlow de acordo com suas "
            "preferências e necessidades específicas."
        )
        row = self._add_text(intro_text, row)
        
        row = self._add_subtitle("👤 Perfil do Usuário:", row)
        
        profile_text = (
            "• Alterar nome completo\n"
            "• Atualizar email\n"
            "• Modificar senha\n"
            "• Configurar foto de perfil"
        )
        row = self._add_text(profile_text, row)
        
        row = self._add_subtitle("🎨 Aparência:", row)
        
        appearance_text = (
            "• Tema claro/escuro\n"
            "• Cores personalizadas\n"
            "• Tamanho da fonte\n"
            "• Layout das telas"
        )
        row = self._add_text(appearance_text, row)
        
        row = self._add_subtitle("💾 Backup e Dados:", row)
        
        backup_text = (
            "• Exportar dados\n"
            "• Importar dados\n"
            "• Limpar cache\n"
            "• Configurar backup automático"
        )
        row = self._add_text(backup_text, row)
        
        row = self._add_tip_box(
            "Faça backup regular dos seus dados para evitar perdas!",
            row
        )
        
    def _show_faq(self):
        """Mostra perguntas frequentes"""
        self._clear_content()
        row = 0
        
        row = self._add_title("❓ Perguntas Frequentes (FAQ)", row)
        
        faqs = [
            {
                "question": "🔐 Como alterar minha senha?",
                "answer": "Vá em Configurações > Perfil > Alterar Senha. Digite a senha atual e a nova senha duas vezes."
            },
            {
                "question": "💾 Os dados ficam salvos na nuvem?",
                "answer": "Sim! O DevFlow usa o banco de dados Neon PostgreSQL na nuvem, garantindo segurança e acesso de qualquer lugar."
            },
            {
                "question": "📱 Posso usar no celular?",
                "answer": "O DevFlow é um aplicativo desktop. Para acesso móvel, recomendamos usar o Google Drive para visualizar contratos."
            },
            {
                "question": "🗑️ Como recuperar um projeto excluído?",
                "answer": "Infelizmente não é possível recuperar projetos excluídos. Sempre confirme antes de excluir dados importantes."
            },
            {
                "question": "⏰ O cronômetro funciona se eu fechar o programa?",
                "answer": "Não, o cronômetro para quando o programa é fechado. Para sessões longas, use pausas regulares."
            },
            {
                "question": "💰 Como categorizar transações?",
                "answer": "Use categorias como 'Pagamento Cliente', 'Software', 'Hardware', 'Marketing' para organizar suas finanças."
            },
            {
                "question": "📊 Posso exportar relatórios?",
                "answer": "Sim! Todos os relatórios podem ser exportados em PDF através do botão 'Exportar PDF'."
            },
            {
                "question": "🔄 Como fazer backup dos dados?",
                "answer": "Vá em Configurações > Backup e Dados > Exportar Dados para salvar uma cópia local."
            }
        ]
        
        for faq in faqs:
            row = self._add_subtitle(faq["question"], row)
            row = self._add_text(faq["answer"], row)
            
    def _show_support(self):
        """Mostra informações de suporte"""
        self._clear_content()
        row = 0
        
        row = self._add_title("📞 Suporte e Contato", row)
        
        intro_text = (
            "Precisa de ajuda adicional? Entre em contato conosco através dos "
            "canais disponíveis abaixo."
        )
        row = self._add_text(intro_text, row)
        
        row = self._add_subtitle("🆘 Canais de Suporte:", row)
        
        # Botão de email
        email_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        email_frame.grid(row=row, column=0, sticky="ew", pady=10, padx=20)
        
        email_btn = ctk.CTkButton(
            email_frame,
            text="📧 Enviar Email de Suporte",
            command=lambda: webbrowser.open("mailto:suporte@devflow.com?subject=Suporte DevFlow"),
            height=40
        )
        email_btn.pack(side="left", padx=(0, 10))
        
        # Botão do GitHub
        github_btn = ctk.CTkButton(
            email_frame,
            text="🐙 Abrir Issue no GitHub",
            command=lambda: webbrowser.open("https://github.com/devflow/issues"),
            height=40,
            fg_color="#24292e",
            hover_color="#1a1e22"
        )
        github_btn.pack(side="left")
        
        row += 1
        
        row = self._add_subtitle("📋 Informações do Sistema:", row)
        
        system_info = (
            "• Versão: DevFlow v1.0.0\n"
            "• Banco de Dados: Neon PostgreSQL\n"
            "• Framework: CustomTkinter\n"
            "• Python: 3.13+"
        )
        row = self._add_text(system_info, row)
        
        row = self._add_subtitle("🚀 Recursos Futuros:", row)
        
        future_features = [
            "📱 Aplicativo móvel",
            "🔄 Sincronização automática",
            "📈 Dashboard avançado",
            "🤖 Automações inteligentes",
            "🌐 API para integrações"
        ]
        
        for feature in future_features:
            row = self._add_text(feature, row)
            
        row = self._add_tip_box(
            "Sua opinião é importante! Envie sugestões e feedback para melhorarmos o DevFlow.",
            row
        )
        
    def _on_close(self):
        """Fecha a janela de ajuda"""
        self.window.destroy()
        self.window = None