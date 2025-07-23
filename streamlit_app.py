#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DevFlow - Sistema de Gestão para Freelancers
Versão Web com Streamlit
"""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import config
from src.database.connection import DatabaseManager
from src.auth.auth_manager import AuthManager
from src.database.models import User, Client, Project, Transaction, TimeEntry, ProjectStatus, TransactionType
from src.utils.logger import setup_logger
from sqlalchemy.orm import joinedload
import bcrypt

# Configuração da página
st.set_page_config(
    page_title="DevFlow - Gestão para Freelancers",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def init_app():
    """Inicializa a aplicação"""
    if 'initialized' not in st.session_state:
        try:
            # Configura o logger
            logger = setup_logger()
            logger.info(f"Iniciando {config.APP_NAME} v{config.APP_VERSION} - Streamlit")
            
            # Valida configurações
            config.validate_config()
            
            # Inicializa o gerenciador de banco de dados
            db_manager = DatabaseManager()
            
            # Verifica conexão com o banco
            if not db_manager.test_connection():
                st.error("Falha na conexão com o banco de dados")
                st.stop()
            
            # Executa migrações se necessário
            db_manager.run_migrations()
            
            # Inicializa o gerenciador de autenticação
            auth_manager = AuthManager()
            
            st.session_state.db_manager = db_manager
            st.session_state.auth_manager = auth_manager
            st.session_state.initialized = True
            
        except Exception as e:
            st.error(f"Erro fatal: {e}")
            st.stop()

def login_page():
    """Página de login"""
    st.markdown('<h1 class="main-header">🚀 DevFlow</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Sistema de Gestão Completa para Freelancers</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["Login", "Registrar"])
        
        with tab1:
            st.subheader("Fazer Login")
            st.info("💡 Use seu **email** ou **nome de usuário** para fazer login")
            with st.form("login_form"):
                email = st.text_input("📧 Email ou Nome de Usuário")
                password = st.text_input("🔒 Senha", type="password")
                submit = st.form_submit_button("Entrar")
                
                if submit:
                    if email and password:
                        token = st.session_state.auth_manager.login(email, password)
                        if token:
                            # Carrega o usuário atual após login bem-sucedido
                            user = st.session_state.auth_manager.get_current_user()
                            if user:
                                st.session_state.user = user
                                st.session_state.user_id = user.id
                                st.session_state.user_name = user.full_name
                                st.session_state.token = token
                                st.success("Login realizado com sucesso!")
                                st.rerun()
                            else:
                                st.error("Erro ao carregar dados do usuário")
                        else:
                            st.error("Email ou senha incorretos")
                    else:
                        st.error("Preencha todos os campos")
        
        with tab2:
            st.subheader("Criar Conta")
            with st.form("register_form"):
                name = st.text_input("Nome completo")
                email = st.text_input("Email", key="reg_email")
                password = st.text_input("Senha", type="password", key="reg_password")
                confirm_password = st.text_input("Confirmar senha", type="password")
                submit = st.form_submit_button("Registrar")
                
                if submit:
                    if name and email and password and confirm_password:
                        if password != confirm_password:
                            st.error("As senhas não coincidem")
                        elif len(password) < 6:
                            st.error("A senha deve ter pelo menos 6 caracteres")
                        else:
                            try:
                                session = st.session_state.db_manager.get_session()
                                
                                # Verifica se o email já existe
                                existing_user = session.query(User).filter(User.email == email).first()
                                if existing_user:
                                    st.error("Este email já está cadastrado")
                                else:
                                    # Cria novo usuário
                                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                                    user = User(
                                        name=name,
                                        email=email,
                                        password_hash=hashed_password.decode('utf-8')
                                    )
                                    session.add(user)
                                    session.commit()
                                    
                                    st.success("Conta criada com sucesso! Faça login para continuar.")
                                    
                                session.close()
                            except Exception as e:
                                st.error(f"Erro ao criar conta: {e}")
                    else:
                        st.error("Preencha todos os campos")

def dashboard_page():
    """Página do dashboard"""
    st.markdown('<h1 class="main-header">📊 Dashboard</h1>', unsafe_allow_html=True)
    
    user = st.session_state.user
    session = st.session_state.db_manager.get_session()
    
    try:
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        # Total de clientes
        total_clients = session.query(Client).filter(
            Client.user_id == user.id,
            Client.is_active == True
        ).count()
        
        # Total de projetos ativos
        active_projects = session.query(Project).filter(
            Project.user_id == user.id,
            Project.status == ProjectStatus.ATIVO
        ).count()
        
        # Receitas do mês
        current_month = datetime.now().replace(day=1)
        monthly_income = session.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.RECEITA,
            Transaction.date >= current_month
        ).with_entities(Transaction.amount).all()
        monthly_income_total = sum([t.amount for t in monthly_income]) if monthly_income else 0
        
        # Horas trabalhadas no mês
        monthly_hours = session.query(TimeEntry).filter(
            TimeEntry.user_id == user.id,
            TimeEntry.date >= current_month
        ).with_entities(TimeEntry.duration_minutes).all()
        monthly_hours_total = sum([t.duration_minutes/60 for t in monthly_hours]) if monthly_hours else 0
        
        with col1:
            st.metric("Clientes Ativos", total_clients)
        
        with col2:
            st.metric("Projetos Ativos", active_projects)
        
        with col3:
            st.metric("Receita do Mês", f"R$ {monthly_income_total:,.2f}")
        
        with col4:
            st.metric("Horas do Mês", f"{monthly_hours_total:.1f}h")
        
        st.divider()
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Receitas vs Despesas (Últimos 6 meses)")
            
            # Dados dos últimos 6 meses
            six_months_ago = datetime.now() - timedelta(days=180)
            transactions = session.query(Transaction).filter(
                Transaction.user_id == user.id,
                Transaction.date >= six_months_ago
            ).all()
            
            if transactions:
                df_transactions = pd.DataFrame([
                    {
                        'Data': t.date,
                        'Tipo': 'Receita' if t.type == TransactionType.RECEITA else 'Despesa',
                        'Valor': t.amount if t.type == TransactionType.RECEITA else -t.amount
                    }
                    for t in transactions
                ])
                
                df_monthly = df_transactions.groupby([df_transactions['Data'].dt.to_period('M'), 'Tipo'])['Valor'].sum().reset_index()
                df_monthly['Data'] = df_monthly['Data'].astype(str)
                
                fig = px.bar(df_monthly, x='Data', y='Valor', color='Tipo',
                           title="Receitas vs Despesas por Mês")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nenhuma transação encontrada")
        
        with col2:
            st.subheader("🕒 Horas Trabalhadas (Últimas 4 semanas)")
            
            # Dados das últimas 4 semanas
            four_weeks_ago = datetime.now() - timedelta(weeks=4)
            time_entries = session.query(TimeEntry).filter(
                TimeEntry.user_id == user.id,
                TimeEntry.date >= four_weeks_ago
            ).all()
            
            if time_entries:
                df_time = pd.DataFrame([
                    {
                        'Data': t.date,
                        'Horas': t.duration_minutes/60 if t.duration_minutes else 0
                    }
                    for t in time_entries
                ])
                
                df_weekly = df_time.groupby(df_time['Data'].dt.to_period('W'))['Horas'].sum().reset_index()
                df_weekly['Data'] = df_weekly['Data'].astype(str)
                
                fig = px.line(df_weekly, x='Data', y='Horas',
                            title="Horas Trabalhadas por Semana")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nenhum registro de tempo encontrado")
        
        # Projetos ativos
        st.subheader("🚀 Projetos Ativos")
        active_projects_list = session.query(Project).options(
            joinedload(Project.client)
        ).filter(
            Project.user_id == user.id,
            Project.status == ProjectStatus.ATIVO
        ).all()
        
        if active_projects_list:
            for project in active_projects_list:
                with st.expander(f"📁 {project.name} - {project.client.name}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Status:** {project.status.value.title()}")
                    with col2:
                        if project.budget:
                            st.write(f"**Orçamento:** R$ {project.budget:,.2f}")
                    with col3:
                        if project.start_date:
                            st.write(f"**Início:** {project.start_date.strftime('%d/%m/%Y')}")
                    
                    if project.description:
                        st.write(f"**Descrição:** {project.description}")
        else:
            st.info("Nenhum projeto ativo encontrado")
    
    finally:
        session.close()

def clients_page():
    """Página de gestão de clientes"""
    st.markdown('<h1 class="main-header">👥 Gestão de Clientes</h1>', unsafe_allow_html=True)
    
    user = st.session_state.user
    session = st.session_state.db_manager.get_session()
    
    try:
        # Sidebar para ações
        with st.sidebar:
            st.markdown('<div class="sidebar-header">Ações</div>', unsafe_allow_html=True)
            if st.button("➕ Novo Cliente", use_container_width=True):
                st.session_state.show_client_form = True
                st.session_state.edit_client = None
        
        # Lista de clientes
        clients = session.query(Client).filter(
            Client.user_id == user.id,
            Client.is_active == True
        ).order_by(Client.name).all()
        
        if clients:
            st.subheader(f"📋 Clientes Cadastrados ({len(clients)})")
            
            for client in clients:
                with st.expander(f"👤 {client.name}"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**Email:** {client.email or 'Não informado'}")
                        st.write(f"**Telefone:** {client.phone or 'Não informado'}")
                    
                    with col2:
                        st.write(f"**Empresa:** {client.company or 'Não informado'}")
                        if client.address:
                            st.write(f"**Endereço:** {client.address}")
                    
                    with col3:
                        if st.button("✏️ Editar", key=f"edit_{client.id}"):
                            st.session_state.show_client_form = True
                            st.session_state.edit_client = client
                            st.rerun()
                    
                    if client.notes:
                        st.write(f"**Observações:** {client.notes}")
        else:
            st.info("Nenhum cliente cadastrado")
        
        # Formulário de cliente
        if st.session_state.get('show_client_form', False):
            edit_client = st.session_state.get('edit_client')
            
            st.subheader("✏️ Editar Cliente" if edit_client else "➕ Novo Cliente")
            
            with st.form("client_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Nome *", value=edit_client.name if edit_client else "")
                    email = st.text_input("Email", value=edit_client.email if edit_client else "")
                    phone = st.text_input("Telefone", value=edit_client.phone if edit_client else "")
                
                with col2:
                    company = st.text_input("Empresa", value=edit_client.company if edit_client else "")
                    address = st.text_area("Endereço", value=edit_client.address if edit_client else "")
                
                notes = st.text_area("Observações", value=edit_client.notes if edit_client else "")
                
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    submit = st.form_submit_button("💾 Salvar")
                
                with col2:
                    cancel = st.form_submit_button("❌ Cancelar")
                
                if submit:
                    if name.strip():
                        try:
                            if edit_client:
                                # Atualizar cliente existente
                                edit_client.name = name.strip()
                                edit_client.email = email.strip() or None
                                edit_client.phone = phone.strip() or None
                                edit_client.company = company.strip() or None
                                edit_client.address = address.strip() or None
                                edit_client.notes = notes.strip() or None
                            else:
                                # Criar novo cliente
                                client = Client(
                                    user_id=user.id,
                                    name=name.strip(),
                                    email=email.strip() or None,
                                    phone=phone.strip() or None,
                                    company=company.strip() or None,
                                    address=address.strip() or None,
                                    notes=notes.strip() or None
                                )
                                session.add(client)
                            
                            session.commit()
                            st.success("Cliente salvo com sucesso!")
                            st.session_state.show_client_form = False
                            st.session_state.edit_client = None
                            st.rerun()
                            
                        except Exception as e:
                            session.rollback()
                            st.error(f"Erro ao salvar cliente: {e}")
                    else:
                        st.error("O nome do cliente é obrigatório")
                
                if cancel:
                    st.session_state.show_client_form = False
                    st.session_state.edit_client = None
                    st.rerun()
    
    finally:
        session.close()

def projects_page():
    """Página de gestão de projetos"""
    st.markdown('<h1 class="main-header">📁 Gestão de Projetos</h1>', unsafe_allow_html=True)
    
    user = st.session_state.user
    session = st.session_state.db_manager.get_session()
    
    try:
        # Sidebar para ações
        with st.sidebar:
            st.markdown('<div class="sidebar-header">Ações</div>', unsafe_allow_html=True)
            if st.button("➕ Novo Projeto", use_container_width=True):
                st.session_state.show_project_form = True
                st.session_state.edit_project = None
        
        # Lista de projetos
        projects = session.query(Project).options(
            joinedload(Project.client)
        ).filter(
            Project.user_id == user.id
        ).order_by(Project.created_at.desc()).all()
        
        if projects:
            st.subheader(f"📋 Projetos ({len(projects)})")
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.selectbox(
                    "Filtrar por Status",
                    ["Todos", "Ativo", "Pausado", "Concluído", "Cancelado"]
                )
            
            # Aplicar filtro
            if status_filter != "Todos":
                status_map = {
                    "Ativo": ProjectStatus.ATIVO,
                    "Pausado": ProjectStatus.PAUSADO,
                    "Concluído": ProjectStatus.CONCLUIDO,
                    "Cancelado": ProjectStatus.CANCELADO
                }
                filtered_projects = [p for p in projects if p.status == status_map[status_filter]]
            else:
                filtered_projects = projects
            
            for project in filtered_projects:
                status_color = {
                    ProjectStatus.ATIVO: "🟢",
                    ProjectStatus.PAUSADO: "🟡",
                    ProjectStatus.CONCLUIDO: "🔵",
                    ProjectStatus.CANCELADO: "🔴"
                }.get(project.status, "⚪")
                
                with st.expander(f"{status_color} {project.name} - {project.client.name}"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**Status:** {project.status.value.title()}")
                        if project.start_date:
                            st.write(f"**Início:** {project.start_date.strftime('%d/%m/%Y')}")
                        if project.end_date:
                            st.write(f"**Fim:** {project.end_date.strftime('%d/%m/%Y')}")
                    
                    with col2:
                        if project.budget:
                            st.write(f"**Orçamento:** R$ {project.budget:,.2f}")
                        if project.hourly_rate:
                            st.write(f"**Valor/Hora:** R$ {project.hourly_rate:,.2f}")
                    
                    with col3:
                        if st.button("✏️ Editar", key=f"edit_proj_{project.id}"):
                            st.session_state.show_project_form = True
                            st.session_state.edit_project = project
                            st.rerun()
                    
                    if project.description:
                        st.write(f"**Descrição:** {project.description}")
        else:
            st.info("Nenhum projeto cadastrado")
        
        # Formulário de projeto (implementação básica)
        if st.session_state.get('show_project_form', False):
            st.subheader("➕ Novo Projeto")
            st.info("Formulário de projeto em desenvolvimento...")
            if st.button("❌ Cancelar"):
                st.session_state.show_project_form = False
                st.rerun()
    
    finally:
        session.close()

def finances_page():
    """Página de gestão financeira"""
    st.markdown('<h1 class="main-header">💰 Gestão Financeira</h1>', unsafe_allow_html=True)
    
    user = st.session_state.user
    session = st.session_state.db_manager.get_session()
    
    try:
        # Métricas financeiras
        col1, col2, col3, col4 = st.columns(4)
        
        # Receitas do mês
        current_month = datetime.now().replace(day=1)
        monthly_income = session.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.RECEITA,
            Transaction.date >= current_month
        ).with_entities(Transaction.amount).all()
        monthly_income_total = sum([t.amount for t in monthly_income]) if monthly_income else 0
        
        # Despesas do mês
        monthly_expenses = session.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.DESPESA,
            Transaction.date >= current_month
        ).with_entities(Transaction.amount).all()
        monthly_expenses_total = sum([t.amount for t in monthly_expenses]) if monthly_expenses else 0
        
        # Saldo do mês
        monthly_balance = monthly_income_total - monthly_expenses_total
        
        # Total geral
        all_income = session.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.RECEITA
        ).with_entities(Transaction.amount).all()
        total_income = sum([t.amount for t in all_income]) if all_income else 0
        
        with col1:
            st.metric("Receitas do Mês", f"R$ {monthly_income_total:,.2f}")
        
        with col2:
            st.metric("Despesas do Mês", f"R$ {monthly_expenses_total:,.2f}")
        
        with col3:
            delta_color = "normal" if monthly_balance >= 0 else "inverse"
            st.metric("Saldo do Mês", f"R$ {monthly_balance:,.2f}")
        
        with col4:
            st.metric("Total Receitas", f"R$ {total_income:,.2f}")
        
        st.divider()
        
        # Sidebar para ações
        with st.sidebar:
            st.markdown('<div class="sidebar-header">Ações</div>', unsafe_allow_html=True)
            if st.button("➕ Nova Transação", use_container_width=True):
                st.session_state.show_transaction_form = True
        
        # Lista de transações recentes
        st.subheader("💳 Transações Recentes")
        
        recent_transactions = session.query(Transaction).filter(
            Transaction.user_id == user.id
        ).order_by(Transaction.date.desc()).limit(20).all()
        
        if recent_transactions:
            for transaction in recent_transactions:
                type_icon = "💰" if transaction.type == TransactionType.RECEITA else "💸"
                type_color = "green" if transaction.type == TransactionType.RECEITA else "red"
                
                with st.expander(f"{type_icon} {transaction.description} - R$ {transaction.amount:,.2f}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Data:** {transaction.date.strftime('%d/%m/%Y')}")
                        st.write(f"**Tipo:** {transaction.type.value.title()}")
                    with col2:
                        st.write(f"**Valor:** R$ {transaction.amount:,.2f}")
                        if transaction.category:
                            st.write(f"**Categoria:** {transaction.category}")
        else:
            st.info("Nenhuma transação encontrada")
        
        # Formulário de transação (implementação básica)
        if st.session_state.get('show_transaction_form', False):
            st.subheader("➕ Nova Transação")
            st.info("Formulário de transação em desenvolvimento...")
            if st.button("❌ Cancelar"):
                st.session_state.show_transaction_form = False
                st.rerun()
    
    finally:
        session.close()

def timesheet_page():
    """Página de controle de tempo"""
    st.markdown('<h1 class="main-header">⏰ Controle de Tempo</h1>', unsafe_allow_html=True)
    
    user = st.session_state.user
    session = st.session_state.db_manager.get_session()
    
    try:
        # Métricas de tempo
        col1, col2, col3 = st.columns(3)
        
        # Horas hoje
        today = datetime.now().date()
        today_hours = session.query(TimeEntry).filter(
            TimeEntry.user_id == user.id,
            TimeEntry.date == today
        ).with_entities(TimeEntry.duration_minutes).all()
        today_hours_total = sum([t.duration_minutes/60 for t in today_hours]) if today_hours else 0
        
        # Horas esta semana
        week_start = today - timedelta(days=today.weekday())
        week_hours = session.query(TimeEntry).filter(
            TimeEntry.user_id == user.id,
            TimeEntry.date >= week_start
        ).with_entities(TimeEntry.duration_minutes).all()
        week_hours_total = sum([t.duration_minutes/60 for t in week_hours]) if week_hours else 0
        
        # Horas este mês
        month_start = today.replace(day=1)
        month_hours = session.query(TimeEntry).filter(
            TimeEntry.user_id == user.id,
            TimeEntry.date >= month_start
        ).with_entities(TimeEntry.duration_minutes).all()
        month_hours_total = sum([t.duration_minutes/60 for t in month_hours]) if month_hours else 0
        
        with col1:
            st.metric("Horas Hoje", f"{today_hours_total:.1f}h")
        
        with col2:
            st.metric("Horas na Semana", f"{week_hours_total:.1f}h")
        
        with col3:
            st.metric("Horas no Mês", f"{month_hours_total:.1f}h")
        
        st.divider()
        
        # Sidebar para ações
        with st.sidebar:
            st.markdown('<div class="sidebar-header">Ações</div>', unsafe_allow_html=True)
            if st.button("➕ Registrar Tempo", use_container_width=True):
                st.session_state.show_time_form = True
        
        # Lista de registros recentes
        st.subheader("📝 Registros Recentes")
        
        recent_entries = session.query(TimeEntry).options(
            joinedload(TimeEntry.project)
        ).filter(
            TimeEntry.user_id == user.id
        ).order_by(TimeEntry.date.desc()).limit(15).all()
        
        if recent_entries:
            for entry in recent_entries:
                project_name = entry.project.name if entry.project else "Sem projeto"
                with st.expander(f"⏱️ {entry.date.strftime('%d/%m/%Y')} - {project_name} - {entry.duration_minutes/60:.1f}h"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Projeto:** {project_name}")
                        st.write(f"**Horas:** {entry.duration_minutes/60:.1f}h")
                    with col2:
                        st.write(f"**Data:** {entry.date.strftime('%d/%m/%Y')}")
                    
                    if entry.description:
                        st.write(f"**Descrição:** {entry.description}")
        else:
            st.info("Nenhum registro de tempo encontrado")
        
        # Formulário de registro de tempo (implementação básica)
        if st.session_state.get('show_time_form', False):
            st.subheader("➕ Registrar Tempo")
            st.info("Formulário de registro de tempo em desenvolvimento...")
            if st.button("❌ Cancelar"):
                st.session_state.show_time_form = False
                st.rerun()
    
    finally:
        session.close()

def help_page():
    """Página de ajuda"""
    st.markdown('<h1 class="main-header">❓ Ajuda e Suporte</h1>', unsafe_allow_html=True)
    
    # Informações do sistema
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ℹ️ Informações do Sistema")
        st.write(f"**Versão:** {config.APP_VERSION}")
        st.write(f"**Aplicação:** {config.APP_NAME}")
        st.write("**Modo:** Streamlit Web")
        st.write("**Banco de Dados:** PostgreSQL (Neon)")
    
    with col2:
        st.subheader("🔗 Links Úteis")
        st.markdown("- [📖 Documentação](https://github.com/devflow)")
        st.markdown("- [🐛 Reportar Bug](https://github.com/devflow/issues)")
        st.markdown("- [💡 Sugestões](https://github.com/devflow/discussions)")
        st.markdown("- [📧 Contato](mailto:suporte@devflow.com)")
    
    st.divider()
    
    # Guia de uso
    st.subheader("📚 Guia de Uso")
    
    with st.expander("🏠 Dashboard"):
        st.write("""
        O Dashboard é sua central de controle, onde você pode:
        - Ver métricas principais (clientes, projetos, receitas, horas)
        - Acompanhar gráficos de receitas vs despesas
        - Monitorar horas trabalhadas
        - Visualizar projetos ativos
        """)
    
    with st.expander("👥 Gestão de Clientes"):
        st.write("""
        Na seção de Clientes você pode:
        - Cadastrar novos clientes
        - Editar informações de clientes existentes
        - Visualizar histórico de projetos por cliente
        - Gerenciar contatos e observações
        """)
    
    with st.expander("📁 Gestão de Projetos"):
        st.write("""
        No módulo de Projetos você pode:
        - Criar e gerenciar projetos
        - Definir orçamentos e prazos
        - Acompanhar status dos projetos
        - Vincular projetos a clientes
        """)
    
    with st.expander("💰 Controle Financeiro"):
        st.write("""
        Na área Financeira você pode:
        - Registrar receitas e despesas
        - Categorizar transações
        - Acompanhar fluxo de caixa
        - Gerar relatórios financeiros
        """)
    
    with st.expander("⏰ Controle de Tempo"):
        st.write("""
        No Timesheet você pode:
        - Registrar horas trabalhadas
        - Vincular tempo a projetos
        - Acompanhar produtividade
        - Gerar relatórios de tempo
        """)
    
    st.divider()
    
    # Atalhos de teclado
    st.subheader("⌨️ Atalhos e Dicas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Navegação:**")
        st.write("- Use a barra lateral para navegar")
        st.write("- Clique nos cards para expandir")
        st.write("- Use os filtros para encontrar dados")
    
    with col2:
        st.write("**Dicas:**")
        st.write("- Mantenha os dados sempre atualizados")
        st.write("- Use categorias para organizar")
        st.write("- Faça backup regular dos dados")
    
    st.divider()
    
    # Solução de problemas
    st.subheader("🔧 Solução de Problemas")
    
    with st.expander("❌ Erro de Conexão com Banco"):
        st.write("""
        Se você está enfrentando problemas de conexão:
        1. Verifique sua conexão com a internet
        2. Confirme se as credenciais do banco estão corretas
        3. Teste a conectividade com o servidor
        4. Entre em contato com o suporte se o problema persistir
        """)
    
    with st.expander("🐌 Performance Lenta"):
        st.write("""
        Para melhorar a performance:
        1. Feche outras abas do navegador
        2. Limpe o cache do navegador
        3. Verifique sua conexão com a internet
        4. Use filtros para reduzir a quantidade de dados
        """)
    
    with st.expander("📱 Problemas no Mobile"):
        st.write("""
        Para melhor experiência no mobile:
        1. Use o navegador em modo paisagem quando necessário
        2. Toque e segure para acessar menus contextuais
        3. Use zoom para visualizar detalhes
        4. Prefira a versão desktop para tarefas complexas
        """)
    
    st.divider()
    
    # Informações técnicas
    with st.expander("🔧 Informações Técnicas"):
        st.write(f"""
        **Tecnologias Utilizadas:**
        - Frontend: Streamlit {st.__version__}
        - Backend: Python {sys.version.split()[0]}
        - Banco de Dados: PostgreSQL (Neon)
        - Autenticação: bcrypt
        - Gráficos: Plotly
        
        **Compatibilidade:**
        - Navegadores: Chrome, Firefox, Safari, Edge
        - Dispositivos: Desktop, Tablet, Mobile
        - Sistemas: Windows, macOS, Linux
        """)

def main():
    """Função principal do Streamlit"""
    # Inicializa a aplicação
    init_app()
    
    # Verifica se o usuário está logado
    if 'user' not in st.session_state:
        login_page()
        return
    
    # Sidebar com navegação
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🚀 DevFlow</div>', unsafe_allow_html=True)
        user_name = getattr(st.session_state.user, 'full_name', st.session_state.get('user_name', 'Usuário'))
        st.write(f"Bem-vindo, **{user_name}**!")
        
        st.divider()
        
        # Menu de navegação
        page = st.selectbox(
            "Navegação",
            ["📊 Dashboard", "👥 Clientes", "📁 Projetos", "💰 Finanças", "⏰ Timesheet", "📊 Relatórios", "❓ Ajuda"]
        )
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            del st.session_state.user
            st.rerun()
    
    # Roteamento de páginas
    if page == "📊 Dashboard":
        dashboard_page()
    elif page == "👥 Clientes":
        clients_page()
    elif page == "📁 Projetos":
        projects_page()
    elif page == "💰 Finanças":
        finances_page()
    elif page == "⏰ Timesheet":
        timesheet_page()
    elif page == "📊 Relatórios":
        st.info("Página de Relatórios em desenvolvimento...")
    elif page == "❓ Ajuda":
        help_page()

if __name__ == "__main__":
    main()