import sqlglot
from sqlglot import exp

ALLOWED_TABLES = {
    'fact_sales',
    'dim_date',
    'dim_customer',
    'dim_product',
    'dim_store',
    'dim_geography',
    'agg_sales_dept_age_quarter'
}

FORBIDDEN = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Create,
    exp.Alter,
    exp.Command,
    exp.Merge
)


def validate_and_limit(sql: str, max_rows: int) -> str:
    """Accept exactly one SELECT over Gold tables and wrap it with a LIMIT."""

    try:
        trees = [
            t for t in sqlglot.parse(sql, read='postgres')
            if t is not None
        ]

    except sqlglot.errors.SqlglotError as error:
        raise ValueError(f'unparseable SQL: {error}')

    if len(trees) != 1:
        raise ValueError('exactly one statement is allowed')

    tree = trees[0]

    if not isinstance(tree, (exp.Select, exp.Union)) or tree.find(*FORBIDDEN):
        raise ValueError('only SELECT is allowed')

    ctes = {
        cte.alias for cte in tree.find_all(exp.CTE)
    }

    for table in tree.find_all(exp.Table):
        if table.name not in ALLOWED_TABLES | ctes:
            raise ValueError(f'table not allowed: {table.name}')

    for func in tree.find_all(exp.Anonymous):
        if func.name.lower().startswith(('pg_', 'dblink', 'lo_')):
            raise ValueError(f'function not allowed: {func.name}')

    if not isinstance(max_rows, int) or not 1 <= max_rows <= 10000:
        raise ValueError('max_rows must be between 1 and 10000')

    return (
        f'SELECT * FROM ({sql.strip().rstrip(";")}) AS q '
        f'LIMIT {max_rows}'
    )
