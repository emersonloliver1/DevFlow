# DevFlow - Gestão Completa para Freelancers

## 📋 Descrição

DevFlow é uma aplicação desktop desenvolvida em Python para freelancers de programação. Oferece uma solução completa para gerenciamento de clientes, projetos, finanças, controle de tempo e geração de relatórios.

## ✨ Funcionalidades

### 🔐 Autenticação
- Sistema de login seguro com JWT
- Criptografia de senhas com bcrypt
- Suporte a múltiplos usuários

### 👥 Gestão de Clientes
- CRUD completo de clientes
- Informações de contato
- Histórico de projetos por cliente

### 📁 Gestão de Projetos
- CRUD completo de projetos
- Associação com clientes
- Controle de orçamento e status
- Datas de início e fim

### 💰 Gestão Financeira
- Controle de receitas e despesas
- Transações por projeto
- Relatórios financeiros
- Cálculo de saldo e lucro

### ⏰ Controle de Tempo
- Timer integrado para registro de atividades
- Histórico de horas trabalhadas
- Associação de tempo por projeto
- Estatísticas de produtividade

### 📊 Relatórios e Faturas
- Relatórios de projeto
- Relatórios financeiros
- Relatórios de horas trabalhadas
- Geração de faturas em PDF
- Resumos gerais

### 📈 Dashboard
- Visão geral das finanças
- Estatísticas de tempo
- Projetos ativos
- Atividades recentes

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **CustomTkinter** - Interface gráfica moderna
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL** - Banco de dados (Neon)
- **Alembic** - Migrações de banco
- **bcrypt** - Criptografia de senhas
- **PyJWT** - Autenticação JWT
- **ReportLab** - Geração de PDFs
- **python-dotenv** - Gerenciamento de variáveis de ambiente

## 📦 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Conta no Neon (PostgreSQL Serverless)

### Passos

1. **Clone ou baixe o projeto**
   ```bash
   cd DevFlow
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente**
   
   Edite o arquivo `.env` na raiz do projeto:
   ```env
   DATABASE_URL=postgresql://usuario:senha@host:porta/database
   SECRET_KEY=sua_chave_secreta_muito_segura_aqui
   ```

4. **Execute as migrações do banco**
   ```bash
   alembic upgrade head
   ```

5. **Execute a aplicação**
   ```bash
   python main.py
   ```

## 🚀 Uso

### Primeiro Acesso
1. Execute a aplicação
2. Na tela de login, clique em "Registrar"
3. Crie sua conta com email e senha
4. Faça login com suas credenciais

### Fluxo de Trabalho Recomendado
1. **Cadastre seus clientes** na aba "Clientes"
2. **Crie projetos** associados aos clientes na aba "Projetos"
3. **Registre transações** financeiras na aba "Finanças"
4. **Controle seu tempo** na aba "Timesheet"
5. **Gere relatórios** na aba "Relatórios"
6. **Acompanhe o progresso** no "Dashboard"

## 📁 Estrutura do Projeto

```
DevFlow/
├── src/
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth_manager.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── models.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── login_window.py
│   │   ├── dashboard.py
│   │   ├── clients_frame.py
│   │   ├── projects_frame.py
│   │   ├── finances_frame.py
│   │   ├── timesheet_frame.py
│   │   └── reports_frame.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py
│   └── __init__.py
├── migrations/
│   ├── env.py
│   └── script.py.mako
├── logs/
├── reports/
├── uploads/
├── .env
├── alembic.ini
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
# Banco de Dados
DATABASE_URL=postgresql://usuario:senha@host:porta/database

# Autenticação
SECRET_KEY=sua_chave_secreta_muito_segura_aqui
```

### Configurações da Aplicação (config.py)

O arquivo `config.py` contém todas as configurações da aplicação:
- Dimensões da janela
- Tema da interface
- Configurações de upload
- Configurações JWT
- Pastas de arquivos

## 🔧 Desenvolvimento

### Executando em Modo de Desenvolvimento

```bash
# Ativar logs detalhados
export LOG_LEVEL=DEBUG
python main.py
```

### Criando Migrações

```bash
# Gerar nova migração
alembic revision --autogenerate -m "Descrição da mudança"

# Aplicar migrações
alembic upgrade head

# Reverter migração
alembic downgrade -1
```

### Estrutura de Logs

Os logs são salvos na pasta `logs/` com rotação automática:
- `devflow.log` - Log principal
- Logs são rotacionados quando atingem 10MB
- Mantém até 5 arquivos de backup

## 📊 Funcionalidades Detalhadas

### Dashboard
- **Estatísticas Financeiras**: Receitas, despesas, saldo
- **Controle de Tempo**: Horas trabalhadas no mês
- **Projetos Ativos**: Lista dos projetos em andamento
- **Atividades Recentes**: Últimas transações e registros de tempo

### Gestão de Clientes
- Nome, email, telefone
- Endereço completo
- Observações
- Histórico de projetos

### Gestão de Projetos
- Nome e descrição
- Cliente associado
- Orçamento total
- Status (Proposta, Ativo, Concluído, Cancelado)
- Datas de início e fim

### Controle Financeiro
- **Receitas**: Pagamentos recebidos
- **Despesas**: Custos do projeto ou gerais
- **Filtros**: Por projeto, tipo, período
- **Estatísticas**: Totais, saldos, médias

### Timesheet
- **Timer**: Cronômetro integrado
- **Registros Manuais**: Adicionar horas trabalhadas
- **Filtros**: Por projeto, data
- **Estatísticas**: Horas diárias, semanais, mensais

### Relatórios
- **Relatório de Projeto**: Detalhes completos de um projeto
- **Relatório Financeiro**: Receitas e despesas por período
- **Relatório de Horas**: Controle de tempo trabalhado
- **Faturas**: Documentos para cobrança
- **Resumo Geral**: Visão geral de todos os dados
- **Exportação PDF**: Todos os relatórios podem ser exportados

## 🔒 Segurança

- **Senhas**: Criptografadas com bcrypt
- **Autenticação**: JWT com expiração configurável
- **Banco de Dados**: Conexão segura via SSL
- **Logs**: Não registram informações sensíveis

## 🐛 Solução de Problemas

### Erro de Conexão com Banco
1. Verifique a `DATABASE_URL` no arquivo `.env`
2. Confirme se o banco está acessível
3. Execute `alembic upgrade head` para aplicar migrações

### Erro de Dependências
1. Atualize o pip: `pip install --upgrade pip`
2. Reinstale as dependências: `pip install -r requirements.txt`

### Interface não Carrega
1. Verifique se o CustomTkinter está instalado
2. Confirme a versão do Python (3.8+)
3. Verifique os logs em `logs/devflow.log`

### PDF não Gera
1. Instale o ReportLab: `pip install reportlab`
2. Verifique permissões da pasta `reports/`

## 📝 Licença

Este projeto é de uso pessoal e educacional.

## 🤝 Contribuição

Para contribuir com o projeto:
1. Faça um fork
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs em `logs/devflow.log`
2. Consulte a documentação
3. Abra uma issue no repositório

---

**DevFlow** - Sua central de gestão completa para freelancers! 🚀
