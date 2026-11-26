
from dataclasses import dataclass

import pandas as pd
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import text

from app.agent.safety import validate_and_limit
from app.config import settings
from app.context.builder import build_system_prompt
from app.db import db, engine
from app.llm import get_llm


@dataclass
class ResultStore:
    sql: str | None = None
    df: pd.DataFrame | None = None


def text_of(message) -> str:
    """Extrae el contenido de un mensaje del agente."""

    content = message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )

    return str(content)


def build_agent(store: ResultStore, system_prompt: str):
    """Construye el agente de consultas SQL."""

    llm = get_llm()

    # Herramientas del toolkit, excluyendo la consulta SQL original.
    base_tools = [
        tool_item
        for tool_item in SQLDatabaseToolkit(
            db=db,
            llm=llm
        ).get_tools()
        if tool_item.name != "sql_db_query"
    ]

    @tool
    def sql_db_query(query: str) -> str:
        """
        Ejecuta una única consulta SELECT de solo lectura
        sobre el modelo Gold del Lakehouse.
        """

        try:
            safe_query = validate_and_limit(
                query,
                settings.max_rows
            )

            with engine.connect() as connection:
                df = pd.read_sql(
                    text(safe_query),
                    connection
                )

            store.sql = safe_query
            store.df = df

            if df.empty:
                return "La consulta se ejecutó correctamente, pero no devolvió resultados."

            return (
                df.head(20).to_markdown(index=False)
                + f"\n({len(df)} filas obtenidas)"
            )

        except Exception as error:
            return f"Error al ejecutar la consulta SQL: {error}"

    return create_agent(
        model=llm,
        tools=[*base_tools, sql_db_query],
        system_prompt=system_prompt
    )


def answer_sync(question: str) -> dict:
    """Procesa una pregunta y devuelve SQL, datos y respuesta."""

    store = ResultStore()

    agent = build_agent(
        store,
        build_system_prompt()
    )

    try:
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            },
            config={
                "recursion_limit": 12
            }
        )

        messages = result.get("messages", [])

        answer = (
            text_of(messages[-1])
            if messages
            else "El agente no generó una respuesta."
        )

        return {
            "question": question,
            "sql": store.sql,
            "columns": (
                []
                if store.df is None
                else list(store.df.columns)
            ),
            "rows": (
                []
                if store.df is None
                else store.df.head(50).to_dict("records")
            ),
            "answer": answer,
        }

    except Exception as error:
        return {
            "question": question,
            "sql": store.sql,
            "columns": [],
            "rows": [],
            "answer": f"Error al procesar la pregunta: {error}",
        }
