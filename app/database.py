import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Deals cache / catalog table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deals (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        brand TEXT NOT NULL,
        store TEXT NOT NULL,
        category TEXT NOT NULL,
        gender TEXT DEFAULT 'Unisex',
        original_price REAL NOT NULL,
        discount_price REAL NOT NULL,
        discount_pct INTEGER NOT NULL,
        currency TEXT DEFAULT '$',
        url TEXT NOT NULL,
        image_url TEXT,
        coupon_code TEXT DEFAULT '',
        sizes TEXT DEFAULT 'S, M, L, XL',
        rating REAL DEFAULT 4.5,
        badge TEXT DEFAULT '',
        in_stock INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    );
    """)

    # Watchlist / Saved deals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deal_id TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        brand TEXT NOT NULL,
        store TEXT NOT NULL,
        original_price REAL NOT NULL,
        discount_price REAL NOT NULL,
        target_price REAL,
        url TEXT NOT NULL,
        image_url TEXT,
        coupon_code TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # Model switch audit logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_switch_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        from_model TEXT NOT NULL,
        to_model TEXT NOT NULL,
        trigger_reason TEXT NOT NULL,
        api_key_masked TEXT DEFAULT '',
        success INTEGER DEFAULT 1
    );
    """)

    # Search history & Chat telemetry table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        model_used TEXT NOT NULL,
        latency_ms INTEGER NOT NULL,
        results_count INTEGER NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

def log_model_switch(from_model: str, to_model: str, trigger_reason: str, api_key_masked: str = "", success: bool = True):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO model_switch_logs (timestamp, from_model, to_model, trigger_reason, api_key_masked, success)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        from_model,
        to_model,
        trigger_reason,
        api_key_masked,
        1 if success else 0
    ))
    conn.commit()
    conn.close()

