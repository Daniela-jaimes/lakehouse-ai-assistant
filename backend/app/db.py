from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

from app.config import settings

GOLD_TABLES = [
    'fact_sales',
    'dim_date',
    'dim_customer',
    'dim_product',
    'dim_store',
    'dim_geography',
    'agg_sales_dept_age_quarter',
]

engine = create_engine(
    settings.database_url_ro,
    pool_pre_ping=True,
    pool_size=3,
    max_overflow=2,
)

db = SQLDatabase(
    engine,
    schema='gold',
    include_tables=GOLD_TABLES,
    sample_rows_in_table_info=2,
)
