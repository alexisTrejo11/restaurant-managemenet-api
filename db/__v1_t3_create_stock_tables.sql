CREATE TABLE stock_items (
    id SERIAL PRIMARY KEY,
    menu_item_id INTEGER,
    name VARCHAR(255) UNIQUE NOT NULL,
    unit VARCHAR(10) NOT NULL,
    category VARCHAR(15) NOT NULL DEFAULT 'OTHER',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT non_empty_unit CHECK (unit IS NOT NULL AND unit != ''),
    FOREIGN KEY (menu_item_id) REFERENCES dishes(id) ON DELETE SET NULL
);

CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    item_id INTEGER UNIQUE NOT NULL,
    total_stock INTEGER NOT NULL DEFAULT 0,
    optimal_stock_quantity INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT non_negative_stock CHECK (total_stock >= 0),
    CONSTRAINT minimum_optimal_stock CHECK (optimal_stock_quantity >= 1),
    FOREIGN KEY (item_id) REFERENCES stock_items(id) ON DELETE RESTRICT
);

CREATE TABLE stock_transactions (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    transaction_type VARCHAR(3) NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    employee_id INTEGER, 
    notes TEXT, -- Can be NULL
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT quantity_check CHECK (quantity >= 1 AND quantity <= 10000),
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE RESTRICT
    --FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_stock_transactions_type ON stock_transactions (transaction_type);
CREATE INDEX idx_stock_transactions_date ON stock_transactions (date);
CREATE INDEX idx_stock_transactions_stock_date ON stock_transactions (stock_id, date);


INSERT INTO stock_items (menu_item_id, name, unit, category) VALUES
((SELECT id FROM dishes WHERE name = 'Grilled Salmon'), 'Fresh Salmon Fillet', 'kg', 'INGREDIENT'),
((SELECT id FROM dishes WHERE name = 'Ribeye Steak'), 'Prime Ribeye', 'kg', 'INGREDIENT'),
((SELECT id FROM dishes WHERE name = 'Caprese Salad'), 'Fresh Mozzarella', 'kg', 'INGREDIENT'),
((SELECT id FROM dishes WHERE name = 'Classic Pancakes'), 'Maple Syrup', 'l', 'INGREDIENT'),
((SELECT id FROM dishes WHERE name = 'Chocolate Lava Cake'), 'Dark Chocolate', 'kg', 'INGREDIENT'),
(NULL, 'Extra Virgin Olive Oil', 'l', 'INGREDIENT'), -- General kitchen ingredient
(NULL, 'Sea Salt', 'kg', 'INGREDIENT'), -- General kitchen ingredient
(NULL, 'Black Peppercorns', 'kg', 'INGREDIENT'); -- General kitchen ingredient

-- UTENSILS
INSERT INTO stock_items (name, unit, category) VALUES
('Chef Knife', 'pc', 'UTENSIL'),
('Cutting Board', 'pc', 'UTENSIL'),
('Saucepan 2L', 'pc', 'UTENSIL'),
('Mixing Bowls Set', 'set', 'UTENSIL'),
('Whisk', 'pc', 'UTENSIL');

-- CONTAINERS
INSERT INTO stock_items (name, unit, category) VALUES
('Food Storage Container 5L', 'pc', 'CONTAINER'),
('Glass Meal Prep Container', 'pc', 'CONTAINER'),
('Sauce Squeeze Bottle', 'pc', 'CONTAINER'),
('Plastic Deli Container', 'pc', 'CONTAINER'),
('Vacuum Seal Bag', 'pc', 'CONTAINER');

-- OTHER items
INSERT INTO stock_items (name, unit, category) VALUES
('Disposable Gloves', 'box', 'OTHER'),
('Apron', 'pc', 'OTHER'),
('Chef Hat', 'pc', 'OTHER'),
('Cleaning Cloth', 'pc', 'OTHER'),
('First Aid Kit', 'pc', 'OTHER');

-- Insert stock levels for all items
INSERT INTO stocks (item_id, total_stock, optimal_stock_quantity) VALUES
(1, 15, 10),  -- Fresh Salmon Fillet (kg)
(2, 20, 15),  -- Prime Ribeye (kg)
(3, 8, 5),    -- Fresh Mozzarella (kg)
(4, 12, 8),    -- Maple Syrup (l)
(5, 6, 4),     -- Dark Chocolate (kg)
(6, 10, 5),    -- Olive Oil (l)
(7, 3, 2),     -- Sea Salt (kg)
(8, 2, 1),     -- Black Peppercorns (kg)
(9, 10, 5),    -- Chef Knife (pc)
(10, 15, 10),  -- Cutting Board (pc)
(11, 8, 6),    -- Saucepan 2L (pc)
(12, 5, 3),    -- Mixing Bowls Set (set)
(13, 12, 8),   -- Whisk (pc)
(14, 20, 15),  -- Food Storage Container 5L (pc)
(15, 30, 20),  -- Glass Meal Prep Container (pc)
(16, 15, 10),  -- Sauce Squeeze Bottle (pc)
(17, 50, 30),  -- Plastic Deli Container (pc)
(18, 200, 100),-- Vacuum Seal Bag (pc)
(19, 10, 5),   -- Disposable Gloves (box)
(20, 15, 10);  -- Apron (pc)


-- Sample transactions

-- Fresh Salmon delivery
INSERT INTO stock_transactions (stock_id, quantity, transaction_type, notes) VALUES
(1, 5, 'IN', 'Weekly fish delivery from supplier');
-- Ribeye Steak used
INSERT INTO stock_transactions (stock_id, quantity, transaction_type, notes) VALUES
(2, 3, 'OUT', 'Dinner service usage');
-- New utensils purchased
INSERT INTO stock_transactions (stock_id, quantity, transaction_type, notes) VALUES
(9, 2, 'IN', 'Replacement chef knives'),
(10, 3, 'IN', 'Additional cutting boards');
-- Olive oil running low
INSERT INTO stock_transactions (stock_id, quantity, transaction_type, notes) VALUES
(6, 4, 'OUT', 'High usage during lunch service');
-- Monthly cleaning supplies restock
INSERT INTO stock_transactions (stock_id, quantity, transaction_type, expires_at, notes) VALUES
(19, 5, 'IN', CURRENT_TIMESTAMP + INTERVAL '1 year', 'Quarterly gloves order'),
(20, 5, 'IN', NULL, 'New staff aprons');