
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    city VARCHAR(100),
    state VARCHAR(100),
    signup_date DATE
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price NUMERIC(12, 2) NOT NULL,
    stock_quantity INTEGER
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TIMESTAMP NOT NULL,
    total_amount NUMERIC(14, 2) NOT NULL,
    payment_method VARCHAR(50),
    order_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    item_total NUMERIC(14, 2) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_customer
ON orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_orders_date
ON orders(order_date);

CREATE INDEX IF NOT EXISTS idx_order_items_product
ON order_items(product_id);


CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id SERIAL PRIMARY KEY,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    status VARCHAR(30),
    customers_processed INTEGER DEFAULT 0,
    products_processed INTEGER DEFAULT 0,
    orders_processed INTEGER DEFAULT 0,
    order_items_processed INTEGER DEFAULT 0,
    error_message TEXT
);


CREATE TABLE IF NOT EXISTS streaming_order_events (
    event_id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL UNIQUE,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL,
    total_amount NUMERIC(14, 2) NOT NULL,
    payment_method VARCHAR(50),
    order_status VARCHAR(50),
    event_timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_streaming_events_timestamp
ON streaming_order_events(event_timestamp);


CREATE TABLE IF NOT EXISTS customer_rfm (
    customer_id INTEGER PRIMARY KEY REFERENCES customers(customer_id),
    last_purchase_date TIMESTAMP,
    recency_days INTEGER,
    frequency INTEGER,
    monetary NUMERIC(14, 2),
    recency_score INTEGER,
    frequency_score INTEGER,
    monetary_score INTEGER,
    rfm_score VARCHAR(3),
    customer_segment VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
