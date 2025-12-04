# Documentação Técnica - CryptoLock Chatbot

## 📋 Índice
1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Integração Twilio](#integração-twilio)
4. [Arquitetura Detalhada](#arquitetura-detalhada)
5. [Componentes do Sistema](#componentes-do-sistema)
6. [Fluxo de Dados](#fluxo-de-dados)
7. [Integração Gemini](#integração-gemini)
8. [Integração Twilio](#integração-twilio)
9. [Gerenciamento de Sessões](#gerenciamento-de-sessões)
10. [Segurança](#segurança)
11. [Performance](#performance)
12. [Próximos Passos](#próximos-passos)

---

## 🎯 Visão Geral do Projeto

**CryptoLock Chatbot** é uma plataforma de atendimento comercial automático via WhatsApp que:

- Recebe mensagens de clientes através do Twilio
- Processa inteligência artificial com Google Gemini 2.5 Flash
- Fornece respostas contextualizadas e comerciais sobre o produto PSPM
- Gerencia sessões de chat independentes por usuário
- Registra todas as interações com logging detalhado

### Características Principais
- ✅ **Atendimento 24/7** via WhatsApp
- ✅ **IA Contextual** com histórico de conversa
- ✅ **Detecção de Idioma** (Português/Inglês)
- ✅ **Prompt Comercial** em YAML configurável
- ✅ **Escalável** em microsserviços
- ✅ **Seguro** com validação de webhooks
- ✅ **Monitorável** com logging completo

---

## 🔧 Stack Tecnológico

### Backend
| Tecnologia | Versão | Propósito |
|-----------|--------|----------|
| **Python** | 3.11.6 | Linguagem principal |
| **FastAPI** | 0.104.1 | Framework web assíncrono |
| **Uvicorn** | 0.24.0 | Servidor ASGI |
| **Pydantic** | 2.5.0 | Validação de dados |

### Integrações Externas
| Serviço | Modelo | Propósito |
|--------|--------|----------|
| **Twilio** | Programmable Messaging | Webhook WhatsApp, envio de mensagens |
| **Google Gemini** | 2.5 Flash | Processamento de IA e geração de respostas |

### Dependências Utilitárias
| Pacote | Versão | Propósito |
|--------|--------|----------|
| **python-dotenv** | 1.0.0 | Gerenciamento de variáveis de ambiente |
| **python-multipart** | 0.0.6 | Parsing de FormData do Twilio |
| **pyyaml** | 6.0.1 | Carregamento de prompts YAML |

---

## 🔄 Migração: Meta → Twilio

### Motivação da Migração

| Aspecto | Meta Cloud API | Twilio |
|--------|----------------|--------|
| **Setup** | Complexo (App ID, Business Account) | Simples (Account SID + Token) |
| **Webhook** | JSON estruturado | FormData simples |
| **Rate Limiting** | Restritivo | Flexível |
| **Suporte** | Community | Comercial 24/7 |
| **Preço** | Variável por volume | Fixo por mensagem |

**Twilio:**
```python
# twilio_service.py
from twilio.rest import Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
message = client.messages.create(to=f"whatsapp:{number}", body=text, from_=TWILIO_WHATSAPP_NUMBER)
```

## 🏗️ Arquitetura Detalhada

### Diagrama de Fluxo

```
┌─────────────┐
│   Usuario   │
│  WhatsApp   │
└──────┬──────┘
       │ Envia "hi"
       ▼
┌──────────────┐
│    Twilio    │ FormData: {From, To, Body, MessageSid, ...}
│  (Webhook)   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│   FastAPI POST /webhook              │
│   - form_data = await request.form() │
│   - data = dict(form_data)           │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  webhook_handler.process_webhook()   │
│  - Extrai From (sender_id)           │
│  - Extrai Body (message_body)        │
│  - Valida dados                      │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  ChatSessionManager                  │
│  - get_or_create_session(user_id)   │
│  - Mantém histórico de conversa      │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  GeminiChatSession.send_message()    │
│  - System Instruction: prompt YAML   │
│  - Message history context           │
│  - Returns: IA response              │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  TwilioWhatsAppClient                │
│  - send_text_message()               │
│  - to: formatted number              │
│  - body: IA response                 │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────┐
│    Twilio    │ Envia resposta
│  (API POST)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Usuario    │ Recebe resposta
│  WhatsApp    │
└──────────────┘
```

### Camadas da Aplicação

```
┌────────────────────────────────────┐
│     Apresentação (API FastAPI)     │
│  GET /  GET /health  POST /webhook │
└────────┬─────────────────────────┬─┘
         │                         │
┌────────▼────────┐    ┌───────────▼──────────┐
│  Handlers Layer │    │  Services Layer      │
│  webhook_handler├───►│  - twilio_service    │
│                 │    │  - gemini_client     │
└─────────────────┘    │  - config            │
                       └──────────┬───────────┘
                                  │
                    ┌─────────────▼──────────┐
                    │   External APIs        │
                    │  - Twilio REST API     │
                    │  - Google Gemini API   │
                    └────────────────────────┘
```

---

## 🔌 Componentes do Sistema

### 1. **app.py** - Aplicação Principal
Responsabilidades:
- Orquestração de rotas FastAPI
- Inicialização de clientes (Twilio, Gemini)
- Tratamento de requisições HTTP
- Logging de operações

```python
@app.post("/webhook")
async def handle_webhook(request: Request):
    form_data = await request.form()
    webhook_data = await process_webhook(dict(form_data))
    # ... processamento ...
    return {"status": "success"}
```

### 2. **handlers/webhook_handler.py** - Manipulador de Webhooks
Responsabilidades:
- Parsing de FormData do Twilio
- Extração de dados da mensagem
- Validação de integridade
- Tratamento de erros

```python
async def process_webhook(data: dict) -> dict:
    message_sid = data.get("MessageSid")
    from_number = data.get("From").replace("whatsapp:", "")
    message_body = data.get("Body", "")
    # ... validação e return ...
```

### 3. **services/twilio_service.py** - Cliente Twilio
Responsabilidades:
- Conexão com API Twilio
- Envio de mensagens WhatsApp
- Tratamento de erros Twilio
- Logging de transações

```python
class TwilioWhatsAppClient:
    def send_text_message(self, to_number: str, body: str):
        message = self.client.messages.create(
            to=f"whatsapp:{to_number}",
            body=body,
            from_=self.twilio_whatsapp_number
        )
```

### 4. **services/gemini_client.py** - Cliente Gemini
Responsabilidades:
- Sessões de chat por usuário
- Gerenciamento de histórico
- Carregamento de prompts YAML
- Comunicação com Gemini API

```python
class GeminiChatSession:
    def __init__(self, user_id: str, system_instruction: Optional[str] = None):
        # Load prompt_template()
        self.chat = self.client.chats.create(
            model="gemini-2.5-flash",
            config={"system_instruction": system_instruction}
        )
```

### 5. **config.py** - Gerenciamento de Configuração
Responsabilidades:
- Leitura de variáveis de ambiente
- Validação de credenciais
- Definição de constantes
- Tratamento de erros de configuração

```python
class Config:
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    # ... validações ...
```

### 6. **models.py** - Modelos de Dados
Define estruturas Pydantic para:
- Validação de payloads
- Type hints
- Documentação automática

---

## 📡 Fluxo de Dados Completo

### Exemplo: Usuário envia "Olá, tenho dúvida sobre o PSPM"

#### 1️⃣ Recebimento (Twilio → FastAPI)
```
POST /webhook HTTP/1.1
Content-Type: application/x-www-form-urlencoded

MessageSid=SMd7da464df2483d2a8bc7b1009726dfd5
From=whatsapp:+xxxxxxxxxxxx
To=whatsapp:+14155238886
Body=Olá, tenho dúvida sobre o PSPM
NumMedia=0
```

#### 2️⃣ Parsing (webhook_handler.py)
```python
data = {
    'From': 'whatsapp:+xxxxxxxxxxxx',
    'Body': 'Olá, tenho dúvida sobre o PSPM',
    'MessageSid': 'SMd7da464df2483d2a8bc7b1009726dfd5',
    ...
}

# Extrai:
sender_id = "+447833106092"
message_body = "Olá, tenho dúvida sobre o PSPM"
message_type = "text"
```

#### 3️⃣ Gerenciamento de Sessão (ChatSessionManager)
```python
chat_session = chat_manager.get_or_create_session("+447833106092")
# Se não existe, cria nova GeminiChatSession com prompt CryptoLock
```

#### 4️⃣ Processamento Gemini (GeminiChatSession)
```
System Instruction (de prompts/cryptolock_atendente_v1.yaml):
"Você é um Atendente Comercial da CryptoLock...
Objetivo: Vender e fornecer informações sobre o PSPM..."

User Message: "Olá, tenho dúvida sobre o PSPM"

Gemini Response: "Olá! Sou o atendente da CryptoLock. 
Ficarei feliz em esclarecer suas dúvidas sobre o PSPM.
O PSPM é um firewall inteligente para pipelines CI/CD que..."
```

#### 5️⃣ Envio da Resposta (TwilioWhatsAppClient)
```python
message = client.messages.create(
    to="whatsapp:+xxxxxxxxxxxx",
    body="Olá! Sou o atendente da CryptoLock...",
    from_="whatsapp:+14155238886"
)
```

#### 6️⃣ Resposta ao Usuário (Twilio → WhatsApp)
```
Usuário recebe a mensagem no WhatsApp em tempo real
```

#### 7️⃣ Logging
```
[INFO] Nova sessão de chat criada para usuário +447833106092
[INFO] Mensagem recebida de +447833106092: 'Olá, tenho dúvida...'
[INFO] Enviando para Gemini: 'Olá, tenho dúvida...'
[INFO] Resposta Gemini: 'Olá! Sou o atendente...'
[INFO] Resposta Twilio enviada: SMd6133526bdefa64a6f0d1f0eeaea4a4a
```

---

## 🤖 Integração Gemini

### Prompt Template (YAML)
Arquivo: `prompts/cryptolock_atendente_v1.yaml`

```yaml
persona:
  role: "Atendente Comercial da CryptoLock"
  company: "CryptoLock"
  product: "Pipeline Security Posture Management (PSPM)"
  goal: "Vender e fornecer informações..."

instructions:
  - "Analise o idioma da mensagem (Português/Inglês)"
  - "Responda no MESMO idioma detectado"
  - "Use documentação como fonte exclusiva"
  - "Seja proativo e dirija para benefícios"

contexto_do_produto: |
  PSPM é um firewall para CI/CD que bloqueia:
  - Vulnerabilidades
  - Segredos vazados
  - Dependências maliciosas
  - Misconfigurations
```

### Carregamento Dinâmico
```python
def load_prompt_template(prompt_file: str = "prompts/cryptolock_atendente_v1.yaml") -> str:
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_data = yaml.safe_load(f)
    
    # Constrói system_instruction formatado
    return formatted_instruction
```

### Modelo Utilizado
- **Modelo:** `gemini-2.5-flash`
- **Velocidade:** ~100ms por mensagem
- **Qualidade:** Excelente para conversação
- **Custo:** Gratuito na camada free tier

---

## 📞 Integração Twilio

### Configuração de Webhooks
1. **URL:** `https://seu-dominio.com/webhook`
2. **Método:** POST
3. **Content-Type:** `application/x-www-form-urlencoded`

### Validação de Assinatura
```python
# Header esperado
X-Twilio-Signature: <signature_hash>

# Validação (feita internamente pelo Twilio SDK)
```

### Limitações e Quotas
- **Messages:** Taxa por conta
- **Sandbox:** 1.000 conversas testáveis
- **Produção:** Escalável conforme plano

---

## 👥 Gerenciamento de Sessões

### Estrutura de Sessão
```python
{
    "user_id": "+xxxxxxxxxxxx",
    "chat_session": <GeminiChatSession>,
    "created_at": "2025-12-04T10:30:00",
    "message_count": 5,
    "last_message": "2025-12-04T10:35:22"
}
```

### Ciclo de Vida
1. **Criação:** Primeira mensagem do usuário
2. **Manutenção:** Histórico de conversa ativo
3. **Retenção:** Memória na RAM enquanto servidor roda
4. **Limpeza:** Manual via `delete_session(user_id)` ou `clear_all_sessions()`

### Persistência
- **Atual:** Em-memory (RAM)
- **Futuro:** Redis, PostgreSQL, MongoDB

---

## 🔒 Segurança

### Autenticação
- ✅ Credenciais Twilio em `.env` (não no código)
- ✅ API Key Gemini em `.env` (não no código)
- ✅ Token de verificação de webhook em `.env`

### Validação
- ✅ Parsing seguro de FormData
- ✅ Validação de campos obrigatórios
- ✅ Tratamento de exceções
- ✅ Rate limiting (via Twilio)

### Logging Seguro
- ⚠️ Não log de credenciais
- ⚠️ Sanitizar dados sensíveis
- ✅ Registrar IDs de mensagens

### HTTPS
- ✅ Twilio exige HTTPS para webhooks
- ✅ Use certificados SSL válidos

---

## ⚡ Performance

### Tempos Típicos
| Operação | Tempo |
|----------|-------|
| Parse FormData | ~1ms |
| Session lookup | ~0.5ms |
| Gemini API call | ~500-1000ms |
| Twilio send | ~200-500ms |
| Total | ~1-2 segundos |

### Otimizações
1. **Async/Await:** FastAPI processa requisições em paralelo
2. **Connection Pooling:** Reutiliza conexões HTTP
3. **Caching:** Sessões mantidas em memória
4. **Lazy Loading:** Carrega prompts uma vez

### Escalabilidade
- **Vertical:** Adicione CPU/RAM
- **Horizontal:** Múltiplas instâncias + load balancer + Redis para sessões

---

## 🚀 Próximos Passos

### Curto Prazo (Semanas 1-2)
- [ ] Testar full flow com mensagens reais
- [ ] Refinementar prompt CryptoLock
- [ ] Implementar logging a arquivo
- [ ] Configurar monitoramento

### Médio Prazo (Semanas 3-4)
- [ ] Persistência de sessões (Redis/PostgreSQL)
- [ ] Analytics de conversas
- [ ] Dashboard de métricas
- [ ] Tratamento de mídia (imagens, PDFs)

### Longo Prazo (Mês 2+)
- [ ] Integração com CRM
- [ ] Suporte a múltiplos idiomas
- [ ] Fallback para atendimento humano
- [ ] Deploy em produção (Heroku/AWS/GCP)
- [ ] Testes de carga e stress
- [ ] Documentação da API (OpenAPI)

---

## 📚 Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [Google Gemini Documentation](https://ai.google.dev/docs)
- [Python Async IO](https://docs.python.org/3/library/asyncio.html)

---

**Última Atualização:** 2025-12-04  
**Status:** ✅ Produção Ativa  
**Versão:** 1.0.0
