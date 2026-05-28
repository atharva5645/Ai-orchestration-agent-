from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

def get_gemini_model(model_name: str = "gemini-1.5-flash", temperature: float = 0.2) -> ChatGoogleGenerativeAI:
    """
    Initializes and returns the Gemini Chat Model.
    """
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=settings.google_api_key,
        temperature=temperature
    )
