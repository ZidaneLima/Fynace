# Fynace - Sistema de Finanças Pessoais

Fynace é um sistema de finanças pessoais que utiliza o Google Sheets como banco de dados pessoal de cada usuário e o Supabase para armazenar dados de usuários.

## Arquitetura

### Backend (FastAPI)
- Hospedado no Render
- Valida apenas tokens JWT (não autentica usuários)
- Integração com Google Sheets API via Service Account
- Conexão com Supabase para dados de usuários

### Banco de Dados (Supabase)
- Armazena IDs das planilhas do Google Sheets por usuário
- Gerencia autenticação de usuários (Google OAuth via Supabase)

### Frontend (Streamlit)
- Interface para gerenciamento de finanças
- Integração com o backend via API

## Autenticação

### Fluxo de Autenticação
1. Usuário se autentica via Google OAuth no Supabase
2. Supabase gera JWT token
3. Backend apenas valida o JWT token (RS256 / JWKS)
4. Backend acessa Google Sheets via Service Account
5. Cada usuário tem sua própria planilha no Google Sheets

### Componentes de Autenticação
- **Supabase Auth**: Gerencia autenticação de usuários via Google OAuth
- **JWT Validation**: Backend valida tokens JWT usando RS256 e JWKS
- **Google Sheets API**: Acesso via Service Account (não por usuário)

## Configuração

### Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure as variáveis:

```bash
cp .env.example .env
```

### Supabase

1. Crie um projeto no [Supabase](https://supabase.com)
2. Configure o Google OAuth no painel do Supabase
3. Adicione as credenciais no arquivo `.env`

### Google API (Service Account)

1. Crie um projeto no [Google Cloud Console](https://console.cloud.google.com)
2. Ative a API do Google Sheets
3. Crie uma Service Account
4. Baixe o arquivo JSON da chave da Service Account
5. Configure a variável `GOOGLE_SERVICE_ACCOUNT_FILE` no `.env`

### Banco de Dados

Execute o script SQL em `database_schema.sql` no seu projeto Supabase para criar as tabelas necessárias.

## Execução

### Backend

```bash
cd /path/to/Fynace
uv venv
source .venv/bin/activate  # ou o equivalente no seu sistema
uv pip install -r pyproject.toml
uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd /path/to/Fynace
streamlit run frontend/app.py
```

## Estrutura do Projeto

```
Fynace/
├── backend/                 # API REST com FastAPI
│   ├── auth_utils.py        # Validação de JWT
│   ├── config.py            # Configurações
│   ├── main.py              # Aplicação principal
│   ├── routes/              # Rotas da API
│   ├── services/            # Lógica de negócio
│   ├── models/              # Modelos de dados
│   ├── database/            # Serviço de banco de dados
│   └── utils/               # Utilitários
├── frontend/                # Interface Streamlit
│   ├── app.py               # Aplicação principal
│   ├── utils/               # Utilitários
│   └── components/          # Componentes reutilizáveis
├── credentials/             # Credenciais do Google
├── database_schema.sql      # Esquema do banco de dados
└── .env.example             # Exemplo de variáveis de ambiente
```

## Segurança

- Validação de entrada de dados
- Sanitização de dados sensíveis
- Cabeçalhos de segurança HTTP
- Criptografia de dados sensíveis
- Controle de acesso baseado em JWT
- Service Account para acesso ao Google Sheets (não credenciais de usuário)

## Escalabilidade

- Arquitetura baseada em serviços
- Separação clara de responsabilidades
- Banco de dados centralizado no Supabase
- Backend stateless
- Integração com serviços externos (Google Sheets via Service Account)