from langchain.chat_models import init_chat_model
from langchain_core.rate_limiters import InMemoryRateLimiter
from app.config import settings
_limiter = InMemoryRateLimiter(requests_per_second=settings.llm_rpm / 60,
max_bucket_size=2)
def get_llm(temperature: float = 0):
 return init_chat_model(settings.llm_model, temperature=temperature,
rate_limiter=_limiter)