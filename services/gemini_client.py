"""
Módulo de integração com Google Gemini AI.
Responsável pela comunicação com a API do Gemini e gerenciamento de sessões de chat.
"""

from typing import Optional
import os
import yaml
from google import genai

from config import Config


def load_prompt_template(prompt_file: str = "prompts/cryptolock_atendente_v1.yaml") -> str:
    """
    Carrega o template do prompt a partir de um arquivo YAML.
    
    Args:
        prompt_file: Caminho relativo do arquivo YAML com o prompt.
        
    Returns:
        str: Instrução de sistema formatada para o Gemini.
    """
    try:
        # Encontra a raiz do projeto
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_path = os.path.join(current_dir, prompt_file)
        
        if not os.path.exists(prompt_path):
            print(f"[WARNING] Arquivo de prompt não encontrado: {prompt_path}. Usando prompt padrão.")
            return None
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_data = yaml.safe_load(f)
        
        # Constrói a instrução de sistema a partir do YAML
        persona = prompt_data.get('persona', {})
        instructions = prompt_data.get('instructions', [])
        contexto = prompt_data.get('contexto_do_produto', '')
        
        system_instruction = f"""
Você é {persona.get('role', 'um assistente')} da {persona.get('company', 'CryptoLock')}.
Seu produto: {persona.get('product', 'Pipeline Security Posture Management (PSPM)')}.
Objetivo: {persona.get('goal', 'Fornecer informações e vendas do produto')}.

INSTRUÇÕES CRÍTICAS:
{chr(10).join(f"- {instr}" for instr in instructions)}

CONTEXTO DO PRODUTO:
{contexto}

FORMATO DE RESPOSTA:
- Inicie com uma saudação profissional em CryptoLock
- Responda focado na necessidade do usuário
- Cite informações da documentação quando relevante
- Conclua de forma proativa com próximos passos
""".strip()
        
        print(f"[INFO] Prompt carregado com sucesso: {prompt_data.get('prompt_id')}")
        return system_instruction
        
    except Exception as e:
        print(f"[ERROR] Erro ao carregar prompt: {e}")
        return None


class GeminiChatSession:
    """Gerencia uma sessão de chat com o Gemini AI."""
    
    def __init__(self, user_id: str, system_instruction: Optional[str] = None):
        """
        Inicializa uma nova sessão de chat.
        
        Args:
            user_id: ID único do usuário.
            system_instruction: Instrução de sistema personalizada para o chat.
        """
        self.user_id = user_id
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        
        # Carrega o prompt do arquivo YAML se não foi fornecido
        if system_instruction is None:
            system_instruction = load_prompt_template()
        
        # Fallback para instrução padrão se o carregamento falhar
        if system_instruction is None:
            system_instruction = (
                "Você é um atendente comercial da CryptoLock, vendedor de soluções de segurança de pipeline CI/CD. "
                "Mantenha as respostas profissionais, informativas e focadas nos benefícios do produto. "
                "Responda no idioma do usuário (Português ou Inglês)."
            )
        
        self.chat = self.client.chats.create(
            model=Config.GEMINI_MODEL,
            config={"system_instruction": system_instruction}
        )
        
        print(f"[INFO] Sessão Gemini criada para {user_id} com prompt CryptoLock")
    
    def send_message(self, message: str) -> str:
        """
        Envia uma mensagem para o Gemini e retorna a resposta.
        
        Args:
            message: Conteúdo da mensagem do usuário.
            
        Returns:
            str: Resposta do Gemini AI.
            
        Raises:
            Exception: Se houver erro na comunicação com a API.
        """
        try:
            response = self.chat.send_message(message)
            return response.text or ""
        except Exception as e:
            print(f"[ERROR] Erro ao comunicar com Gemini para usuário {self.user_id}: {e}")
            raise


class ChatSessionManager:
    """Gerencia múltiplas sessões de chat de diferentes usuários."""
    
    def __init__(self):
        """Inicializa o gerenciador de sessões."""
        self.sessions: dict[str, GeminiChatSession] = {}
    
    def get_or_create_session(self, user_id: str, system_instruction: Optional[str] = None) -> GeminiChatSession:
        """
        Obtém uma sessão existente ou cria uma nova para o usuário.
        
        Args:
            user_id: ID único do usuário.
            system_instruction: Instrução de sistema personalizada (usado na criação).
            
        Returns:
            GeminiChatSession: Sessão de chat do usuário.
        """
        if user_id not in self.sessions:
            self.sessions[user_id] = GeminiChatSession(user_id, system_instruction)
            print(f"[INFO] Nova sessão de chat criada para usuário {user_id}")
        
        return self.sessions[user_id]
    
    def get_session(self, user_id: str) -> Optional[GeminiChatSession]:
        """
        Obtém uma sessão existente sem criar uma nova.
        
        Args:
            user_id: ID único do usuário.
            
        Returns:
            GeminiChatSession ou None: Sessão se existir, None caso contrário.
        """
        return self.sessions.get(user_id)
    
    def delete_session(self, user_id: str) -> bool:
        """
        Deleta uma sessão de chat.
        
        Args:
            user_id: ID único do usuário.
            
        Returns:
            bool: True se deletada, False se não existia.
        """
        if user_id in self.sessions:
            del self.sessions[user_id]
            print(f"[INFO] Sessão de chat deletada para usuário {user_id}")
            return True
        return False
    
    def clear_all_sessions(self):
        """Limpa todas as sessões de chat."""
        self.sessions.clear()
        print("[INFO] Todas as sessões de chat foram limpas")
