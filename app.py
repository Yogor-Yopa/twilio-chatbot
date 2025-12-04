"""
Módulo principal do aplicativo FastAPI.
Integração do WhatsApp com Google Gemini 2.5 Flash via Twilio.

Este módulo coordena:
- Verificação do webhook do Twilio WhatsApp
- Recebimento e processamento de mensagens
- Integração com IA Gemini
- Envio de respostas via Twilio Programmable Messaging
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from starlette.status import HTTP_200_OK

from config import Config
from handlers.webhook_handler import verify_webhook, process_webhook
from services.gemini_client import ChatSessionManager
from services.twilio_service import TwilioWhatsAppClient, TwilioMessageError
from typing import cast


# Inicialização da aplicação
app = FastAPI(
    title="CryptoLock Chatbot API",
    description="API de integração WhatsApp com Gemini AI via Twilio",
    version="1.0.0"
)

# Validação de configuração na inicialização
try:
    Config.validate()
except EnvironmentError as e:
    raise RuntimeError(f"Falha na inicialização: {e}")

# Instância do gerenciador de sessões de chat
chat_manager = ChatSessionManager()

# Cliente do Twilio
try:
    twilio_client = TwilioWhatsAppClient()
except TwilioMessageError as e:
    print(f"[WARNING] Cliente Twilio não inicializado: {e}")
    twilio_client = None


# ============================================================================
# ROTAS DE INFO
# ============================================================================

@app.get("/")
async def root():
    """
    Rota raiz com informações da API.
    
    Returns:
        dict: Informações sobre a aplicação
    """
    return {
        "message": "CryptoLock Chatbot API - Twilio WhatsApp Integration",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "webhook_get": "GET /webhook (Twilio verification)",
            "webhook_post": "POST /webhook (Receive messages)",
            "docs": "/docs (Interactive API documentation)",
            "redoc": "/redoc (ReDoc documentation)"
        },
        "technology": {
            "framework": "FastAPI",
            "ai_model": "Google Gemini 2.5 Flash",
            "messaging": "Twilio Programmable Messaging"
        }
    }


# ============================================================================
# ROTAS DE WEBHOOK
# ============================================================================

@app.get("/webhook")
async def verify_webhook_endpoint(request: Request):
    """
