from datetime import datetime
import psycopg
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def add_check(url_id):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO url_checks ' \
            '(url_id, created_at) VALUES (%s, %s) RETURNING id',
                (url_id, datetime.now())
            )
            check_id = cur.fetchone()[0]
            conn.commit()
            return check_id


def get_checks_by_url_id(url_id):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id, status_code, h1, title, description, created_at ' \
                'FROM url_checks WHERE url_id = %s ' \
                'ORDER BY created_at DESC',
                (url_id,)
            )
            return cur.fetchall()


def get_last_check_date(url_id):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT created_at FROM url_checks ' \
                'WHERE url_id = %s ORDER BY created_at DESC LIMIT 1',
                (url_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None