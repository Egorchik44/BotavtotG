import os
import logging
import psycopg2
from contextlib import contextmanager

conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT')
)

@contextmanager
def get_cursor():
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        logging.error(f"Database error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        


async def add_user(user_id: int, username: str):
    with get_cursor() as cursor:
        cursor.execute(
            'INSERT INTO users (user_id, username, num_ads, status) VALUES (%s, %s, 0, %s) ON CONFLICT (user_id) DO NOTHING',
            (user_id, username, 'user')
        )

async def get_user_info(user_id: int):
    with get_cursor() as cursor:
        cursor.execute('SELECT user_id, username, num_ads, status FROM users WHERE user_id = %s', (user_id,))
        return cursor.fetchone()

async def get_user_status(user_id: int):
    with get_cursor() as cursor:
        cursor.execute('SELECT status FROM users WHERE user_id = %s', (user_id,))
        user_status = cursor.fetchone()
        if user_status:
            return user_status[0]
        return 'unknown'

async def update_user_ads_count(user_id: int):
    with get_cursor() as cursor:
        cursor.execute('UPDATE users SET num_ads = num_ads + 1 WHERE user_id = %s', (user_id,))

async def update_user_status(user_id: int, status: str):
    with get_cursor() as cursor:
        cursor.execute('UPDATE users SET status = %s WHERE user_id = %s', (status, user_id))

async def get_admins():
    with get_cursor() as cursor:
        cursor.execute("SELECT user_id FROM users WHERE status = 'admin'")
        admins = cursor.fetchall()
        return [admin[0] for admin in admins]

async def get_username_by_user_id(user_id: int):
    with get_cursor() as cursor:
        cursor.execute('SELECT username FROM users WHERE user_id = %s', (user_id,))
        username = cursor.fetchone()
        if username:
            return username[0]
        return None

async def fetch_user_ad_ids(user_id: int):
    with get_cursor() as cursor:
        cursor.execute('SELECT id FROM cars WHERE user_id = %s AND status = %s', (user_id, 'in_sale'))
        return [ad[0] for ad in cursor.fetchall()]

async def fetch_user_ids():
    with get_cursor() as cursor:
        cursor.execute('SELECT user_id FROM users')
        return cursor.fetchall()

async def update_all_users_status():
    with get_cursor() as cursor:
        cursor.execute('SELECT user_id FROM users')
        user_ids = cursor.fetchall()
        


def close_connections():
    conn.close()