Endpoint responsável por validar o webhook do Twilio.
Para Twilio, retorna sucesso simples. A validação completa de assinatura
é feita pelo Twilio SDK internamente.
    """

    try:
        # Valida parâmetros e retorna ok
        result = await verify_webhook(request)

        # Retorna resposta em texto puro
        return PlainTextResponse(content=result, status_code=200)

    except HTTPException:
        # Erros esperados (token inválido, parâmetros ausentes)
        raise

    except Exception as e:
        # Qualquer erro inesperado
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao verificar webhook")


@app.post("/webhook")
async def handle_webhook(request: Request):
    """
    Recebe e processa mensagens do WhatsApp via Twilio.
    Integra com IA Gemini e envia respostas via Twilio.
    
    Nota: Twilio envia dados como FormData (x-www-form-urlencoded),
    não como JSON. FastAPI converte automaticamente para dict.
    
    Returns:
        dict: Status do processamento
    """
    print("\n" + "="*80)
    print("[WEBHOOK] POST /webhook ACIONADO!")
    print("="*80)
    
    try:
        # Obtém dados do FormData enviado pelo Twilio
        form_data = await request.form()
        data = dict(form_data)
        
        print(f"[WEBHOOK] FormData recebido com {len(data)} campos")
        print(f"[WEBHOOK] Campos: {list(data.keys())}")
        print(f"[WEBHOOK] Conteúdo: {data}")
        
        # Processa os dados brutos do webhook
        webhook_data = await process_webhook(data)
        
        # Se não há mensagens ou é notificação inválida, ignora
        if webhook_data.get("status") == "ignored":
            print(f"[INFO] Evento ignorado: {webhook_data.get('type')}")
            return {"status": "success", "message": "Evento ignorado"}
        
        # Se houve erro no processamento
        if webhook_data.get("status") == "error":
            error_detail = webhook_data.get('detail', 'Erro desconhecido')
            print(f"[ERROR] Erro ao processar webhook: {error_detail}")
            return {"status": "error", "message": f"Erro ao processar: {error_detail}"}
        
        # Extrai dados da mensagem
        sender_id = webhook_data.get("sender_id")
        message_type = webhook_data.get("message_type")
        message_body = webhook_data.get("message_body", "")
        message_sid = webhook_data.get("message_sid")
        
        # Processa mensagens de texto
        if message_type == "text" and message_body:
            
            if not sender_id:
                print("[WARNING] Mensagem ou ID do remetente vazio recebido")
                return {"status": "success", "message": "Mensagem vazia"}
            
            print(f"[INFO] Mensagem recebida de {sender_id}: '{message_body}'")
            
            # Obtém ou cria sessão de chat
            chat_session = chat_manager.get_or_create_session(str(sender_id))
            
            # Gera resposta com IA
            try:
                print(f"[INFO] Enviando para Gemini: '{message_body}'")
                ai_response = chat_session.send_message(message_body)
                print(f"[INFO] Resposta Gemini: '{ai_response}'")
            except Exception as e:
                print(f"[ERROR] Erro ao obter resposta do Gemini: {e}")
                import traceback
                traceback.print_exc()
                ai_response = "Desculpe, ocorreu um erro ao processar sua mensagem."
            
            # Envia resposta via WhatsApp com Twilio
            if twilio_client:
                try:
                    print(f"[INFO] Enviando resposta via Twilio para {sender_id}")
                    result = twilio_client.send_text_message(str(sender_id), ai_response)
                    print(f"[INFO] Resposta Twilio enviada: {result.get('message_sid')}")
                except TwilioMessageError as e:
                    print(f"[ERROR] Falha ao enviar resposta: {e}")
                    return {"status": "error", "message": f"Falha ao enviar: {e}"}
            else:
                print("[WARNING] Cliente Twilio não disponível, resposta não enviada")
                return {"status": "warning", "message": "Twilio não disponível"}
            
            return {"status": "success", "message": "Mensagem processada"}
        
        elif message_type == "media":
            print(f"[INFO] Mensagem de mídia recebida de {sender_id}")
            return {"status": "success", "message": "Mídia recebida"}
        
        else:
            print(f"[INFO] Tipo de mensagem não suportado: {message_type}")
            return {"status": "success", "message": "Tipo de mensagem não suportado"}
    
    except Exception as e:
        print(f"[ERROR] Erro crítico ao processar webhook: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*80)
        print("[WEBHOOK] FIM DO PROCESSAMENTO COM ERRO")
        print("="*80 + "\n")
        return {"status": "error", "message": f"Erro crítico: {e}"}
    
    print("\n" + "="*80)
    print("[WEBHOOK] FIM DO PROCESSAMENTO COM SUCESSO")
    print("="*80 + "\n")



# ============================================================================
# ROTAS DE STATUS (Opcional - para monitoramento)
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Verifica a saúde da aplicação.
    
    Returns:
        dict: Status da aplicação
    """
    return {
        "status": "ok",
        "service": "CryptoLock Chatbot API",
        "active_sessions": len(chat_manager.sessions)
    }


@app.get("/status")
async def get_status():
    """
    Retorna informações detalhadas sobre o estado da aplicação.
    
    Returns:
        dict: Status completo do sistema
    """
    twilio_sid = Config.TWILIO_ACCOUNT_SID if twilio_client else "not_available"
    twilio_number = Config.TWILIO_WHATSAPP_NUMBER if twilio_client else "not_available"
    
    return {
        "status": "running",
        "version": "1.0.0",
        "services": {
            "twilio": {
                "available": twilio_client is not None,
                "account_sid": twilio_sid,
                "whatsapp_number": twilio_number
            },
            "gemini": {
                "available": True,
                "model": Config.GEMINI_MODEL
            }
        },
        "sessions": {
            "active_chat_sessions": len(chat_manager.sessions)
        },
        "configuration": {
            "debug_mode": Config.DEBUG,
            "server_host": Config.SERVER_HOST,
            "server_port": Config.SERVER_PORT
        }
    }


# ============================================================================
# INICIALIZAÇÃO DO SERVIDOR
# ============================================================================
# Para iniciar o servidor, use:
# uvicorn app:app --host 0.0.0.0 --port 8000
# ou
# python -m uvicorn app:app --host 0.0.0.0 --port 8000

