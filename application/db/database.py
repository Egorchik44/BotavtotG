
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def init_db():
    db_params = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
    }

    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE,
        username TEXT,
        status TEXT,
        num_ads INTEGER DEFAULT 0
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cars (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        make TEXT,
        model TEXT,
        year TEXT,
        mileage TEXT,
        price TEXT,
        place TEXT,
        description TEXT,
        status TEXT,
        admin_status TEXT,
        message_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS car_photos (
        id SERIAL PRIMARY KEY,
        car_id INTEGER,
        photo_path TEXT,
        FOREIGN KEY (car_id) REFERENCES cars (id)
    )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    init_db()

