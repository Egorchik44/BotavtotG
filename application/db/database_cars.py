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


async def add_car(user_id, make, model, year, mileage, price, place, description):
    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO cars (user_id, make, model, year, mileage, price, place, description, status, admin_status, message_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active', 'pending', 0)
            RETURNING id
        """, (user_id, make, model, year, mileage, price, place, description))
        return cursor.fetchone()[0]

async def update_ad_status(car_id, status=None, admin_status=None):
    with get_cursor() as cursor:
        if status and admin_status:
            cursor.execute("""
                UPDATE cars SET status = %s, admin_status = %s WHERE id = %s
            """, (status, admin_status, car_id))
        elif status:
            cursor.execute("""
                UPDATE cars SET status = %s WHERE id = %s
            """, (status, car_id))
        elif admin_status:
            cursor.execute("""
                UPDATE cars SET admin_status = %s WHERE id = %s
            """, (admin_status, car_id))

async def get_ad_status(car_id):
    with get_cursor() as cursor:
        cursor.execute('SELECT status, admin_status FROM cars WHERE id = %s', (car_id,))
        return cursor.fetchone()

async def add_car_photo(car_id, photo_path):
    with get_cursor() as cursor:
        cursor.execute('INSERT INTO car_photos (car_id, photo_path) VALUES (%s, %s)', (car_id, photo_path))

async def get_car_info(car_id):
    with get_cursor() as cursor:
        cursor.execute('SELECT user_id, make, model, year, mileage, price, place, description, status, admin_status, message_id FROM cars WHERE id = %s', (car_id,))
        car_info = cursor.fetchone()
        cursor.execute('SELECT photo_path FROM car_photos WHERE car_id = %s', (car_id,))
        photos = cursor.fetchall()
        
        return car_info, photos

async def update_message_id(car_id, message_id):
    with get_cursor() as cursor:
        cursor.execute('UPDATE cars SET message_id = %s WHERE id = %s', (message_id, car_id))

async def get_message_id(car_id):
    with get_cursor() as cursor:
        cursor.execute('SELECT message_id FROM cars WHERE id = %s', (car_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None

async def get_media_count(car_id):
    with get_cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM car_photos WHERE car_id = %s', (car_id,))
        return cursor.fetchone()[0]

def close_connections():
    conn.close()



