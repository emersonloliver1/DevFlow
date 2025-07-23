Plano de Projeto: DevFlow (Escopo Expandido)
Visão do Produto: Criar uma aplicação desktop para Windows, chamada DevFlow, que serve como uma central de gestão completa para freelancers de programação. A aplicação permitirá o gerenciamento de clientes, projetos, finanças (recebíveis e despesas), controle de tempo e geração de relatórios. Utilizará Python com CustomTkinter para a interface e NeonDB para armazenamento de dados na nuvem, com capacidade de sincronização de arquivos.

1. Escopo do Projeto (Versão Completa)
O objetivo é construir uma solução robusta que abranja todo o ciclo de vida de um projeto freelancer.

Funcionalidades Essenciais (Dentro do Escopo):
Gestão de Usuários e Autenticação:

Sistema de login para múltiplos perfis de usuário. Cada dado na aplicação (cliente, projeto, etc.) será vinculado a um usuário.

Módulo de Clientes:

Funcionalidade completa para Criar, Visualizar, Atualizar e Deletar (CRUD) clientes.

Módulo de Projetos:

CRUD completo para projetos, associados a um cliente.

Campos para "Orçamento Total" e "Status" (Ex: Proposta, Ativo, Concluído).

Gestão Financeira Completa:

Transações (Recebimentos): Lançamento de múltiplos pagamentos recebidos por projeto.

Controle de Despesas: Lançamento de custos e despesas que podem ser associados a projetos específicos (ex: compra de um plugin) ou gerais (ex: assinatura de software).

Controle de Tempo (Timesheet):

Funcionalidade para registrar horas trabalhadas.

Cada entrada de tempo pode ser associada a um projeto específico.

O sistema poderá calcular o total de horas gastas por projeto.

Gestão de Arquivos na Nuvem:

Sincronização de Contratos: Funcionalidade para fazer o upload de arquivos de contrato, que serão armazenados de forma segura na nuvem e vinculados ao projeto correspondente.

Relatórios e Faturas:

Geração de Relatórios em PDF: Capacidade de gerar relatórios simples por projeto, mostrando o orçamento, recebimentos, despesas e horas trabalhadas.

Geração de Faturas em PDF: Criação de faturas (invoices) básicas a partir dos dados de um projeto para enviar ao cliente.

Dashboard (Tela Principal):

Exibirá indicadores chave: "Valor a Receber", "Lucro por Projeto", "Total Recebido (mês)", "Total de Despesas (mês)" e "Horas Trabalhadas (mês)".

2. PRD (Documento de Requisitos do Produto)
Estrutura de Dados (Modelo do Banco de Dados NeonDB):
Tabela: users

id (SERIAL, PRIMARY KEY)

username (VARCHAR(100), UNIQUE, NOT NULL)

password_hash (VARCHAR(255), NOT NULL)

Tabela: clients

id (SERIAL, PRIMARY KEY)

user_id (INTEGER, FOREIGN KEY references users(id))

name (VARCHAR(255), NOT NULL)

contact_info (TEXT)

Tabela: projects

id (SERIAL, PRIMARY KEY)

user_id (INTEGER, FOREIGN KEY references users(id))

client_id (INTEGER, FOREIGN KEY references clients(id))

name (VARCHAR(255), NOT NULL)

total_budget (DECIMAL(10, 2), NOT NULL)

status (VARCHAR(50), default 'Ativo')

contract_url (TEXT) -> URL do arquivo na nuvem

Tabela: transactions (Recebimentos)

id (SERIAL, PRIMARY KEY)

project_id (INTEGER, FOREIGN KEY references projects(id))

amount_received (DECIMAL(10, 2), NOT NULL)

date_received (DATE, NOT NULL)

Tabela: expenses (Despesas)

id (SERIAL, PRIMARY KEY)

user_id (INTEGER, FOREIGN KEY references users(id))

project_id (INTEGER, FOREIGN KEY references projects(id), NULLABLE) -> Pode ser associada a um projeto ou não

description (VARCHAR(255), NOT NULL)

amount (DECIMAL(10, 2), NOT NULL)

expense_date (DATE, NOT NULL)

Tabela: time_entries (Controle de Tempo)

id (SERIAL, PRIMARY KEY)

project_id (INTEGER, FOREIGN KEY references projects(id))

hours_worked (DECIMAL(5, 2), NOT NULL)

work_date (DATE, NOT NULL)

description (TEXT)

3. Cronograma de Desenvolvimento Detalhado (Estimativa: 8 Semanas)
Fase 1: Fundação e Backend Core (Semanas 1-2)
Objetivo: Configurar a base técnica e a estrutura de dados principal.

Etapas:

Setup do Ambiente e NeonDB: Configurar ambiente, bibliotecas e banco de dados.

Módulo de Usuários: Implementar a lógica de criação e login de usuários (incluindo hashing de senhas).

Backend CRUD Inicial: Desenvolver no database.py as funções CRUD para Clients e Projects, já incluindo a lógica de user_id em todas as queries para garantir que um usuário só veja seus próprios dados.

Interface Gráfica Base: Criar a janela principal, a tela de login e a navegação básica.

Fase 2: Gestão Financeira (Semanas 3-4)
Objetivo: Construir o núcleo do controle financeiro.

Etapas:

Backend Financeiro: Implementar funções CRUD para Transactions (recebimentos) e Expenses (despesas).

Interface de Transações: Na tela de detalhes do projeto, criar a UI para listar e adicionar recebimentos.

Módulo de Despesas: Criar uma nova tela dedicada para o usuário listar, adicionar e editar despesas (associadas ou não a projetos).

Cálculos de Lucratividade: Implementar a lógica que calcula o lucro de um projeto (Total Recebido - Despesas do Projeto).

Fase 3: Produtividade e Dashboard (Semanas 5-6)
Objetivo: Adicionar o controle de tempo e consolidar os dados na tela principal.

Etapas:

Backend do Timesheet: Implementar funções CRUD para time_entries.

Interface do Timesheet: Na tela de detalhes do projeto, adicionar uma aba ou seção para listar e adicionar horas trabalhadas.

Desenvolvimento do Dashboard: Criar a tela principal com todos os widgets definidos, buscando os dados agregados do banco de dados (total a receber, lucro, despesas, horas).

Conexão dos Dados: Ligar todas as funções do backend aos elementos visuais do dashboard.

Fase 4: Relatórios e Arquivos (Semana 7)
Objetivo: Implementar as funcionalidades de exportação e gestão de arquivos.

Etapas:

Integração com Cloud Storage: Configurar um serviço de armazenamento (ex: AWS S3, Google Cloud Storage) e implementar no backend as funções para upload e download de arquivos.

Upload de Contrato: Conectar a função de upload ao formulário de projeto.

Gerador de PDF: Integrar uma biblioteca como FPDF2 ou ReportLab.

Implementação de Relatórios: Criar a lógica para buscar os dados de um projeto e formatá-los em uma fatura ou relatório em PDF.

Fase 5: Refinamento e Empacotamento (Semana 8)
Objetivo: Polir, testar exaustivamente e preparar a aplicação para distribuição.

Etapas:

Testes de Integração: Realizar um teste completo de ponta a ponta, simulando o fluxo de trabalho de um freelancer.

Tratamento de Erros e UX: Adicionar feedback visual para o usuário (mensagens de sucesso, erro, carregamento) e refinar a interface.

Empacotamento com PyInstaller: Gerar o arquivo .exe final.

Criação do README: Documentar o processo de instalação e configuração, especialmente como lidar com as chaves de API para o NeonDB e o serviço de Cloud Storage.