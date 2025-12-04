"""
Módulo de configuração centralizada da aplicação.
Gerencia variáveis de ambiente e constantes do projeto.
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


class Config:
    """Classe para armazenar configurações da aplicação."""
    
    # Variáveis de ambiente críticas
    VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    
    # Credenciais Twilio Programmable Messaging
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")
    
    # Modelo de IA padrão
    GEMINI_MODEL = "gemini-2.5-flash"
    
    # Configuração do servidor
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8000
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    
    @classmethod
    def validate(cls):
        """Valida se todas as variáveis críticas estão configuradas."""
        required_vars = [
            ("VERIFY_TOKEN", cls.VERIFY_TOKEN),
            ("GEMINI_API_KEY", cls.GEMINI_API_KEY),
            ("TWILIO_ACCOUNT_SID", cls.TWILIO_ACCOUNT_SID),
            ("TWILIO_AUTH_TOKEN", cls.TWILIO_AUTH_TOKEN),
            ("TWILIO_WHATSAPP_NUMBER", cls.TWILIO_WHATSAPP_NUMBER),
        ]
        
        missing_vars = [name for name, value in required_vars if not value]
        
        if missing_vars:
            raise EnvironmentError(
                f"Variáveis de ambiente obrigatórias não configuradas: {', '.join(missing_vars)}. "
                "Verifique o arquivo .env e a instalação do python-dotenv."
            )
    
    @classmethod
    def validate_twilio(cls) -> bool:
        """Valida se configurações Twilio estão corretas."""
        return all([cls.TWILIO_ACCOUNT_SID, cls.TWILIO_AUTH_TOKEN, cls.TWILIO_WHATSAPP_NUMBER])
