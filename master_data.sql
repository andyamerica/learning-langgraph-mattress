-- ============================
-- PRODUCTS (model, size, price)
-- ============================

INSERT INTO products (model, size, price) VALUES
('Luxury', 'King', 1200),
('Luxury', 'Queen', 1000),
('Luxury', 'Super King', 1500),

('Essential', 'King', 900),
('Essential', 'Queen', 750),
('Essential', 'Super King', 1100),

('Base', 'King', 600),
('Base', 'Queen', 500),
('Base', 'Super King', 800);

-- ============================
-- CATALOG (model, description, image_url)
-- ============================

INSERT INTO catalog (model, description, image_url) VALUES
('Luxury', 'Premium hybrid mattress with cooling gel and 7-zone support.', 'https://example.com/luxury.jpg'),
('Essential', 'Balanced comfort and support at an affordable price.', 'https://example.com/essential.jpg'),
('Base', 'Simple, firm, and durable mattress for everyday use.', 'https://example.com/base.jpg');
