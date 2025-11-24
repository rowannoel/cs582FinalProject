-- ------------------------------------------------------------
--  SCHEMA: ShopLite (Final Project)
--  Matches frontend catalog + backend API exactly
-- ------------------------------------------------------------

DROP DATABASE IF EXISTS shoplite;
CREATE DATABASE shoplite;
USE shoplite;

-- ------------------------------------------------------------
--  PRODUCTS
-- ------------------------------------------------------------
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    stock_quantity INT NOT NULL DEFAULT 0,
    reorder_level INT NOT NULL DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index to speed up category searches
CREATE INDEX idx_products_category ON products(category);

-- ------------------------------------------------------------
--  ORDERS
-- ------------------------------------------------------------
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,

    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255),
    customer_address VARCHAR(255),
    customer_city VARCHAR(100),
    customer_state VARCHAR(100),
    customer_zip VARCHAR(20),

    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for time-window report queries
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- ------------------------------------------------------------
--  ORDER ITEMS
-- ------------------------------------------------------------
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,

    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_orderitems_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_orderitems_product
        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE RESTRICT
);

-- Speed up product performance calculations
CREATE INDEX idx_orderitems_product_id ON order_items(product_id);

-- ------------------------------------------------------------
--  DAILY SALES SUMMARY (for 90-day report)
-- ------------------------------------------------------------
CREATE TABLE daily_sales_summary (
    sale_date DATE PRIMARY KEY,
    total_revenue DECIMAL(10,2) NOT NULL,
    total_orders INT NOT NULL
);

-- ------------------------------------------------------------
--  SEED PRODUCT DATA
--  (Matches catalog used in your frontend)
-- ------------------------------------------------------------
INSERT INTO products (name, description, price, category, stock_quantity, reorder_level)
VALUES
('Wireless Mouse',
 'Ergonomic 2.4GHz wireless mouse',
 19.99, 'Electronics', 50, 10),

('Mechanical Keyboard',
 'Backlit mechanical keyboard with tactile switches',
 79.99, 'Electronics', 25, 5),

('USB-C Cable',
 'Durable 1-meter USB-C charging cable',
 9.99, 'Accessories', 100, 20),

('Laptop Stand',
 'Adjustable aluminum laptop stand for desks',
 39.99, 'Accessories', 30, 8),

('Noise Cancelling Headphones',
 'Over-ear headphones with active noise cancellation',
 129.99, 'Electronics', 15, 3);

