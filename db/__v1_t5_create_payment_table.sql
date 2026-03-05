CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE,
    payment_method VARCHAR(20),
    payment_status VARCHAR(20) NOT NULL,
    sub_total NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    discount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    vat_rate NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    vat NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    currency_type VARCHAR(3) NOT NULL,
    total NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP WITH TIME ZONE, 
    deleted_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE RESTRICT
);

CREATE TABLE payment_items (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER NOT NULL,
    order_item_id INTEGER UNIQUE,
    menu_item_id INTEGER,
    menu_item_extra_id INTEGER,
    price NUMERIC(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    extras_charges NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    total NUMERIC(10, 2) NOT NULL,
    charge_description VARCHAR(255) NOT NULL DEFAULT '',
    FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES dishes(id) ON DELETE RESTRICT,
    FOREIGN KEY (menu_item_extra_id) REFERENCES menu_extras(id) ON DELETE SET NULL,
    FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE RESTRICT
);


-- 1. Completed Payment (Dine-in)

-- Main payment record
INSERT INTO payments (order_id, payment_method, payment_status, sub_total, discount, vat_rate, vat, currency_type, total, paid_at)
VALUES (1, 'CARD', 'COMPLETED', 42.50, 0.00, 10.00, 4.25, 'USD', 46.75, CURRENT_TIMESTAMP - INTERVAL '2 hours');

-- Payment items
INSERT INTO payment_items (payment_id, menu_item_id, price, quantity, extras_charges, total, charge_description)
VALUES 
(1, (SELECT id FROM dishes WHERE name = 'Grilled Salmon'), 18.50, 1, 0.00, 18.50, 'Grilled Salmon'),
(1, (SELECT id FROM dishes WHERE name = 'Mushroom Risotto'), 16.00, 1, 0.00, 16.00, 'Mushroom Risotto'),
(1, (SELECT id FROM dishes WHERE name = 'Sparkling Water'), 2.50, 2, 0.00, 5.00, 'Sparkling Water x2'),
(1, (SELECT id FROM dishes WHERE name = 'Tiramisu'), 7.00, 1, 3.00, 10.00, 'Tiramisu + Extra Cream');

-- 2. Refunded Payment (Takeaway order with issues)

-- Main payment record (initially completed, then refunded)
INSERT INTO payments (order_id, payment_method, payment_status, sub_total, discount, vat_rate, vat, currency_type, total, paid_at, deleted_at)
VALUES (2, 'CARD', 'REFUNDED', 35.50, 0.00, 10.00, 3.55, 'USD', 39.05, CURRENT_TIMESTAMP - INTERVAL '1 day', CURRENT_TIMESTAMP - INTERVAL '23 hours');

-- Payment items
INSERT INTO payment_items (payment_id, menu_item_id, price, quantity, extras_charges, total, charge_description)
VALUES 
(2, (SELECT id FROM dishes WHERE name = 'Ribeye Steak'), 24.00, 1, 0.00, 24.00, 'Ribeye Steak'),
(2, (SELECT id FROM dishes WHERE name = 'Calamari'), 4.00, 1, 0.00, 4.00, 'French Fries'),
(2, (SELECT id FROM dishes WHERE name = 'House Red Wine'), 8.00, 1, -4.00, 4.00, 'House Red Wine (half refund for corked bottle)'),
(2, NULL, 0.00, 1, 3.50, 3.50, 'Delivery Fee');

-- 3. Cancelled Payment (Online order cancelled before preparation)
-- Main payment record
INSERT INTO payments (order_id, payment_method, payment_status, sub_total, discount, vat_rate, vat, currency_type, total, deleted_at)
VALUES (3, 'ONLINE', 'CANCELLED', 28.00, 0.00, 10.00, 2.80, 'USD', 30.80, CURRENT_TIMESTAMP - INTERVAL '30 minutes');

-- Payment items
INSERT INTO payment_items (payment_id, menu_item_id, price, quantity, extras_charges, total, charge_description)
VALUES 
(3, (SELECT id FROM dishes WHERE name = 'Chicken Parmesan'), 17.50, 1, 0.00, 17.50, 'Chicken Parmesan'),
(3, (SELECT id FROM dishes WHERE name = 'Garlic Bread'), 2.50, 2, 0.00, 5.00, 'Garlic Bread x2'),
(3, (SELECT id FROM dishes WHERE name = 'Iced Tea'), 3.50, 1, 0.00, 3.50, 'Iced Tea'),
(3, NULL, 0.00, 1, 2.00, 2.00, 'Service Fee (refunded)');


-- 4. Completed Payment with Discount (Loyalty Customer)
-- Main payment record
INSERT INTO payments (order_id, payment_method, payment_status, sub_total, discount, vat_rate, vat, currency_type, total, paid_at)
VALUES (4, 'CASH', 'COMPLETED', 60.50, 10.00, 10.00, 5.05, 'USD', 55.55, CURRENT_TIMESTAMP - INTERVAL '3 hours');

-- Payment items
INSERT INTO payment_items (payment_id, menu_item_id, menu_item_extra_id, price, quantity, extras_charges, total, charge_description)
VALUES 
(4, (SELECT id FROM dishes WHERE name = 'Classic Pancakes'), NULL, 8.50, 2, 0.00, 17.00, 'Classic Pancakes x2'),
(4, (SELECT id FROM dishes WHERE name = 'Avocado Toast'), NULL, 9.00, 1, 0.00, 9.00, 'Avocado Toast'),
(4, (SELECT id FROM dishes WHERE name = 'Fresh Orange Juice'), NULL, 4.00, 3, 0.00, 12.00, 'Orange Juice x3'),
(4, (SELECT id FROM dishes WHERE name = 'Chocolate Lava Cake'), NULL, 7.50, 1, 0.00, 7.50, 'Chocolate Lava Cake'),
(4, NULL, (SELECT id FROM menu_extras WHERE name = 'Chicken Wings'), 3.50, 2, 0.00, 7.00, 'Chicken Wingsx2'),
(4, NULL, (SELECT id FROM menu_extras WHERE name = 'Caprese Salad'), 1.00, 3, 0.00, 3.00, 'Caprese Saladx3');


-- 5. Refunded Partial Payment (Wrong item delivered)
-- Main payment record
INSERT INTO payments (order_id, payment_method, payment_status, sub_total, discount, vat_rate, vat, currency_type, total, paid_at, deleted_at)
VALUES (5, 'CARD', 'REFUNDED', 31.00, 0.00, 10.00, 3.10, 'USD', 34.10, CURRENT_TIMESTAMP - INTERVAL '5 hours', CURRENT_TIMESTAMP - INTERVAL '4 hours');

-- Payment items
INSERT INTO payment_items (payment_id, menu_item_id, price, quantity, extras_charges, total, charge_description)
VALUES 
(5, (SELECT id FROM dishes WHERE name = 'Vegetable Curry'), 15.00, 1, 0.00, 15.00, 'Vegetable Curry (correct item)'),
(5, (SELECT id FROM dishes WHERE name = 'Grilled Salmon'), 18.50, 1, 0.00, 0.00, 'Grilled Salmon (refunded - wrong item)'),
(5, (SELECT id FROM dishes WHERE name = 'Sparkling Water'), 2.50, 1, 0.00, 2.50, 'Sparkling Water'),
(5, NULL, 0.00, 1, 15.00, 15.00, 'Partial refund + compensation');