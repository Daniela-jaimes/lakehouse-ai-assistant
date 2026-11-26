import pytest

from app.agent.safety import validate_and_limit

MAX_ROWS = 1000


# --- Statements that must be rejected -------------------------------------

@pytest.mark.parametrize('sql', [
    'DROP TABLE fact_sales',
    'dRoP table fact_sales',
    'DELETE FROM fact_sales',
    'UPDATE fact_sales SET quantity = 0',
    "INSERT INTO dim_store VALUES (1, 1, 'x')",
    'TRUNCATE fact_sales',
    'CREATE TABLE x (a int)',
    'COPY fact_sales TO STDOUT',
    'SET ROLE neondb_owner',
    'WITH t AS (DELETE FROM fact_sales RETURNING *) SELECT * FROM t',
])
def test_rejects_non_select(sql):
    with pytest.raises(ValueError):
        validate_and_limit(sql, MAX_ROWS)


@pytest.mark.parametrize('sql', [
    'SELECT 1; DROP TABLE fact_sales',
    'SELECT * FROM dim_store; SELECT * FROM dim_date',
    '',
])
def test_rejects_multiple_or_empty_statements(sql):
    with pytest.raises(ValueError):
        validate_and_limit(sql, MAX_ROWS)


@pytest.mark.parametrize('sql', [
    'SELECT * FROM pg_user',
    'SELECT * FROM pg_catalog.pg_user',
    'SELECT * FROM information_schema.tables',
    'SELECT * FROM rag.knowledge',
    'SELECT * FROM (SELECT * FROM pg_shadow) AS q',
    'SELECT 1 UNION SELECT usename FROM pg_user',
    'SELECT * INTO new_table FROM fact_sales',
])
def test_rejects_tables_outside_gold(sql):
    with pytest.raises(ValueError):
        validate_and_limit(sql, MAX_ROWS)


@pytest.mark.parametrize('sql', [
    'SELECT pg_sleep(10)',
    'SELECT pg_sleep(10) FROM fact_sales',
    "SELECT pg_read_file('/etc/passwd')",
    "SELECT lo_import('/etc/passwd')",
])
def test_rejects_dangerous_functions(sql):
    with pytest.raises(ValueError):
        validate_and_limit(sql, MAX_ROWS)


# --- Statements that must be accepted --------------------------------------

def test_valid_select_gets_a_limit():
    result = validate_and_limit('SELECT count(*) FROM fact_sales', MAX_ROWS)
    assert result == 'SELECT * FROM (SELECT count(*) FROM fact_sales) AS q LIMIT 1000'


def test_trailing_semicolon_is_removed():
    result = validate_and_limit('SELECT count(*) FROM fact_sales;', MAX_ROWS)
    assert ';' not in result
    assert result.endswith('LIMIT 1000')


def test_limit_uses_the_given_max_rows():
    result = validate_and_limit('SELECT * FROM dim_store', 50)
    assert result.endswith('LIMIT 50')


def test_accepts_join_over_gold_tables():
    sql = ('SELECT p.category, SUM(f.net_amount) FROM fact_sales f '
           'JOIN dim_product p USING (product_key) GROUP BY 1')
    assert validate_and_limit(sql, MAX_ROWS).endswith('LIMIT 1000')


def test_accepts_schema_qualified_gold_table():
    assert validate_and_limit('SELECT count(*) FROM gold.fact_sales', MAX_ROWS)


def test_accepts_the_mart():
    sql = 'SELECT department, SUM(net_sales) FROM agg_sales_dept_age_quarter GROUP BY 1'
    assert validate_and_limit(sql, MAX_ROWS)


def test_accepts_cte_over_gold_tables():
    sql = ('WITH t AS (SELECT * FROM fact_sales) '
           'SELECT count(*) FROM t')
    assert validate_and_limit(sql, MAX_ROWS)


def test_accepts_union_over_gold_tables():
    sql = 'SELECT store_name FROM dim_store UNION SELECT product_name FROM dim_product'
    assert validate_and_limit(sql, MAX_ROWS)


# --- Known gaps (documented, still contained by the read-only role) --------

def test_line_comment_does_not_break_the_wrapper():
    result = validate_and_limit('SELECT 1 -- note', MAX_ROWS)
    assert '-- note' not in result


@pytest.mark.xfail(reason='FOR UPDATE passes the validator; agent_ro (read-only) blocks it')
def test_rejects_row_locking():
    with pytest.raises(ValueError):
        validate_and_limit('SELECT * FROM dim_store FOR UPDATE', MAX_ROWS)


def test_valid_select_gets_a_limit():
    result = validate_and_limit('SELECT count(*) FROM fact_sales', MAX_ROWS)
    assert result.lower() == 'select * from (select count(*) from fact_sales) as q limit 1000'