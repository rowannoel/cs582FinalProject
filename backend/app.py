from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import datetime

app = Flask(__name__)
CORS(app)

print(">>> RUNNING NEW APP.PY <<<")

# ---------------------------
# DATABASE CONFIG
# ---------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "(I am hiding my password)",   # <--- replace with your real password
    "database": "shoplite"
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ---------------------------
# GET PRODUCTS
# ---------------------------
@app.get("/api/products")
def api_products():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM products;")
    rows = cur.fetchall()
    conn.close()
    return jsonify(rows)


# ---------------------------
# GET ORDER DETAILS
# ---------------------------
@app.get("/api/order/<int:order_id>")
def api_get_order(order_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Get order
    cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = cur.fetchone()
    if not order:
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    # Get items
    cur.execute("""
        SELECT oi.*, p.name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE order_id = %s
    """, (order_id,))
    items = cur.fetchall()

    conn.close()
    return jsonify({"order": order, "items": items})


# ---------------------------
# CREATE ORDER
# ---------------------------
@app.post("/api/order")
def api_create_order():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    customer = data.get("customer", {})
    items = data.get("items", [])

    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    conn = get_db()
    cur = conn.cursor()

    try:
        # Insert placeholder order
        cur.execute("""
            INSERT INTO orders
            (customer_name, customer_email, customer_address,
             customer_city, customer_state, customer_zip, total_amount)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            customer.get("name"),
            customer.get("email"),
            customer.get("address"),
            customer.get("city"),
            customer.get("state"),
            customer.get("zip"),
            0.0
        ))

        order_id = cur.lastrowid
        total_amount = 0.0

        # Insert each item
        for item in items:
            pid = int(item["product_id"])
            qty = int(item["quantity"])
            price = float(item["price"])
            line_total = qty * price
            total_amount += line_total

            cur.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
                VALUES (%s,%s,%s,%s,%s)
            """, (order_id, pid, qty, price, line_total))

            # Update stock
            cur.execute("""
                UPDATE products
                SET stock_quantity = stock_quantity - %s
                WHERE id = %s
            """, (qty, pid))

        # Update final total
        cur.execute("""
            UPDATE orders SET total_amount = %s WHERE id = %s
        """, (total_amount, order_id))

        conn.commit()

        return jsonify({"order_id": order_id})

    except Exception as e:

        print(">>> MYSQL ERROR:", e)

        conn.rollback()

        return jsonify({"error": "TEST ERROR CATCH"}), 500


    finally:
        conn.close()


# ---------------------------
# DAILY SALES REPORT
# ---------------------------
@app.get("/api/reports/daily")
def api_daily_report():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            DATE(created_at) AS sale_date,
            SUM(total_amount) AS total_revenue,
            COUNT(*) AS order_count
        FROM orders
        GROUP BY DATE(created_at)
        ORDER BY sale_date DESC;
    """)

    rows = cur.fetchall()
    conn.close()
    return jsonify(rows)


# ---------------------------
# LOW STOCK REPORT
# ---------------------------
@app.get("/api/reports/low-stock")
def api_low_stock():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT * FROM products
        WHERE stock_quantity <= reorder_level
        ORDER BY stock_quantity ASC;
    """)

    rows = cur.fetchall()
    conn.close()
    return jsonify(rows)


# ---------------------------
# START FLASK SERVER
# ---------------------------
if __name__ == "__main__":
    print("Starting backend server on http://127.0.0.1:5000")
    app.run(debug=True)

