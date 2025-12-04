"""
Módulo de integração com Twilio Programmable Messaging.
Responsável pelo envio e recebimento de mensagens via WhatsApp através do Twilio.

Substitui completamente a integração anterior com Meta WhatsApp Cloud API.
"""

from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from config import Config


class TwilioMessageError(Exception):
    """Exceção para erros ao enviar/receber mensagens via Twilio."""
    pass


class TwilioWhatsAppClient:
    """Cliente para integração com Twilio Programmable Messaging para WhatsApp."""
    
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        twilio_whatsapp_number: Optional[str] = None
    ):
        """
        Inicializa o cliente do Twilio.
        
        Args:
            account_sid: SID da conta Twilio (usa Config.TWILIO_ACCOUNT_SID se não fornecido).
            auth_token: Auth Token Twilio (usa Config.TWILIO_AUTH_TOKEN se não fornecido).
            twilio_whatsapp_number: Número WhatsApp Twilio (usa Config.TWILIO_WHATSAPP_NUMBER se não fornecido).
            
        Raises:
            TwilioMessageError: Se credenciais essenciais não estiverem configuradas.
        """
        self.account_sid = account_sid or Config.TWILIO_ACCOUNT_SID
        self.auth_token = auth_token or Config.TWILIO_AUTH_TOKEN
        self.twilio_whatsapp_number = twilio_whatsapp_number or Config.TWILIO_WHATSAPP_NUMBER
        
        # Validação de credenciais
        if not all([self.account_sid, self.auth_token, self.twilio_whatsapp_number]):
            raise TwilioMessageError(
                "Credenciais Twilio incompletas. Verifique: "
                "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER"
            )
        
        # Inicializa cliente Twilio
        try:
            self.client = Client(self.account_sid, self.auth_token)
        except Exception as e:
            raise TwilioMessageError(f"Erro ao inicializar cliente Twilio: {e}") from e
    
    def send_text_message(
        self,
        recipient_number: str,
        message_body: str,
        media_urls: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        Envia uma mensagem de texto via WhatsApp pelo Twilio.
        
        Args:
            recipient_number: Número do destinatário com código do país (ex: +5511999999999).
            message_body: Conteúdo da mensagem.
            media_urls: Lista opcional de URLs de mídia para enviar (imagens, vídeos, áudio).
            
        Returns:
            dict: Resposta do Twilio contendo SID da mensagem e status.
            
        Raises:
            TwilioMessageError: Se houver erro ao enviar a mensagem.
        """
        try:
            # Garante que o número começa com '+'
            if not recipient_number.startswith('whatsapp:+') and not recipient_number.startswith('+'):
                recipient_number = f"whatsapp:+{recipient_number.lstrip('+')}"
            elif recipient_number.startswith('+'):
                recipient_number = f"whatsapp:{recipient_number}"
            
            # Número de origem do Twilio
            from_number = f"whatsapp:{self.twilio_whatsapp_number}"
            
            # Envia mensagem de texto
            if media_urls:
                # Se há mídia, envia com media_url (para primeira URL)
                message = self.client.messages.create(
                    body=message_body,
                    from_=from_number,
                    to=recipient_number,
                    media_url=media_urls[0] if media_urls else None
                )
            else:
                # Mensagem de texto puro
                message = self.client.messages.create(
                    body=message_body,
                    from_=from_number,
                    to=recipient_number
                )
            
            result = {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
                "to": recipient_number,
                "from": from_number
            }
            
            print(f"[INFO] Mensagem Twilio enviada para {recipient_number}: SID={message.sid}")
            return result
            
        except TwilioRestException as e:
            error_detail = f"Erro Twilio {e.status}: {e.msg}"
            print(f"[ERROR] Erro ao enviar mensagem para {recipient_number}: {error_detail}")
            raise TwilioMessageError(error_detail) from e
            
        except Exception as e:
            error_detail = str(e)
            print(f"[ERROR] Erro inesperado ao enviar mensagem para {recipient_number}: {error_detail}")
            raise TwilioMessageError(f"Erro ao enviar mensagem: {error_detail}") from e
    
    def get_message_status(self, message_sid: str) -> str:
        """
        Obtém o status de uma mensagem já enviada.
        
        Args:
            message_sid: SID da mensagem.
            
        Returns:
            str: Status da mensagem (queued, sending, sent, delivered, failed, etc).
            
        Raises:
            TwilioMessageError: Se houver erro ao obter o status.
        """
        try:
            message = self.client.messages(message_sid).fetch()
            return message.status
        except TwilioRestException as e:
            raise TwilioMessageError(f"Erro ao obter status da mensagem: {e.msg}") from e
    
    def parse_incoming_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpreta dados recebidos do webhook de entrada do Twilio.
        
        Args:
            webhook_data: Dados do webhook (geralmente FormData convertida para dict).
            
        Returns:
            dict: Dicionário estruturado com informações da mensagem.
            
        Raises:
            TwilioMessageError: Se os dados forem inválidos.
        """
        try:
            # Extrai informações do webhook Twilio
            message_sid = webhook_data.get("MessageSid")
            account_sid = webhook_data.get("AccountSid")
            from_number = webhook_data.get("From", "").replace("whatsapp:", "")
            to_number = webhook_data.get("To", "").replace("whatsapp:", "")
            message_body = webhook_data.get("Body", "")
            num_media = int(webhook_data.get("NumMedia", 0))
            
            # Valida dados essenciais
            if not message_sid or not from_number:
                raise TwilioMessageError("Dados de mensagem incompletos no webhook")
            
            # Extrai URLs de mídia se houver
            media_urls = []
            for i in range(num_media):
                media_url = webhook_data.get(f"MediaUrl{i}")
                if media_url:
                    media_urls.append(media_url)
            
            return {
                "status": "success",
                "message_sid": message_sid,
                "account_sid": account_sid,
                "sender_id": from_number,
                "message_type": "text" if not media_urls else "media",
                "message_body": message_body,
                "media_urls": media_urls,
                "timestamp": webhook_data.get("Timestamp", ""),
                "raw_webhook": webhook_data
            }
            
        except (KeyError, ValueError, TypeError) as e:
            print(f"[ERROR] Erro ao processar webhook Twilio: {e}")
            raise TwilioMessageError(f"Erro ao processar webhook: {e}") from e
    
    def verify_webhook_signature(
        self,
        url: str,
        post_data: Dict[str, Any],
        signature_header: str
    ) -> bool:
        """
        Verifica a assinatura do webhook para garantir que veio do Twilio.
        
        Args:
            url: URL completa do webhook (ex: https://seu-servidor.com/webhook).
            post_data: Dados POST recebidos.
            signature_header: Header X-Twilio-Signature da requisição.
            
        Returns:
            bool: True se a assinatura for válida, False caso contrário.
        """
        try:
            from twilio.request_validator import RequestValidator
            
            validator = RequestValidator(self.auth_token)
            
            # Reconstrói a query string a partir dos dados POST
            params_string = ''.join(f"{k}{v}" for k, v in sorted(post_data.items()))
            url_with_params = f"{url}{params_string}"
            
            is_valid = validator.validate(url_with_params, signature_header)
            
            if not is_valid:
                print(f"[WARNING] Assinatura de webhook inválida: {signature_header}")
            
            return is_valid
            
        except Exception as e:
            print(f"[ERROR] Erro ao verificar assinatura do webhook: {e}")
            return False


def send_whatsapp_message(
    recipient_number: str,
    message_body: str,
    media_urls: Optional[list[str]] = None,
    account_sid: Optional[str] = None,
    auth_token: Optional[str] = None,
    twilio_whatsapp_number: Optional[str] = None
) -> bool:
    """
    Função auxiliar para compatibilidade e facilidade de uso.
    Envia uma mensagem de texto via WhatsApp usando o Twilio.
    
    Args:
        recipient_number: Número do destinatário.
        message_body: Conteúdo da mensagem.
        media_urls: URLs de mídia opcionais.
        account_sid: SID da conta Twilio (usa Config se não fornecido).
        auth_token: Auth Token (usa Config se não fornecido).
        twilio_whatsapp_number: Número Twilio (usa Config se não fornecido).
        
    Returns:
        bool: True se enviado com sucesso, False caso contrário.
    """
    try:
        client = TwilioWhatsAppClient(
            account_sid=account_sid,
            auth_token=auth_token,
            twilio_whatsapp_number=twilio_whatsapp_number
        )
        client.send_text_message(recipient_number, message_body, media_urls)
        return True
    except TwilioMessageError as e:
        print(f"[ERROR] {e}")
        return False
