-- Dish
CREATE TABLE dishes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image VARCHAR(255) NOT NULL DEFAULT '',
    price NUMERIC(10,2) NOT NULL,
    description VARCHAR(255) NOT NULL DEFAULT '',
    category VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Menu Extra
CREATE TABLE menu_extras(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    description VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Drinks (Non-Alcoholic)
INSERT INTO dishes (name, price, description, category, status) VALUES
('Sparkling Water', 2.50, 'Carbonated mineral water with lemon slice', 'DRINKS', 'ACTIVE'),
('Fresh Orange Juice', 4.00, 'Freshly squeezed orange juice', 'DRINKS', 'ACTIVE'),
('Iced Tea', 3.50, 'House brewed black tea with lemon', 'DRINKS', 'ACTIVE'),
('Espresso', 3.00, 'Single shot of premium Italian espresso', 'DRINKS', 'ACTIVE'),
('Cappuccino', 4.50, 'Espresso with steamed milk and foam', 'DRINKS', 'ACTIVE');

-- Alcohol Drinks
INSERT INTO dishes (name, price, description, category, status) VALUES
('House Red Wine', 8.00, 'Glass of our signature Cabernet Sauvignon', 'ALCOHOL_DRINKS', 'ACTIVE'),
('Craft Beer', 6.50, 'Local IPA with citrus notes', 'ALCOHOL_DRINKS', 'ACTIVE'),
('Classic Mojito', 10.00, 'White rum, fresh mint, lime, sugar and soda', 'ALCOHOL_DRINKS', 'ACTIVE'),
('Chardonnay', 9.00, 'Glass of Californian Chardonnay', 'ALCOHOL_DRINKS', 'ACTIVE'),
('Whiskey Sour', 12.00, 'Bourbon, lemon juice, sugar and angostura', 'ALCOHOL_DRINKS', 'ACTIVE');

-- Breakfast
INSERT INTO dishes (name, price, description, category, status) VALUES
('Classic Pancakes', 8.50, 'Stack of three buttermilk pancakes with maple syrup', 'BREAKFASTS', 'ACTIVE'),
('Avocado Toast', 9.00, 'Sourdough bread with smashed avocado and poached eggs', 'BREAKFASTS', 'ACTIVE'),
('Full English', 12.50, 'Eggs, bacon, sausages, beans, mushrooms and toast', 'BREAKFASTS', 'ACTIVE'),
('Greek Yogurt Parfait', 7.00, 'With granola, honey and fresh berries', 'BREAKFASTS', 'ACTIVE'),
('Breakfast Burrito', 10.50, 'Scrambled eggs, cheese, beans and salsa in tortilla', 'BREAKFASTS', 'ACTIVE');

-- Starters
INSERT INTO dishes (name, price, description, category, status) VALUES
('Bruschetta', 7.50, 'Toasted bread topped with tomatoes, garlic and basil', 'STARTERS', 'ACTIVE'),
('Calamari', 9.00, 'Crispy fried squid with lemon aioli', 'STARTERS', 'ACTIVE'),
('Caprese Salad', 8.50, 'Fresh mozzarella, tomatoes and basil', 'STARTERS', 'ACTIVE'),
('French Onion Soup', 7.00, 'Caramelized onions in rich beef broth with cheese toast', 'STARTERS', 'ACTIVE'),
('Chicken Wings', 8.50, 'Crispy wings with choice of BBQ or Buffalo sauce', 'STARTERS', 'ACTIVE');

-- Meals
INSERT INTO dishes (name, price, description, category, status) VALUES
('Grilled Salmon', 18.50, 'With lemon butter sauce and seasonal vegetables', 'MEALS', 'ACTIVE'),
('Ribeye Steak', 24.00, '12oz prime cut with mashed potatoes and red wine jus', 'MEALS', 'ACTIVE'),
('Mushroom Risotto', 16.00, 'Creamy arborio rice with wild mushrooms and parmesan', 'MEALS', 'ACTIVE'),
('Chicken Parmesan', 17.50, 'Breaded chicken with marinara and mozzarella, served with pasta', 'MEALS', 'ACTIVE'),
('Vegetable Curry', 15.00, 'Spicy coconut curry with seasonal vegetables and rice', 'MEALS', 'ACTIVE');

-- Desserts
INSERT INTO dishes (name, price, description, category, status) VALUES
('Chocolate Lava Cake', 7.50, 'Warm chocolate cake with molten center and vanilla ice cream', 'DESSERTS', 'ACTIVE'),
('Cheesecake', 6.50, 'New York style with berry compote', 'DESSERTS', 'ACTIVE'),
('Tiramisu', 7.00, 'Classic Italian dessert with coffee and mascarpone', 'DESSERTS', 'ACTIVE'),
('Crème Brûlée', 6.50, 'Vanilla custard with caramelized sugar top', 'DESSERTS', 'ACTIVE'),
('Fruit Sorbet', 5.50, 'Selection of seasonal fruit sorbets', 'DESSERTS', 'ACTIVE');

-- Extras
INSERT INTO menu_extras (name, price, description) VALUES
('Side Salad', 3.50, 'Mixed greens with balsamic vinaigrette'),
('Garlic Bread', 2.50, 'Toasted bread with garlic butter'),
('French Fries', 4.00, 'Crispy golden fries with sea salt'),
('Truffle Oil Drizzle', 1.50, 'For pasta or risotto dishes'),
('Extra Cheese', 1.00, 'For any dish that needs more cheese');

-- Draft Items
INSERT INTO dishes (name, price, description, category, status) VALUES
('Pumpkin Spice Latte', 5.00, 'Seasonal autumn coffee drink', 'DRINKS', 'DRAFT'),
('Holiday Eggnog', 6.50, 'Traditional Christmas drink with rum', 'ALCOHOL_DRINKS', 'DRAFT'),
('Summer Berry Salad', 14.00, 'Seasonal salad with fresh berries and goat cheese', 'MEALS', 'DRAFT');

-- Inactive
INSERT INTO dishes (name, price, description, category, status) VALUES
('Shrimp Scampi', 19.50, 'Pasta with garlic butter shrimp (discontinued)', 'MEALS', 'INACTIVE'),
('Peach Melba', 6.00, 'Classic dessert with peaches and raspberry sauce (seasonal)', 'DESSERTS', 'INACTIVE');
