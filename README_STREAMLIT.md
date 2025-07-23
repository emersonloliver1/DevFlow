# DevFlow - Versão Web com Streamlit

## 🚀 Visão Geral

O DevFlow agora oferece duas formas de execução:
- **🖥️ Desktop**: Interface nativa com CustomTkinter (versão original)
- **🌐 Web**: Interface web com Streamlit (nova versão)

Ambas as versões compartilham a mesma base de dados e lógica de negócio, permitindo usar qualquer uma conforme sua preferência.

## 📦 Instalação

### Opção 1: Instalação Automática (Recomendada)
```bash
python run_devflow.py --install
```

### Opção 2: Instalação Manual

**Para versão Desktop:**
```bash
pip install -r requirements.txt
```

**Para versão Web:**
```bash
pip install -r requirements_streamlit.txt
```

## 🎯 Como Executar

### Launcher Interativo (Recomendado)
```bash
python run_devflow.py
```
Este comando abre um menu interativo onde você pode escolher qual versão executar.

### Execução Direta

**Versão Desktop:**
```bash
python run_devflow.py --desktop
# ou
python main.py
```

**Versão Web:**
```bash
python run_devflow.py --web
# ou
python -m streamlit run streamlit_app.py
```

## 🌐 Versão Web - Características

### ✅ Funcionalidades Implementadas
- 🔐 **Sistema de Autenticação**: Login e registro de usuários
- 📊 **Dashboard**: Métricas principais e gráficos interativos
- 👥 **Gestão de Clientes**: CRUD completo de clientes
- 📱 **Interface Responsiva**: Funciona em desktop, tablet e mobile
- 🎨 **Design Moderno**: Interface limpa e intuitiva

### 🚧 Em Desenvolvimento
- 📁 Gestão de Projetos
- 💰 Controle Financeiro
- ⏰ Timesheet
- 📊 Relatórios Avançados

### 🔗 Acesso
Após iniciar a versão web, acesse:
- **Local**: http://localhost:8501
- **Rede**: http://[seu-ip]:8501

## 🖥️ Versão Desktop vs 🌐 Versão Web

| Característica | Desktop | Web |
|---|---|---|
| **Interface** | CustomTkinter nativo | Streamlit web |
| **Acesso** | Apenas local | Local + Rede |
| **Responsividade** | Fixa | Responsiva |
| **Colaboração** | Individual | Multi-usuário |
| **Instalação** | Mais dependências | Mais leve |
| **Performance** | Mais rápida | Boa |
| **Mobile** | Não | Sim |

## 🗄️ Banco de Dados

Ambas as versões utilizam o mesmo banco de dados PostgreSQL (Neon), garantindo:
- ✅ Sincronização automática entre versões
- ✅ Backup na nuvem
- ✅ Acesso de qualquer lugar
- ✅ Escalabilidade

## 🔧 Configuração

As configurações são compartilhadas entre as versões através do arquivo `.env`:

```env
DATABASE_URL=postgresql://usuario:senha@host:porta/database
SECRET_KEY=sua_chave_secreta_aqui
```

## 🚀 Deploy (Futuro)

A versão web está preparada para deploy em:
- **Streamlit Cloud**: Deploy gratuito e automático
- **Heroku**: Plataforma robusta
- **Railway**: Deploy simples
- **AWS/GCP/Azure**: Máxima flexibilidade

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
DevFlow/
├── main.py                 # Launcher desktop
├── streamlit_app.py        # Aplicação Streamlit
├── run_devflow.py         # Launcher universal
├── requirements.txt        # Deps desktop
├── requirements_streamlit.txt  # Deps web
├── src/                   # Código compartilhado
│   ├── database/         # Modelos e conexão
│   ├── auth/            # Autenticação
│   └── utils/           # Utilitários
└── gui/                  # Interface desktop
```

### Adicionando Funcionalidades

1. **Lógica de Negócio**: Adicione em `src/`
2. **Interface Desktop**: Modifique arquivos em `gui/`
3. **Interface Web**: Edite `streamlit_app.py`

## 🐛 Solução de Problemas

### Erro: "streamlit não encontrado"
```bash
pip install streamlit
# ou
python run_devflow.py --install
```

### Erro: "customtkinter não encontrado"
```bash
pip install customtkinter
# ou
python run_devflow.py --install
```

### Erro de Conexão com Banco
1. Verifique o arquivo `.env`
2. Confirme se o DATABASE_URL está correto
3. Teste a conexão de rede

### Porta 8501 em Uso
```bash
# Matar processo na porta
netstat -ano | findstr :8501
taskkill /PID [PID_NUMBER] /F
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique este README
2. Execute `python run_devflow.py --install`
3. Teste ambas as versões
4. Reporte bugs com logs detalhados

## 🎉 Próximos Passos

1. **Teste ambas as versões** para escolher sua preferida
2. **Configure o banco de dados** se ainda não fez
3. **Importe seus dados** se migrar de outro sistema
4. **Explore as funcionalidades** disponíveis
5. **Aguarde atualizações** com novas features

---

**DevFlow** - Gestão Completa para Freelancers 🚀