def get_model_switch_logs(limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM model_switch_logs ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def log_search(query: str, model_used: str, latency_ms: int, results_count: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO search_history (query, model_used, latency_ms, results_count, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        query,
        model_used,
        latency_ms,
        results_count,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def get_search_history(limit: int = 15) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM search_history ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_deal(deal: Dict[str, Any]):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO deals 
        (id, title, brand, store, category, gender, original_price, discount_price, discount_pct, currency, url, image_url, coupon_code, sizes, rating, badge, in_stock, created_at)
        VALUES (:id, :title, :brand, :store, :category, :gender, :original_price, :discount_price, :discount_pct, :currency, :url, :image_url, :coupon_code, :sizes, :rating, :badge, :in_stock, :created_at)
    """, deal)
    conn.commit()
    conn.close()

def save_deals_bulk(deals: List[Dict[str, Any]]):
    conn = get_db()
    cursor = conn.cursor()
    for deal in deals:
        cursor.execute("""
            INSERT OR REPLACE INTO deals 
            (id, title, brand, store, category, gender, original_price, discount_price, discount_pct, currency, url, image_url, coupon_code, sizes, rating, badge, in_stock, created_at)
            VALUES (:id, :title, :brand, :store, :category, :gender, :original_price, :discount_price, :discount_pct, :currency, :url, :image_url, :coupon_code, :sizes, :rating, :badge, :in_stock, :created_at)
        """, deal)
    conn.commit()
    conn.close()

def query_deals(
    query: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    store: Optional[str] = None,
    min_discount: Optional[int] = None,
    max_price: Optional[float] = None,
    gender: Optional[str] = None,
    sort_by: str = "discount_pct",
    limit: int = 50
) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM deals WHERE 1=1"
    params = []
    
    if query and isinstance(query, str):
        words = query.strip().split()
        for w in words:
            sql += " AND (title LIKE ? OR brand LIKE ? OR category LIKE ? OR store LIKE ?)"
            pat = f"%{w}%"
            params.extend([pat, pat, pat, pat])
            
    if category and category.lower() != "all":
        sql += " AND LOWER(category) = LOWER(?)"
        params.append(category)
        
    if brand and brand.lower() != "all":
        sql += " AND LOWER(brand) = LOWER(?)"
        params.append(brand)
        
    if store and store.lower() != "all":
        sql += " AND LOWER(store) = LOWER(?)"
        params.append(store)
        
    if min_discount:
        sql += " AND discount_pct >= ?"
        params.append(min_discount)
        
    if max_price:
        sql += " AND discount_price <= ?"
        params.append(max_price)
        
    if gender and gender.lower() != "all":
        sql += " AND (LOWER(gender) = LOWER(?) OR LOWER(gender) = 'unisex')"
        params.append(gender)
        
    # Sort order
    if sort_by == "price_asc":
        sql += " ORDER BY discount_price ASC"
    elif sort_by == "price_desc":
        sql += " ORDER BY discount_price DESC"
    elif sort_by == "rating":
        sql += " ORDER BY rating DESC"
    else: # default: discount_pct
        sql += " ORDER BY discount_pct DESC"
        
    sql += " LIMIT ?"
    params.append(limit)
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_deal_by_id(deal_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deals WHERE id = ?", (deal_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Watchlist helpers
def add_to_watchlist(deal: Dict[str, Any], target_price: Optional[float] = None) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO watchlist (deal_id, title, brand, store, original_price, discount_price, target_price, url, image_url, coupon_code, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            deal["id"],
            deal["title"],
            deal["brand"],
            deal["store"],
            deal["original_price"],
            deal["discount_price"],
            target_price or (deal["discount_price"] * 0.9), # default target 10% lower
            deal["url"],
            deal.get("image_url", ""),
            deal.get("coupon_code", ""),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding to watchlist: {e}")
        return False
    finally:
        conn.close()

def remove_from_watchlist(deal_id: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM watchlist WHERE deal_id = ?", (deal_id,))
    conn.commit()
    conn.close()
    return True

def get_watchlist() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM watchlist ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Analytics Aggregations
def get_dashboard_stats() -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    
    # Total deals
    cursor.execute("SELECT COUNT(*), AVG(discount_pct), AVG(discount_price) FROM deals")
    row = cursor.fetchone()
    total_deals = row[0] or 0
    avg_discount = round(row[1] or 0, 1)
    avg_price = round(row[2] or 0, 2)
    
    # Total Watchlist items & Total Savings
    cursor.execute("SELECT COUNT(*), SUM(original_price - discount_price) FROM watchlist")
    w_row = cursor.fetchone()
    watchlist_count = w_row[0] or 0
    total_saved = round(w_row[1] or 0, 2)
    
    # Category Distribution & Average Discount
    cursor.execute("""
        SELECT category, COUNT(*) as count, ROUND(AVG(discount_pct), 1) as avg_disc, ROUND(MIN(discount_price), 2) as min_price
        FROM deals
        GROUP BY category
        ORDER BY count DESC
    """)
    category_stats = [dict(r) for r in cursor.fetchall()]
    
    # Store Distribution
    cursor.execute("""
        SELECT store, COUNT(*) as count, ROUND(AVG(discount_pct), 1) as avg_disc
        FROM deals
        GROUP BY store
        ORDER BY count DESC
        LIMIT 8
    """)
    store_stats = [dict(r) for r in cursor.fetchall()]
    
    # Top 5 Steal Deals
    cursor.execute("""
        SELECT * FROM deals ORDER BY discount_pct DESC LIMIT 5
    """)
    top_steals = [dict(r) for r in cursor.fetchall()]
    
    # Model switch count
    cursor.execute("SELECT COUNT(*) FROM model_switch_logs")
    total_switches = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "total_deals": total_deals,
        "avg_discount": avg_discount,
        "avg_price": avg_price,
        "watchlist_count": watchlist_count,
        "total_saved": total_saved,
        "category_stats": category_stats,
        "store_stats": store_stats,
        "top_steals": top_steals,
        "total_switches": total_switches
    }
