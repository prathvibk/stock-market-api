# ============================================
# FLASK REST API — Stock Market Dashboard
# ============================================

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)  # Allow React frontend to connect

# Database config
DB_CONFIG = {
    "host": "shortline.proxy.rlwy.net",
    "port": 30612,
    "user": "root",
    "password": "tvxfgRAhoXcSLIwSkGNQLrUNDYHgayNH",
    "database": "railway"
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def query_db(sql):
    conn = get_db()
    df = pd.read_sql(sql, conn)
    conn.close()
    return df.to_dict(orient='records')


# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.route('/')
def home():
    return jsonify({"message": "Stock Market API is running!"})


@app.route('/api/summary')
def summary():
    """All stocks summary"""
    data = query_db("""
        SELECT symbol, company_name, avg_close_price,
               max_price, min_price, avg_daily_return,
               avg_volatility, total_records
        FROM stock_summary
        ORDER BY avg_daily_return DESC
    """)
    return jsonify(data)


@app.route('/api/stock/<symbol>')
def stock_detail(symbol):
    """Get price history for one stock"""
    data = query_db(f"""
        SELECT date, open_price, high_price, low_price,
               close_price, volume, daily_return_pct,
               ma_7, ma_30, volatility_pct
        FROM stock_prices
        WHERE symbol = '{symbol}'
        ORDER BY date ASC
    """)
    return jsonify(data)


@app.route('/api/top-gainers')
def top_gainers():
    """Top performing stocks"""
    data = query_db("""
        SELECT symbol, company_name,
               avg_daily_return, avg_close_price
        FROM stock_summary
        WHERE avg_daily_return > 0
        ORDER BY avg_daily_return DESC
        LIMIT 5
    """)
    return jsonify(data)


@app.route('/api/top-losers')
def top_losers():
    """Worst performing stocks"""
    data = query_db("""
        SELECT symbol, company_name,
               avg_daily_return, avg_close_price
        FROM stock_summary
        WHERE avg_daily_return <= 0
        ORDER BY avg_daily_return ASC
        LIMIT 5
    """)
    return jsonify(data)


@app.route('/api/most-volatile')
def most_volatile():
    """Most volatile stocks"""
    data = query_db("""
        SELECT symbol, company_name, avg_volatility
        FROM stock_summary
        ORDER BY avg_volatility DESC
        LIMIT 5
    """)
    return jsonify(data)


@app.route('/api/monthly/<symbol>')
def monthly(symbol):
    """Monthly performance for a stock"""
    data = query_db(f"""
        SELECT
            DATE_FORMAT(date, '%Y-%m') as month,
            ROUND(AVG(close_price), 2) as avg_price,
            ROUND(AVG(daily_return_pct), 2) as avg_return,
            ROUND(AVG(volatility_pct), 2) as avg_volatility
        FROM stock_prices
        WHERE symbol = '{symbol}'
        GROUP BY month
        ORDER BY month
    """)
    return jsonify(data)


@app.route('/api/best-days')
def best_days():
    """Best trading days"""
    data = query_db("""
        SELECT symbol, date, close_price, daily_return_pct
        FROM stock_prices
        ORDER BY daily_return_pct DESC
        LIMIT 10
    """)
    return jsonify(data)


@app.route('/api/worst-days')
def worst_days():
    """Worst trading days"""
    data = query_db("""
        SELECT symbol, date, close_price, daily_return_pct
        FROM stock_prices
        ORDER BY daily_return_pct ASC
        LIMIT 10
    """)
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)