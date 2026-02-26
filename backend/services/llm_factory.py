from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from config import settings

def get_llm():
    """Returns the LLM instance based on the environment configuration."""
    provider = settings.LLM_PROVIDER.upper()
    
    if provider == "OPENAI":
        return ChatOpenAI(
            model=settings.LLM_MODEL, 
            api_key=settings.OPENAI_API_KEY
        )
    elif provider == "GEMINI":
        return ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL, 
            google_api_key=settings.GEMINI_API_KEY
        )
    elif provider == "OLLAMA":
        return ChatOllama(
            model=settings.LLM_MODEL, 
            base_url=settings.OLLAMA_BASE_URL
        )
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")