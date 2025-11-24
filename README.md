# ShopLite – CS 582 Final Project  
Authors: Rowan Noel-Rickert   
Instructor: Vinay  
Semester: Fall 2024  

---

## 1. Overview

ShopLite is a lightweight e-commerce web application built for the CS 582 Final Project.  
It includes:

- Product catalog  
- Product filtering  
- Shopping cart (localStorage-based)  
- Checkout and order creation  
- Order confirmation  
- Sales reports (top products, daily sales, low stock)  
- Admin data tools  
- MySQL backend  
- Flask API  
- Frontend hosted on GitHub Pages  

Per instructor guidelines:  
**Frontend runs on GitHub Pages (static).**  
**Backend + MySQL run on localhost during the presentation.**

---

## 2. Frontend (GitHub Pages)

The frontend is fully static and contains:

- index.html
- product.html
- cart.html
- order_confirmation.html
- reports.html
- data_tools.html
- /css/styles.css
- /js/*.js files

API calls point to:

http://127.0.0.1:5000/api/...

GitHub Pages → Localhost communication works because CORS is enabled in the backend.

---

## 3. Backend (Local Flask Server)

The backend provides:

- REST API for products, orders, and reports  
- Checkout endpoint  
- Daily sales chart data  
- Low-stock warnings  
- Data tools (recompute totals, refresh 90-day summary)  
- CORS support  

Tech stack:

- Python 3  
- Flask  
- Flask-CORS  
- MySQL  
- mysql-connector-python  

---

## 4. Database Setup (MySQL)

Run the provided `schema.sql`:

mysql -u root -p < schema.sql


This creates:

- products  
- orders  
- order_items  
- daily_sales_summary  
- sample seed data  

Ensure the database name is:


---

## 5. Backend Setup

### Step 1: Create & activate virtual environment

Windows:
python -m venv venv
venv\Scripts\activate


macOS/Linux:
python3 -m venv venv
source venv/bin/activate


### Step 2: Install dependencies
pip install flask flask-cors mysql-connector-python


### Step 3: Set database credentials in app.py
DB_CONFIG = {
"host": "localhost",
"user": "root",
"password": "YOUR_PASSWORD",
"database": "shoplite"
}


### Step 4: Run the backend
python app.py


Backend runs at:
http://127.0.0.1:5000


---

## 6. Running the Frontend (GitHub Pages)

1. Push the frontend folder to GitHub  
2. Enable GitHub Pages → “Deploy from /root folder”  
3. Visit:

https://<rowannoel>.github.io/<cs582FinalProject>/


Your backend must be running locally before loading pages:
python app.py


All pages will load data through API calls to:
http://127.0.0.1:5000/api/

---

## 7. Testing Workflow

1. Start backend (`python app.py`)  
2. Open GitHub Pages website  
3. Catalog loads products from `/api/products`  
4. Product page loads via URL param (`product.html?id=3`)  
5. Add products to cart (localStorage)  
6. Checkout posts to `/api/order`  
7. Order confirmation loads via `/api/order/<id>`  
8. Reports page loads:
   - Top products
   - Daily sales chart
   - Low-stock warnings  
9. Data tools page allows:
   - Recompute order totals
   - Refresh 90-day summary  

---

## 8. Project Structure
ShopLite/
	backend/
		app.py
		schema.sql
		requirements.txt
	frontend/
		index.html
		product.html
		cart.html
		order_confirmation.html
		reports.html
		data_tools.html
		css/
		js/
	README.md

---

## 9. Design Brief

### Products  
- id (PK)  
- name  
- description  
- price  
- category  
- stock_quantity  
- reorder_level  

### Orders  
- id (PK)  
- customer fields  
- total_amount  
- created_at  

### Order Items  
- id (PK)  
- order_id (FK → orders.id)  
- product_id (FK → products.id)  
- quantity  
- unit_price  
- line_total  

### Daily Sales Summary  
- Precomputed aggregates for reporting  
- Improves chart performance  

---

## 10. Performance Notes

- Index on orders.created_at improves report queries  
- Order totals pre-stored to prevent recalculating  
- Daily sales summary precomputed  
- Category search uses indexed column  
- Cart uses localStorage for instant performance  
- API is stateless and efficient  

---

## 11. Presentation Guide

In class:

1. Start backend:
python app.py

2. Open GitHub Pages link  
3. Demonstrate:
- Catalog
- Filtering
- Product details
- Cart
- Checkout
- Order confirmation
- Reports
- Admin tools  
4. Show database schema  
5. Walk through code structure  
6. Submit GitHub repo + SQL file  

---

## 12. Submission Checklist

- [x] GitHub repo  
- [x] GitHub Pages frontend  
- [x] Flask backend  
- [x] schema.sql included  
- [x] README.md (this file)  
- [x] Design brief included  
- [x] Performance notes  
- [x] Live demo prepared  

---

## ✔ Project Complete



