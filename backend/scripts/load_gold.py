import glob
import io
import os

import pandas as pd
import psycopg
import pyarrow.parquet as pq

TABLES = ['dim_date', 'dim_customer', 'dim_product',
          'dim_store', 'dim_geography', 'fact_sales']


def load(conn, table):
    files = sorted(glob.glob(f'data/export/{table}/*'))
    if not files:
        raise SystemExit(f'No files found in data/export/{table}. Run from the repo root.')
    total = 0
    with conn.cursor() as cur:
        cur.execute(f'TRUNCATE gold.{table}')
        with cur.copy(f'COPY gold.{table} FROM STDIN WITH (FORMAT csv)') as copy:
            for path in files:
                parquet = pq.ParquetFile(path)
                for batch in parquet.iter_batches(batch_size=200_000):
                    buffer = io.StringIO()
                    batch.to_pandas(types_mapper=pd.ArrowDtype).to_csv(
                        buffer, index=False, header=False)
                    copy.write(buffer.getvalue())
                    total += batch.num_rows
    conn.commit()
    print(f'[LOAD] {table} done: {total} rows', flush=True)


if __name__ == '__main__':
    with psycopg.connect(os.environ['DATABASE_URL_OWNER']) as conn:
        for table in TABLES:
            load(conn, table)