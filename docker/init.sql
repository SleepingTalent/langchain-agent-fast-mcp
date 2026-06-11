-- init.sql: Database schema and seed data for the AI Agent application.

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes to support ILIKE search queries efficiently
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_users_name_trgm  ON users USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_users_email_trgm ON users USING GIN (email gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_products_name_trgm ON products USING GIN (name gin_trgm_ops);

-- Seed users
INSERT INTO users (name, email) VALUES
    ('Alice Johnson', 'alice@example.com'),
    ('Bob Smith', 'bob@example.com'),
    ('Charlie Davis', 'charlie@example.com'),
    ('Diana Martinez', 'diana@example.com'),
    ('Eve Wilson', 'eve@example.com');

-- Seed products
INSERT INTO products (name, price, stock) VALUES
    ('Wireless Keyboard', 49.99, 150),
    ('USB-C Hub', 34.99, 75),
    ('Mechanical Pencil Set', 12.50, 3),
    ('Noise-Cancelling Headphones', 199.99, 42),
    ('Laptop Stand', 29.99, 8),
    ('Webcam HD 1080p', 59.99, 0),
    ('Portable SSD 1TB', 89.99, 5),
    ('Ergonomic Mouse', 39.99, 200);
