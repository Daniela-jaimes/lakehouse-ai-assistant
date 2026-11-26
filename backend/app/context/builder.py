from pathlib import Path

from sqlalchemy import text

from app.db import db, engine

CATEGORICAL = [
    ('dim_product', 'category'),
    ('dim_geography', 'department'),
    ('dim_customer', 'age_group'),
    ('fact_sales', 'order_status'),
    ('fact_sales', 'payment_method'),
]


def valid_values() -> str:
    lines = []
    with engine.connect() as conn:
        for table, column in CATEGORICAL:
            query = text(
                f'SELECT DISTINCT {column} FROM gold.{table} '
                f'WHERE {column} IS NOT NULL ORDER BY 1'
            )
            rows = conn.execute(query).scalars().all()
            lines.append(f'- {table}.{column}: {rows}')
        ref_date = conn.execute(
            text('SELECT max(order_date) FROM gold.fact_sales')
        ).scalar()
    return '\n'.join(lines) + f'\n- reference date (today for the data): {ref_date}'


def build_system_prompt(extra: str = '') -> str:
    rules = Path(__file__).with_name('rules.md').read_text(encoding='utf-8')
    return (
        'You are a senior data analyst. Answer in Spanish using ONLY the Gold '
        'model (PostgreSQL).\n'
        'Never invent tables or columns. Write ONE read-only SELECT, run it '
        'with sql_db_query and answer with the exact figures returned. '
        'If the model cannot answer (personal data, costs, margins), '
        'start the reply with SIN_DATOS: and explain why. '
        'Never write INSERT/UPDATE/DELETE/DDL.\n\n'
        f'## Schema\n{db.get_table_info()}\n\n'
        f'## Valid values\n{valid_values()}\n\n'
        f'## Business rules\n{rules}\n{extra}'
    )