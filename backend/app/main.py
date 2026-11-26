from fastapi import FastAPI
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.agent.sql_agent import answer_sync
from app.db import engine

app = FastAPI(title='Lakehouse AI Assistant')


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


@app.get('/health')
def health():
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    return {'status': 'ok'}


@app.post('/ask/sync')
def ask_sync(request: AskRequest):
    return answer_sync(request.question)

