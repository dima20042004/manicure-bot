import sqlite3
import datetime

def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                reg_date TEXT,
                orders_count INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER,
                prompt TEXT,
                image_path TEXT,
                status TEXT,
                created_at TEXT
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS moodboards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER,
                image_hash TEXT,
                extracted_colors TEXT,
                created_at TEXT
            )
        ''')
        db.commit()

def add_user(tg_id, username, first_name, last_name):
    with get_db() as db:
        db.execute(
            "INSERT OR IGNORE INTO users (tg_id, username, first_name, last_name, reg_date) VALUES (?, ?, ?, ?, ?)",
            (tg_id, username, first_name, last_name, datetime.datetime.utcnow().isoformat())
        )
        db.commit()

def create_order(tg_id, prompt):
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO orders (tg_id, prompt, status, created_at) VALUES (?, ?, ?, ?)",
            (tg_id, prompt, 'pending', datetime.datetime.utcnow().isoformat())
        )
        db.commit()
        return cur.lastrowid

def update_order_status(order_id, status, image_path=None):
    with get_db() as db:
        if image_path:
            db.execute("UPDATE orders SET status=?, image_path=? WHERE id=?", (status, image_path, order_id))
        else:
            db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        db.commit()

def get_user_orders(tg_id):
    with get_db() as db:
        return db.execute("SELECT * FROM orders WHERE tg_id=? ORDER BY created_at DESC", (tg_id,)).fetchall()