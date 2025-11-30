-- ------------------------------------------------------------
--  SCHEMA: ShopLite (Final Project)
--  Matches frontend catalog + backend API exactly
-- ------------------------------------------------------------

DROP DATABASE IF EXISTS shoplite;
CREATE DATABASE shoplite;
USE shoplite;

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;

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

DESCRIBE orders;
DESCRIBE order_items;

SELECT * FROM orders;
SELECT * FROM order_items;

-- ------------------------------------------------------------
--  SEED HISTORICAL ORDERS (Last 90 Days)
--  This creates realistic demo data for reports
-- ------------------------------------------------------------

-- Order 1: 85 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Alice Johnson', 'alice@email.com', '123 Main St', 'Seattle', 'WA', '98101', 0.00, DATE_SUB(NOW(), INTERVAL 85 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES 
    (@order_id, 1, 2, 19.99, 39.98),
    (@order_id, 3, 1, 9.99, 9.99);

UPDATE orders SET total_amount = 49.97 WHERE id = @order_id;

-- Order 2: 80 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Bob Smith', 'bob@email.com', '456 Oak Ave', 'Portland', 'OR', '97201', 0.00, DATE_SUB(NOW(), INTERVAL 80 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES (@order_id, 5, 1, 129.99, 129.99);

UPDATE orders SET total_amount = 129.99 WHERE id = @order_id;

-- Order 3: 75 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Carol White', 'carol@email.com', '789 Pine Rd', 'San Francisco', 'CA', '94102', 0.00, DATE_SUB(NOW(), INTERVAL 75 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES 
    (@order_id, 2, 1, 79.99, 79.99),
    (@order_id, 4, 1, 39.99, 39.99);

UPDATE orders SET total_amount = 119.98 WHERE id = @order_id;

