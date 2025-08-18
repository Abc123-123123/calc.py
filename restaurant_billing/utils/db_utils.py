import sqlite3
from pathlib import Path
import csv
from datetime import datetime
from typing import List, Tuple

# Database file path (relative to project)
BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "db" / "restaurant.db"
MENU_CSV = BASE_DIR / "data" / "menu.csv"

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Create tables if they don't exist"""
    with get_conn() as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT,
                price REAL NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                subtotal REAL NOT NULL,
                gst_amount REAL NOT NULL,
                discount REAL NOT NULL,
                total REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                qty INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                line_total REAL NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id)
            )
        """)
        con.commit()

def bootstrap_menu_from_csv():
    """Load menu.csv into DB if menu table is empty"""
    if not MENU_CSV.exists():
        return
    with get_conn() as con:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM menu")
        cnt = cur.fetchone()[0]
        if cnt > 0:
            return
        with open(MENU_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = []
            for r in reader:
                try:
                    name = r['name'].strip()
                    category = r.get('category','').strip()
                    price = float(r['price'])
                    rows.append((name, category, price))
                except Exception:
                    continue
        cur.executemany("INSERT OR IGNORE INTO menu(name, category, price) VALUES(?,?,?)", rows)
        con.commit()

def fetch_menu() -> List[Tuple[int, str, str, float]]:
    """Return list of (id, name, category, price)"""
    with get_conn() as con:
        cur = con.cursor()
        cur.execute("SELECT id, name, category, price FROM menu ORDER BY name")
        return cur.fetchall()

def save_order(mode: str, payment: str, items: List[Tuple[str,int,float,float]],
               subtotal: float, gst_amount: float, discount: float, total: float) -> int:
    """
    items: list of tuples (item_name, qty, unit_price, line_total)
    returns order_id
    """
    with get_conn() as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO orders(mode, payment_method, subtotal, gst_amount, discount, total, created_at)
            VALUES (?,?,?,?,?,?,?)
        """, (mode, payment, subtotal, gst_amount, discount, total, datetime.now().isoformat(timespec='seconds')))
        order_id = cur.lastrowid
        cur.executemany("""
            INSERT INTO order_items(order_id, item_name, qty, unit_price, line_total)
            VALUES (?,?,?,?,?)
        """, [(order_id, n, q, p, lt) for (n,q,p,lt) in items])
        con.commit()
        return order_id

def sales_report(period: str = "daily"):
    """
    period: 'daily', 'weekly', 'monthly'
    returns list of tuples (period_key, total_sales, total_orders)
    """
    with get_conn() as con:
        cur = con.cursor()
        if period == "daily":
            key = "substr(created_at,1,10)"
        elif period == "weekly":
            key = "strftime('%Y-W%W', created_at)"
        else:
            key = "substr(created_at,1,7)"
        cur.execute(f"""
            SELECT {key} as k, SUM(total) as total_sales, COUNT(*) as total_orders
            FROM orders
            GROUP BY k
            ORDER BY k
        """)
        return cur.fetchall()