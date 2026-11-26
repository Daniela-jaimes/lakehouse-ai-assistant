import os

import psycopg

conn = psycopg.connect(os.environ['DATABASE_URL_RO'])
cur = conn.cursor()

cur.execute('SELECT count(*) FROM gold.fact_sales')
print('SELECT ok:', cur.fetchone())

for sql in ['DELETE FROM gold.dim_store', 'CREATE TABLE gold.x (a int)']:
    try:
        cur.execute(sql)
        print('PELIGRO, se ejecuto:', sql)
    except Exception as error:
        print('BLOQUEADO:', sql, '->', type(error).__name__)
        conn.rollback()