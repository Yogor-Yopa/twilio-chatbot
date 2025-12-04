# 🔒 CryptoLock Chatbot - Documentação Completa

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Instalação](#instalação)
4. [Configuração](#configuração)
5. [Como Usar](#como-usar)
6. [API Endpoints](#api-endpoints)
7. [Estrutura do Projeto](#estrutura-do-projeto)
8. [Variáveis de Ambiente](#variáveis-de-ambiente)
9. [Troubleshooting](#troubleshooting)
10. [Recursos Adicionais](#recursos-adicionais)

---

## 🎯 Visão Geral

**CryptoLock Chatbot** é uma aplicação de chatbot inteligente integrada com:

- **WhatsApp** via [Twilio Programmable Messaging](https://www.twilio.com/whatsapp)
- **IA Generativa** com [Google Gemini 2.5 Flash](https://ai.google.dev/)
- **API REST** construída com [FastAPI](https://fastapi.tiangolo.com/)
- **Atendimento Comercial** para venda do produto PSPM (Pipeline Security Posture Management)

### ✨ Funcionalidades Principais

- ✅ Recebimento de mensagens WhatsApp em tempo real
- ✅ Processamento inteligente com IA Gemini
- ✅ Detecção automática de idioma (Português/Inglês)
- ✅ Gerenciamento de sessões de chat por usuário
- ✅ Respostas contextualizadas e comerciais
- ✅ Logging detalhado de operações
- ✅ Escalabilidade horizontal

---

## 🏗️ Arquitetura

### Fluxo de Mensagens

```
WhatsApp User
    ↓
Twilio Webhook (FormData)
    ↓
FastAPI POST /webhook
    ↓
webhook_handler.process_webhook()
    ↓
Chat Session Manager
    ↓
Google Gemini AI
    ↓
Twilio Service (send_text_message)
    ↓
WhatsApp Response
```

### Componentes Principais

| Componente | Responsabilidade | Arquivo |
|-----------|-----------------|---------|
| **FastAPI App** | Orquestração de rotas e webhooks | `app.py` |
| **Webhook Handler** | Parsing e validação de dados Twilio | `handlers/webhook_handler.py` |
| **Twilio Service** | Integração com API Twilio | `services/twilio_service.py` |
| **Gemini Client** | Integração com IA Google Gemini | `services/gemini_client.py` |
| **Config** | Gerenciamento de variáveis de ambiente | `config.py` |
| **Models** | Definição de estruturas de dados | `models.py` |

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.11+**
- **pip** ou **poetry**
- **Conta Twilio** com sandbox WhatsApp ativo
- **API Key Google Gemini**

### Passo 1: Clonar o Repositório

```bash
git clone https://github.com/Yogor-Yopa/cryptolock-chatbot.git
cd cryptolock-project-repo/cryptolock-chatbot
```

### Passo 2: Criar Virtual Environment

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

**Pacotes instalados:**
- `fastapi==0.104.1` - Framework web
- `uvicorn[standard]==0.24.0` - Servidor ASGI
- `pydantic==2.5.0` - Validação de dados
- `python-dotenv==1.0.0` - Gerenciamento de .env
- `python-multipart==0.0.6` - Parsing de FormData
- `pyyaml==6.0.1` - Carregamento de prompts YAML
- `google-genai==0.1.0` - Cliente Gemini AI
- `twilio==8.10.0` - Cliente Twilio

---

## ⚙️ Configuração

### Passo 1: Criar Arquivo .env

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

### Passo 2: Obter Credenciais Twilio

1. Acesse [Twilio Console](https://www.twilio.com/console)
2. Copie o **Account SID** e **Auth Token**
3. Vá para **Messaging → Try it out → WhatsApp Sandbox**
4. Obtenha o número WhatsApp do Twilio (ex: +14155238886)

### Passo 3: Obter API Key Google Gemini

1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Crie uma nova API Key
3. Copie e salve em local seguro

### Passo 4: Preencher .env

```env
# Insira seus dados de acordo com o .env.example
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=seu_token_aqui
TWILIO_WHATSAPP_NUMBER=+14155552671
GEMINI_API_KEY=sua_chave_aqui
VERIFY_TOKEN=seu_token_qualquer
```

⚠️ **IMPORTANTE:** Nunca commit o `.env` no Git! Está no `.gitignore`.

---

## 🎮 Como Usar

### 1. Iniciar o Servidor

```bash
# Modo desenvolvimento com reload automático
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Modo produção
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --log-level info
```

### 2. Verificar Status

```bash
# Health check
curl http://localhost:8000/health

# Status detalhado
curl http://localhost:8000/status

# Documentação interativa
http://localhost:8000/docs
```

### 3. Configurar Webhook no Twilio

1. Vá para **Twilio Console → Messaging → WhatsApp → Sandbox**
2. Em **When a message comes in**, coloque:
   ```
   https://seu-dominio.com/webhook
   ```
3. Método: **POST**
4. Salve as mudanças

### 4. Testar com WhatsApp

1. Adicione o número WhatsApp do Twilio nos seus contatos
2. Envie uma mensagem de teste
3. O chatbot responderá automaticamente

---

## 📡 API Endpoints

### GET `/`
**Descrição:** Retorna informações da API

**Resposta:**
```json
{
  "message": "CryptoLock Chatbot API - Twilio WhatsApp Integration",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {...},
  "technology": {...}
}
```

### GET `/health`
**Descrição:** Health check rápido

**Resposta:**
```json
{
  "status": "ok"
}
```

### GET `/status`
**Descrição:** Status detalhado de todos os serviços

**Resposta:**
```json
{
  "status": "operational",
  "services": {
    "twilio": "connected",
    "gemini": "connected",
    "sessions": 5
  }
}
```

### GET `/webhook`
**Descrição:** Verificação de webhook do Twilio

**Query Parameters:**
- `hub.verify_token` - Token de verificação
- `hub.challenge` - Challenge para validação

### POST `/webhook`
**Descrição:** Recebe mensagens do WhatsApp

**Content-Type:** `application/x-www-form-urlencoded` (FormData)

**Campos esperados:**
```
MessageSid      - ID único da mensagem
From            - Número do remetente (whatsapp:+XXX)
To              - Número de destino (whatsapp:+XXX)
Body            - Corpo da mensagem
NumMedia        - Número de mídias anexadas
MessageType     - Tipo (text, media)
Timestamp       - Timestamp da mensagem
```

**Resposta (Sucesso):**
```json
{
  "status": "success",
  "message": "Mensagem processada"
}
```

**Resposta (Erro):**
```json
{
  "status": "error",
  "message": "Descrição do erro"
}
```

---

## 📁 Estrutura do Projeto

```
cryptolock-chatbot/
├── .venv/                          # Virtual environment (ignorado)
├── .gitignore                      # Configuração Git
├── __init__.py
├── __pycache__/                    # Cache Python (ignorado)
├── app.py                          # Aplicação FastAPI principal
├── config.py                       # Configurações e variáveis de ambiente
├── models.py                       # Modelos Pydantic
├── requirements.txt                # Dependências Python
├── .env                           # Variáveis de ambiente (IGNORADO)
├── .env.example                   # Exemplo de .env
│
├── docs/
│   ├── README.md                  # Este arquivo
│   ├── doc.md                     # Documentação técnica
│   └── QUICKSTART_TWILIO.md       # Guia rápido Twilio
│
├── handlers/
│   ├── __init__.py
│   └── webhook_handler.py         # Processamento de webhooks Twilio
│
├── services/
│   ├── __init__.py
│   ├── gemini_client.py          # Integração Google Gemini
│   ├── twilio_service.py         # Integração Twilio
│   └── meta_api.py               # Código legado (Meta API)
│
├── prompts/
│   └── cryptolock_atendente_v1.yaml  # Prompt do atendente
│
├── utils/
│   └── __init__.py
│
└── tests/
    └── __init__.py
```

---

## 🔐 Variáveis de Ambiente

### Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `TWILIO_ACCOUNT_SID` | Account ID do Twilio | 
| `TWILIO_AUTH_TOKEN` | Token de autenticação Twilio | 
| `TWILIO_WHATSAPP_NUMBER` | Número WhatsApp do Twilio | 
| `GEMINI_API_KEY` | API Key Google Gemini | 
| `VERIFY_TOKEN` | Token para verificação de webhook |

### Opcionais

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DEBUG` | Ativa modo debug | `False` |
| `GEMINI_MODEL` | Modelo Gemini a usar | `gemini-2.5-flash` |
| `LOG_LEVEL` | Nível de logging | `INFO` |

---

## 🐛 Troubleshooting

### Erro: "The `python-multipart` library must be installed"

**Solução:**
```bash
pip install python-multipart
```

### Erro: "No module named 'google'"

**Solução:**
```bash
pip install google-genai
```

### Webhook retorna 403 Forbidden

**Causa:** Token de verificação inválido ou ausente

**Solução:**
1. Verifique `VERIFY_TOKEN` no `.env`
2. Confira se o token está correto no Twilio Console
3. Reinicie o servidor

### Mensagens não chegam ao WhatsApp

**Checklist:**
- ✅ Twilio Account SID está correto?
- ✅ Twilio Auth Token está correto?
- ✅ Número WhatsApp está correto?
- ✅ Número está formatado com `+` e código país?
- ✅ Sandbox do WhatsApp está ativo?
- ✅ Número do usuário foi adicionado ao sandbox?

### Gemini retorna erro "quota exceeded"

**Solução:** 
Você atingiu o limite da API Key. Aguarde o reset diário ou upgrade o plano.

### Porta 8000 já em uso

**Solução:**
```bash
# Windows
netstat -ano | Select-String "8000"
Stop-Process -Id <PID> -Force

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```

---

## 🔄 Fluxo de Uma Mensagem

1. **Usuário envia mensagem** via WhatsApp
2. **Twilio recebe** e faz POST para `/webhook`
3. **webhook_handler.process_webhook()** extrai dados:
   - `From` → ID do usuário
   - `Body` → Conteúdo da mensagem
   - `MessageSid` → ID único
4. **ChatSessionManager** obtém/cria sessão
5. **Gemini** recebe mensagem e retorna resposta
6. **TwilioWhatsAppClient** envia resposta para usuário
7. **Logs** registram toda a operação

---

## 📊 Monitoramento

### Visualizar Logs em Tempo Real

```bash
# Windows
Get-Content -Path "logs\app.log" -Tail 100 -Wait

# Linux/macOS
tail -f logs/app.log
```

### Endpoints de Debug

```bash
# Ver status geral
curl http://localhost:8000/status

# Ver documentação interativa
curl http://localhost:8000/docs

# Health check
curl http://localhost:8000/health
```

---

## 🚀 Deploy em Produção

### Opção 1: Heroku

```bash
# Instalar Heroku CLI
# Fazer login
heroku login

# Criar app
heroku create cryptolock-chatbot

# Deploy
git push heroku main

# Ver logs
heroku logs --tail
```

### Opção 2: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t cryptolock-chatbot .
docker run -p 8000:8000 --env-file .env cryptolock-chatbot
```

### Opção 3: AWS Lambda

Use `mangum` para adaptar FastAPI para Lambda:

```bash
pip install mangum
```

---

## 📚 Recursos Adicionais

### Documentação Oficial
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [Google Gemini AI](https://ai.google.dev/docs)
- [Pydantic Docs](https://docs.pydantic.dev/)

### Arquivos de Documentação
- [`doc.md`](doc.md) - Documentação técnica detalhada
- [`QUICKSTART_TWILIO.md`](QUICKSTART_TWILIO.md) - Guia rápido Twilio

### Contatos e Suporte
- **Repositório:** [cryptolock-project-repo](https://github.com/Yogor-Yopa/cryptolock-chatbot)
- **Dúvidas:** Crie uma Issue no GitHub

---

## 📝 Changelog

### v1.0.0 (2025-12-04)
- ✅ Integração com Twilio
- ✅ Integração com Google Gemini 2.5 Flash
- ✅ Prompt comercial CryptoLock YAML
- ✅ Gerenciamento de sessões de chat
- ✅ Logging detalhado
- ✅ Documentação completa

