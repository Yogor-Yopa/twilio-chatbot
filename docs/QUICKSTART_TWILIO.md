# ⚡ QUICK START - SETUP TWILIO EM 5 MINUTOS

## 1️⃣ Obter Credenciais Twilio (2 min)

1. Acesse https://www.twilio.com/console
2. Copie **Account SID** e **Auth Token** (visíveis no dashboard)
3. Vá para **Develop** → **Messaging** → **Try it out** → **WhatsApp Sandbox**
4. Copie o número WhatsApp fornecido (ex: `+14155552671`)

## 2️⃣ Configurar `.env` (1 min)

```bash
# Na raiz do projeto, copie o template:
cp .env.example .env

# Edite .env com seus valores:
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=+14155552671
VERIFY_TOKEN=seu_token_aleatorio_qualquer
GEMINI_API_KEY=sua_chave_gemini_aqui
```

## 3️⃣ Instalar Dependências (1 min)

```bash
pip install -r requirements.txt
```

## 4️⃣ Iniciar Servidor (30 seg)

```bash
python app.py
# ou
uvicorn app:app --reload
```

Esperado:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 5️⃣ Validar Health (30 seg)

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "ok",
  "service": "CryptoLock Chatbot API",
  "active_sessions": 0
}
```

## ✅ Pronto! 

Sua aplicação está rodando com Twilio. Agora configure o webhook URL no Twilio Console.

---

### 🔗 Próximo Passo: Configurar Webhook no Twilio

1. Twilio Console → Messaging → WhatsApp Sandbox
2. Campo **"When a message comes in"**: `https://seu-servidor.com/webhook`
3. Clique em **"Save"**
4. Envie uma mensagem para o número Twilio via WhatsApp

**Pronto! 🎉**

---

### 📚 Documentação Completa

- Instruções detalhadas: `/docs/MIGRATION_META_TO_TWILIO.md`
- Resumo executivo: `/docs/SUMMARY_MIGRATION.md`
- Código novo: `/services/twilio_service.py`
