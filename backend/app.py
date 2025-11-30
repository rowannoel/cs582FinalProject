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
    "password": "(hiding my password)",   # <--- replace with your real password
    "database": "shoplite"
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ---------------------------
# GET PRODUCTS
# ---------------------------
@app.get("/api/products")
def api_products():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search:
        query += " AND name LIKE %s"
        params.append(f"%{search}%")

    if category:
        query += " AND category = %s"
        params.append(category)

    query += " ORDER BY name ASC"

    cur.execute(query, tuple(params))
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
    print(">>> ORDER ROUTE HIT <<<")
    data = request.get_json()
    print(">>> RECEIVED DATA:", data)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    customer = data.get("customer", {})
    items = data.get("items", [])
    print(">>> CUSTOMER:", customer)
    print(">>> ITEMS:", items)

    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    try:
        # Insert placeholder order
        print(">>> ABOUT TO INSERT ORDER")
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
            print(">>> ITEM:", item)
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

        print(">>> ORDER COMMITTING")
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

@app.get("/api/debug/db")
def api_debug_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT DATABASE(), @@hostname, @@port;")
    result = cur.fetchall()
    conn.close()
    return jsonify({"db_info": result})


# ---------------------------
# TOP PRODUCTS BY REVENUE
# ---------------------------
@app.get("/api/reports/top-products")
def api_top_products():
    days = request.args.get("days", 30, type=int)
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            p.name,
            SUM(oi.line_total) AS revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY p.id, p.name
        ORDER BY revenue DESC
        LIMIT 10
    """, (days,))

    rows = cur.fetchall()
    conn.close()
    return jsonify(rows)


# ---------------------------
# DAILY SALES WITH MOVING AVERAGE
# ---------------------------
@app.get("/api/reports/daily-sales")
def api_daily_sales():
    days = request.args.get("days", 90, type=int)
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            DATE(created_at) AS sale_date,
            SUM(total_amount) AS daily_revenue
        FROM orders
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY DATE(created_at)
        ORDER BY sale_date ASC
    """, (days,))

    rows = cur.fetchall()
    conn.close()

    # Prepare data for Chart.js
    dates = [row['sale_date'].strftime('%Y-%m-%d') for row in rows]
    revenues = [float(row['daily_revenue']) for row in rows]

    # Calculate 7-day moving average
    moving_avg = []
    for i in range(len(revenues)):
        if i < 6:
            moving_avg.append(None)
        else:
            avg = sum(revenues[i - 6:i + 1]) / 7
            moving_avg.append(round(avg, 2))

    return jsonify({
        "dates": dates,
        "revenues": revenues,
        "moving_avg": moving_avg
    })


# ---------------------------
# RECOMPUTE ORDER TOTALS
# ---------------------------
@app.post("/api/tools/recompute-order-totals")
def api_recompute_totals():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    try:
        # Get all orders
        cur.execute("SELECT id FROM orders")
        orders = cur.fetchall()

        updated_count = 0
        for order in orders:
            order_id = order['id']

            # Calculate correct total
            cur.execute("""
                SELECT SUM(line_total) AS correct_total
                FROM order_items
                WHERE order_id = %s
            """, (order_id,))

            result = cur.fetchone()
            correct_total = result['correct_total'] or 0.0

            # Update order total
            cur.execute("""
                UPDATE orders
                SET total_amount = %s
                WHERE id = %s
            """, (correct_total, order_id))

            updated_count += 1

        conn.commit()
        return jsonify({"message": f"Recomputed {updated_count} order totals successfully."})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()


# ---------------------------
# REFRESH 90-DAY SUMMARY
# ---------------------------
@app.post("/api/tools/refresh-90day-summary")
def api_refresh_summary():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    try:
        # You could create a summary table and refresh it here
        # For now, we'll just return a success message
        # since your daily report query already filters by date

        cur.execute("""
            SELECT 
                COUNT(*) AS order_count,
                SUM(total_amount) AS total_revenue
            FROM orders
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 90 DAY)
        """)

        result = cur.fetchone()
        conn.close()

        return jsonify({
            "message": f"90-day summary refreshed. {result['order_count']} orders, ${result['total_revenue']:.2f} revenue."
        })

    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500


# ---------------------------
# CHECK ORDER TOTALS FOR ERRORS
# ---------------------------
@app.get("/api/tools/check-order-totals")
def api_check_order_totals():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            o.id as order_id,
            o.total_amount as stored_total,
            COALESCE(SUM(oi.line_total), 0) as correct_total
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        GROUP BY o.id
        HAVING ABS(stored_total - correct_total) > 0.01
    """)

    errors = cur.fetchall()
    conn.close()

    return jsonify({"errors": errors})


# ---------------------------
# GET 90-DAY SUMMARY
# ---------------------------
@app.get("/api/tools/get-90day-summary")
def api_get_90day_summary():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            COUNT(*) AS order_count,
            COALESCE(SUM(total_amount), 0) AS total_revenue
        FROM orders
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 90 DAY)
    """)

    result = cur.fetchone()
    conn.close()

    return jsonify({
        "order_count": result['order_count'],
        "total_revenue": f"{float(result['total_revenue']):.2f}"
    })

# ---------------------------
# GET SINGLE PRODUCT BY ID
# ---------------------------
@app.get("/api/products/<int:product_id>")
def api_get_single_product(product_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(row)



# ---------------------------
# START FLASK SERVER
# ---------------------------
print(">>> ROUTES LOADED:")
for rule in app.url_map.iter_rules():
    print("  ", rule)

if __name__ == "__main__":
    print("Starting backend server on http://127.0.0.1:5000")
    app.run(debug=True)
