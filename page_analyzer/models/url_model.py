from datetime import datetime
import psycopg
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def add_url_to_db(normalized_url):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO urls (name, created_at)' \
            'VALUES (%s, %s) RETURNING id',
            (normalized_url, datetime.now()))       
            url_id = cur.fetchone()[0]
            conn.commit()
        return url_id
    

def get_all_urls():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id, name, created_at ' \
                        'FROM urls ORDER BY created_at DESC')
            urls = cur.fetchall()
            return urls
        

def get_url_by_id(url_id):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur: 
            cur.execute('SELECT id, name, created_at ' \
                        'FROM urls WHERE id = %s', (url_id,))
            url = cur.fetchone()
            return url
        

def get_url_by_name(url_name):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur: 
            cur.execute('SELECT id, name, created_at ' \
                        'FROM urls WHERE name = %s', (url_name,))
            url = cur.fetchone()
            return url
        

def url_exists(normalized_url):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM urls WHERE ' \
                        'name = %s', (normalized_url,))
            result = cur.fetchone()
            return result is not None