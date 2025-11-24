from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from datetime import datetime

app = Flask(__name__)
CORS(app)  # allow GitHub Pages → localhost

# -----------------------------------------------------------
#  CONFIG: MySQL credentials (EDIT THESE!)
# -----------------------------------------------------------

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_PASSWORD",
    "database": "shoplite"
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# -----------------------------------------------------------
#  PRODUCTS API
# -----------------------------------------------------------

@app.route("/api/products", methods=["GET"])
def api_products():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE %s OR description LIKE %s)"
        like = f"%{search}%"
        params.extend([like, like])

    if category:
        query += " AND category = %s"
        params.append(category)

    cur.execute(query, params)
    products = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(products)


@app.route("/api/products/<int:product_id>", methods=["GET"])
def api_single_product(product_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    cur.close()
    conn.close()

    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(product)


# -----------------------------------------------------------
#  ORDERS API
# -----------------------------------------------------------

@app.route("/api/order", methods=["POST"])
def api_create_order():
    data = request.get_json()

    customer = data.get("customer", {})
    items = data.get("items", [])

    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    if not customer.get("name"):
        return jsonify({"error": "Missing customer name"}), 400

    conn = get_db()
    cur = conn.cursor()

    # create order (placeholder total)
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

    # Insert line items
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

        # decrease stock
        cur.execute("""
            UPDATE products
            SET stock_quantity = stock_quantity - %s
            WHERE id = %s
        """, (qty, pid))

    # update final total
    cur.execute("""
        UPDATE orders SET total_amount = %s WHERE id = %s
    """, (total_amount, order_id))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"order_id": order_id})


@app.route("/api/order/<int:order_id>", methods=["GET"])
def api_get_order(order_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    order = cur.fetchone()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    cur.execute("""
        SELECT oi.*, p.name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = %s
    """, (order_id,))
    items = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({"order": order, "items": items})


# -----------------------------------------------------------
#  REPORTS API
# -----------------------------------------------------------

@app.route("/api/reports/top-products", methods=["GET"])
def api_top_products():
    days = int(request.args.get("days", 30))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT p.id, p.name, SUM(oi.line_total) AS revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN products p ON oi.product_id = p.id
        WHERE o.created_at >= NOW() - INTERVAL %s DAY
        GROUP BY p.id, p.name
        ORDER BY revenue DESC
    """, (days,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(rows)


@app.route("/api/reports/daily-sales", methods=["GET"])
def api_daily_sales():
    days = int(request.args.get("days", 90))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT DATE(created_at) AS sale_date,
               SUM(total_amount) AS total_revenue,
               COUNT(*) AS total_orders
        FROM orders
        WHERE created_at >= NOW() - INTERVAL %s DAY
        GROUP BY DATE(created_at)
        ORDER BY sale_date
    """, (days,))

    rows = cur.fetchall()

    # compute simple moving average (7-day)
    revenues = [float(r["total_revenue"]) for r in rows]
    dates = [r["sale_date"].isoformat() for r in rows]

    moving_avg = []
    for i in range(len(revenues)):
        window = revenues[max(0, i - 6):i + 1]
        moving_avg.append(sum(window) / len(window))

    cur.close()
    conn.close()

    return jsonify({
        "dates": dates,
        "revenues": revenues,
        "moving_avg": moving_avg
    })


@app.route("/api/reports/low-stock", methods=["GET"])
def api_low_stock():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT * FROM products
        WHERE stock_quantity <= reorder_level
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(rows)


# -----------------------------------------------------------
#  DATA TOOLS API
# -----------------------------------------------------------

@app.route("/api/tools/recompute-order-totals", methods=["POST"])
def api_recompute_totals():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id FROM orders")
    all_ids = [row[0] for row in cur.fetchall()]

    for oid in all_ids:
        cur.execute("""
            SELECT SUM(line_total) FROM order_items WHERE order_id = %s
        """, (oid,))
        total = cur.fetchone()[0] or 0.0

        cur.execute("""
            UPDATE orders SET total_amount = %s WHERE id = %s
        """, (total, oid))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Order totals recomputed."})


@app.route("/api/tools/refresh-90day-summary", methods=["POST"])
def api_refresh_summary():
    conn = get_db()
    cur = conn.cursor()

    # remove recent summary
    cur.execute("""
        DELETE FROM daily_sales_summary
        WHERE sale_date >= CURDATE() - INTERVAL 90 DAY
    """)

    # recompute
    cur.execute("""
        INSERT INTO daily_sales_summary (sale_date, total_revenue, total_orders)
        SELECT DATE(created_at),
               SUM(total_amount),
               COUNT(*)
        FROM orders
        WHERE created_at >= NOW() - INTERVAL 90 DAY
        GROUP BY DATE(created_at)
    """)

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "90-day summary refreshed."})


# -----------------------------------------------------------
#  RUN SERVER
# -----------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
