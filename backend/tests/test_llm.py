
from app.agent.sql_agent import text_of
from app.llm import get_llm


def test_llm_responds():
    """Verifica que el modelo LLM responda correctamente."""

    reply = get_llm(temperature=0).invoke(
        'Responde solo con la palabra: listo'
    )

    response = text_of(reply).lower()

    print(f'\nRespuesta del LLM: {response}')

    assert 'listo' in response
