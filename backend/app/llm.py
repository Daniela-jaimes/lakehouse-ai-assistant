
from langchain.chat_models import init_chat_model
from langchain_core.rate_limiters import InMemoryRateLimiter

from app.config import settings


_limiter = InMemoryRateLimiter(
    requests_per_second=settings.llm_rpm / 60,
    max_bucket_size=2,
)


def get_llm(temperature: float = 0):
    """Inicializa el modelo LLM con límite de solicitudes y API Key."""

    kwargs = {}

    if settings.llm_model.startswith('google_genai:'):
        kwargs['google_api_key'] = settings.google_api_key

    elif settings.llm_model.startswith('groq:'):
        kwargs['api_key'] = settings.groq_api_key

    return init_chat_model(
        settings.llm_model,
        temperature=temperature,
        rate_limiter=_limiter,
        **kwargs,
    )
