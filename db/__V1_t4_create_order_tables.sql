CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    table_id INTEGER,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_at TIMESTAMP WITH TIME ZONE, -- NULLable
    FOREIGN KEY (table_id) REFERENCES tables(id) ON DELETE RESTRICT
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    menu_item_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    menu_extra_id INTEGER,
    quantity INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    is_delivered BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (menu_item_id) REFERENCES dishes(id) ON DELETE RESTRICT,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_extra_id) REFERENCES menu_extras(id) ON DELETE RESTRICT
);


--1. Completed Dine-in Order (Matches Payment ID 1)
-- Order header
INSERT INTO orders (table_id, status, created_at, end_at)
VALUES (
    (SELECT id FROM tables WHERE number = 'T2'), 
    'COMPLETED', 
    CURRENT_TIMESTAMP - INTERVAL '3 hours', 
    CURRENT_TIMESTAMP - INTERVAL '2 hours'
);
-- Order items
INSERT INTO order_items (menu_item_id, order_id, menu_extra_id, quantity, notes, is_delivered)
VALUES
((SELECT id FROM dishes WHERE name = 'Grilled Salmon'), 1, NULL, 1, 'Medium rare, extra lemon', true),
((SELECT id FROM dishes WHERE name = 'Mushroom Risotto'), 1, NULL, 1, 'No onions', true),
((SELECT id FROM dishes WHERE name = 'Sparkling Water'), 1, NULL, 2, 'With lime wedge', true),
((SELECT id FROM dishes WHERE name = 'Tiramisu'), 1, NULL, 1, 'Extra cream on side', true);


--2. Refunded Takeaway Order (Matches Payment ID 2)
-- Order header (marked completed before refund)
INSERT INTO orders (table_id, status, created_at, end_at)
VALUES (
    NULL, -- Takeaway order has no table
    'COMPLETED', 
    CURRENT_TIMESTAMP - INTERVAL '25 hours', 
    CURRENT_TIMESTAMP - INTERVAL '24 hours'
);
-- Order items
INSERT INTO order_items (menu_item_id, order_id, menu_extra_id, quantity, notes, is_delivered)
VALUES
((SELECT id FROM dishes WHERE name = 'Ribeye Steak'), 2, NULL, 1, 'Medium well, peppercorn sauce', true),
((SELECT id FROM dishes WHERE name = 'Calamari'), 2, NULL, 1, '', true),
((SELECT id FROM dishes WHERE name = 'House Red Wine'), 2, NULL, 1, 'Corked - refund issued', true);


-- 3. Cancelled Online Order (Matches Payment ID 3)
-- Order header
INSERT INTO orders (table_id, status, created_at, end_at)
VALUES (
    NULL, -- Online delivery order
    'CANCELLED', 
    CURRENT_TIMESTAMP - INTERVAL '45 minutes', 
    CURRENT_TIMESTAMP - INTERVAL '30 minutes'
);
-- Order items (never prepared/delivered)
INSERT INTO order_items (menu_item_id, order_id, menu_extra_id, quantity, notes, is_delivered)
VALUES
((SELECT id FROM dishes WHERE name = 'Chicken Parmesan'), 3, NULL, 1, 'Extra marinara', false),
((SELECT id FROM dishes WHERE name = 'Shrimp Scampi'), 3, NULL, 2, 'Extra garlic butter', false),
((SELECT id FROM dishes WHERE name = 'Iced Tea'), 3, NULL, 1, 'No lemon', false);


-- 4. Completed Breakfast Order with Discount (Matches Payment ID 4)
-- Order header
INSERT INTO orders (table_id, status, created_at, end_at)
VALUES (
    (SELECT id FROM tables WHERE number = 'Booth-A'), 
    'COMPLETED', 
    CURRENT_TIMESTAMP - INTERVAL '4 hours', 
    CURRENT_TIMESTAMP - INTERVAL '3 hours'
);
-- Order items
INSERT INTO order_items (menu_item_id, order_id, menu_extra_id, quantity, notes, is_delivered)
VALUES
((SELECT id FROM dishes WHERE name = 'Classic Pancakes'), 4, NULL, 2, 'Maple syrup on side', true),
((SELECT id FROM dishes WHERE name = 'Avocado Toast'), 4, NULL, 1, 'Eggs poached hard', true),
((SELECT id FROM dishes WHERE name = 'Fresh Orange Juice'), 4, NULL, 3, 'No ice', true),
((SELECT id FROM dishes WHERE name = 'Chocolate Lava Cake'), 4, NULL, 1, 'For dessert', true),
((SELECT id FROM dishes WHERE name = 'Chicken Wings'), 4, (SELECT id FROM menu_extras WHERE name = 'Side Salad'), 2, 'Balsamic dressing', true),
((SELECT id FROM dishes WHERE name = 'Caprese Salad'), 4, (SELECT id FROM menu_extras WHERE name = 'Extra Cheese'), 3, 'For avocado toast', true);

-- 5. Refunded Partial Order (Matches Payment ID 5)
-- Order header
INSERT INTO orders (table_id, status, created_at, end_at)
VALUES (
    (SELECT id FROM tables WHERE number = 'Window-1'), 
    'COMPLETED', 
    CURRENT_TIMESTAMP - INTERVAL '6 hours', 
    CURRENT_TIMESTAMP - INTERVAL '5 hours'
);
-- Order items
INSERT INTO order_items (menu_item_id, order_id, menu_extra_id, quantity, notes, is_delivered)
VALUES
((SELECT id FROM dishes WHERE name = 'Vegetable Curry'), 5, NULL, 1, 'Mild spice', true),
((SELECT id FROM dishes WHERE name = 'Grilled Salmon'), 5, NULL, 1, 'Wrong item delivered - refunded', false),
((SELECT id FROM dishes WHERE name = 'Sparkling Water'), 5, NULL, 1, NULL, true);