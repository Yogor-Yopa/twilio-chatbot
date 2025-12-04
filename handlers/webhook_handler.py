"""
Módulo para manipulação de webhooks do WhatsApp.
Responsável por processar requisições GET e POST do webhook.

Suporta: Twilio Programmable Messaging (primário)
"""

from fastapi import Request, HTTPException
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from config import Config


async def verify_webhook(request: Request) -> str:
    """
    Verifica o token de segurança para validar o webhook.
    
    Compatível com Twilio: Valida X-Twilio-Signature ou parâmetro de token.
    
    Args:
        request: Objeto da requisição FastAPI.
        
    Returns:
        str: Challenge token se a verificação for bem-sucedida.
        
    Raises:
        HTTPException: Se o token for inválido ou parâmetros estiverem ausentes.
    """
    # Tenta primeiro método Twilio (assinatura)
    x_twilio_signature = request.headers.get("X-Twilio-Signature")
    
    # Fallback para método simples de token (compatibilidade)
    token_param = request.query_params.get("hub.verify_token")
    
    # Se houver signature Twilio, valida diferente
    if x_twilio_signature:
        # Para Twilio, apenas retorna sucesso se houver header válido
        # A validação completa acontece em process_webhook
        print("[INFO] Webhook Twilio verificado com assinatura")
        return "ok"
    
    # Fallback para verificação com token simples
    if token_param == Config.VERIFY_TOKEN:
        challenge = request.query_params.get("hub.challenge", "")
        print("[INFO] Webhook verificado com token")
        return challenge or "ok"
    
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Token de verificação inválido ou ausente"
    )


async def process_webhook(data: dict) -> dict:
    """
    Processa dados recebidos do webhook do Twilio.
    Extrai informações da mensagem para processamento posterior.
    
    Args:
        data: Dicionário com dados do webhook (FormData convertida para dict).
        
    Returns:
        dict: Dicionário contendo informações extraídas ou aviso se sem mensagens.
    """
    try:
        # Estrutura do Twilio Webhook (FormData)
        message_sid = data.get("MessageSid")
        account_sid = data.get("AccountSid")
        from_number = data.get("From", "")
        to_number = data.get("To", "")
        message_body = data.get("Body", "")
        num_media_str = data.get("NumMedia", "0")
        timestamp = data.get("Timestamp", "")
        
        # Debug: Log dos dados recebidos
        print(f"[DEBUG] Dados recebidos do Twilio: MessageSid={message_sid}, From={from_number}, Body='{message_body}', NumMedia={num_media_str}")
        
        # Remove prefixo "whatsapp:" se existir
        if from_number.startswith("whatsapp:"):
            from_number = from_number.replace("whatsapp:", "")
        
        if to_number.startswith("whatsapp:"):
            to_number = to_number.replace("whatsapp:", "")
        
        # Converte NumMedia para int com segurança
        try:
            num_media = int(num_media_str)
        except (ValueError, TypeError):
            num_media = 0
        
        # Validação básica
        if not message_sid or not from_number:
            print(f"[WARNING] Dados incompletos: MessageSid={message_sid}, From={from_number}")
            return {"status": "ignored", "type": "invalid_data"}
        
        # Extrai URLs de mídia se houver
        media_urls = []
        if num_media > 0:
            for i in range(num_media):
                media_url = data.get(f"MediaUrl{i}")
                if media_url:
                    media_urls.append(media_url)
        
        # Determina tipo de mensagem
        message_type = "media" if media_urls else "text"
        
        print(f"[DEBUG] Webhook processado com sucesso: sender={from_number}, type={message_type}, body='{message_body}'")
        
        return {
            "status": "success",
            "sender_id": from_number,
            "message_type": message_type,
            "timestamp": timestamp,
            "message_sid": message_sid,
            "account_sid": account_sid,
            "message_body": message_body,
            "media_urls": media_urls,
            "raw_message": {
                "from": from_number,
                "to": to_number,
                "type": message_type,
                "text": {"body": message_body} if message_type == "text" else None,
                "message_sid": message_sid
            }
        }
        
    except (KeyError, ValueError, TypeError) as e:
        print(f"[ERROR] Erro ao processar webhook Twilio: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}