-- Order 4: 70 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('David Brown', 'david@email.com', '321 Elm St', 'Austin', 'TX', '78701', 0.00, DATE_SUB(NOW(), INTERVAL 70 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES 
    (@order_id, 1, 3, 19.99, 59.97),
    (@order_id, 3, 2, 9.99, 19.98);

UPDATE orders SET total_amount = 79.95 WHERE id = @order_id;

-- Order 5: 65 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Emma Davis', 'emma@email.com', '654 Maple Dr', 'Denver', 'CO', '80201', 0.00, DATE_SUB(NOW(), INTERVAL 65 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES (@order_id, 2, 1, 79.99, 79.99);

UPDATE orders SET total_amount = 79.99 WHERE id = @order_id;

-- Order 6: 60 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Frank Wilson', 'frank@email.com', '987 Birch Ln', 'Chicago', 'IL', '60601', 0.00, DATE_SUB(NOW(), INTERVAL 60 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES 
    (@order_id, 5, 2, 129.99, 259.98),
    (@order_id, 4, 1, 39.99, 39.99);

UPDATE orders SET total_amount = 299.97 WHERE id = @order_id;

-- Order 7: 55 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Grace Lee', 'grace@email.com', '246 Cedar St', 'Boston', 'MA', '02101', 0.00, DATE_SUB(NOW(), INTERVAL 55 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES 
    (@order_id, 1, 1, 19.99, 19.99),
    (@order_id, 3, 5, 9.99, 49.95);

UPDATE orders SET total_amount = 69.94 WHERE id = @order_id;

-- Order 8: 50 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Henry Martinez', 'henry@email.com', '135 Walnut Ave', 'Miami', 'FL', '33101', 0.00, DATE_SUB(NOW(), INTERVAL 50 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES (@order_id, 2, 2, 79.99, 159.98);

UPDATE orders SET total_amount = 159.98 WHERE id = @order_id;

-- Order 9: 45 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Ivy Taylor', 'ivy@email.com', '579 Spruce Ct', 'Phoenix', 'AZ', '85001', 0.00, DATE_SUB(NOW(), INTERVAL 45 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES 
    (@order_id, 4, 2, 39.99, 79.98),
    (@order_id, 3, 3, 9.99, 29.97);

UPDATE orders SET total_amount = 109.95 WHERE id = @order_id;

-- Order 10: 40 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Jack Anderson', 'jack@email.com', '864 Ash Blvd', 'Las Vegas', 'NV', '89101', 0.00, DATE_SUB(NOW(), INTERVAL 40 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES (@order_id, 5, 1, 129.99, 129.99);

UPDATE orders SET total_amount = 129.99 WHERE id = @order_id;

-- Order 11: 35 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Karen Thomas', 'karen@email.com', '753 Willow Way', 'Atlanta', 'GA', '30301', 0.00, DATE_SUB(NOW(), INTERVAL 35 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES 
    (@order_id, 1, 4, 19.99, 79.96),
    (@order_id, 2, 1, 79.99, 79.99);

UPDATE orders SET total_amount = 159.95 WHERE id = @order_id;

-- Order 12: 30 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Larry Jackson', 'larry@email.com', '951 Poplar Pl', 'Detroit', 'MI', '48201', 0.00, DATE_SUB(NOW(), INTERVAL 30 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES 
    (@order_id, 3, 10, 9.99, 99.90),
    (@order_id, 4, 1, 39.99, 39.99);

UPDATE orders SET total_amount = 139.89 WHERE id = @order_id;

-- Order 13: 25 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Monica Harris', 'monica@email.com', '159 Hickory St', 'Seattle', 'WA', '98102', 0.00, DATE_SUB(NOW(), INTERVAL 25 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES (@order_id, 5, 1, 129.99, 129.99);

UPDATE orders SET total_amount = 129.99 WHERE id = @order_id;

-- Order 14: 20 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Nathan Clark', 'nathan@email.com', '357 Beech Ave', 'Philadelphia', 'PA', '19101', 0.00, DATE_SUB(NOW(), INTERVAL 20 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES 
    (@order_id, 1, 2, 19.99, 39.98),
    (@order_id, 2, 1, 79.99, 79.99),
    (@order_id, 3, 2, 9.99, 19.98);

UPDATE orders SET total_amount = 139.95 WHERE id = @order_id;

-- Order 15: 15 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Olivia Lewis', 'olivia@email.com', '468 Sycamore Dr', 'Houston', 'TX', '77001', 0.00, DATE_SUB(NOW(), INTERVAL 15 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES (@order_id, 4, 3, 39.99, 119.97);

UPDATE orders SET total_amount = 119.97 WHERE id = @order_id;

-- Order 16: 10 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Paul Walker', 'paul@email.com', '741 Chestnut Rd', 'San Diego', 'CA', '92101', 0.00, DATE_SUB(NOW(), INTERVAL 10 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES 
    (@order_id, 2, 1, 79.99, 79.99),
    (@order_id, 5, 1, 129.99, 129.99);

UPDATE orders SET total_amount = 209.98 WHERE id = @order_id;

-- Order 17: 5 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Quinn Robinson', 'quinn@email.com', '852 Magnolia Ln', 'Dallas', 'TX', '75201', 0.00, DATE_SUB(NOW(), INTERVAL 5 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES 
    (@order_id, 1, 5, 19.99, 99.95),
    (@order_id, 3, 4, 9.99, 39.96);

UPDATE orders SET total_amount = 139.91 WHERE id = @order_id;

-- Order 18: 2 days ago
INSERT INTO orders (customer_name, customer_email, customer_address, customer_city, customer_state, customer_zip, total_amount, created_at)
VALUES ('Rachel Young', 'rachel@email.com', '963 Dogwood Ct', 'New York', 'NY', '10001', 0.00, DATE_SUB(NOW(), INTERVAL 2 DAY));

SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
VALUES (@order_id, 5, 2, 129.99, 259.98);

UPDATE orders SET total_amount = 259.98 WHERE id = @order_id;

-- Verify the seed data
SELECT 
    COUNT(*) as total_orders,
    MIN(created_at) as earliest_order,
    MAX(created_at) as latest_order,
    SUM(total_amount) as total_revenue
FROM orders;


-- Intentionally set some order totals to WRONG values
-- This simulates data corruption or manual database errors

UPDATE orders SET total_amount = 990.99 WHERE id = 1;
UPDATE orders SET total_amount = 90.00 WHERE id = 5;
UPDATE orders SET total_amount = 55.00 WHERE id = 10;

