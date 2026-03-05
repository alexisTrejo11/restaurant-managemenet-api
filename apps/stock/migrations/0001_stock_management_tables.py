from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        # --- Create stock_items table ---
        migrations.RunSQL(
            sql="""
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
            """,
            reverse_sql="""
            DROP TABLE stock_items;
            """,
            state_operations=[
                migrations.CreateModel(
                    name='StockItem',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('menu_item', models.ForeignKey(
                            on_delete=models.SET_NULL, # Matches ON DELETE SET NULL
                            to='menu.dish',             # Reference the 'Dish' model in 'menu' app
                            null=True,                  # Allow NULL for menu_item_id
                            blank=True,                 # Allow blank in forms
                        )),
                        ('name', models.CharField(max_length=255, unique=True)),
                        ('unit', models.CharField(max_length=10)), # Django models handle CHECK constraints implicitly often
                        ('category', models.CharField(max_length=15, default='OTHER')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                ),
            ]
        ),

        # --- Create stocks table ---
        migrations.RunSQL(
            sql="""
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
            """,
            reverse_sql="""
            DROP TABLE stocks;
            """,
            state_operations=[
                migrations.CreateModel(
                    name='Stock',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('item', models.OneToOneField( # OneToOneField as item_id is UNIQUE
                            on_delete=models.RESTRICT,  # Matches ON DELETE RESTRICT
                            to='stock.stockitem',        # Reference the 'StockItem' model
                        )),
                        ('total_stock', models.IntegerField(default=0)),
                        ('optimal_stock_quantity', models.IntegerField(default=1)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                ),
            ]
        ),

        # --- Create stock_transactions table ---
        migrations.RunSQL(
            sql="""
            CREATE TABLE stock_transactions (
                id SERIAL PRIMARY KEY,
                stock_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                transaction_type VARCHAR(3) NOT NULL,
                date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP WITH TIME ZONE,
                employee_id INTEGER, 
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT quantity_check CHECK (quantity >= 1 AND quantity <= 10000),
                FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE RESTRICT
                -- Assuming 'users' table is in 'auth' app or similar.
                -- FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE SET NULL
            );
            """,
            reverse_sql="""
            DROP TABLE stock_transactions;
            """,
            state_operations=[
                migrations.CreateModel(
                    name='StockTransaction',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('stock', models.ForeignKey(
                            on_delete=models.RESTRICT,  # Matches ON DELETE RESTRICT
                            to='stock.stock',            # Reference the 'Stock' model
                        )),
                        ('quantity', models.IntegerField()), # Django models often handle CHECK constraints implicitly
                        ('transaction_type', models.CharField(max_length=3)),
                        ('date', models.DateTimeField(auto_now_add=True)),
                        ('expires_at', models.DateTimeField(null=True, blank=True)),
                        # If you have a User model in Django's auth app:
                        ('employee', models.ForeignKey(
                            on_delete=models.SET_NULL,
                            to='auth.user', # Assuming 'users' means Django's default User model
                            null=True, blank=True
                        )),
                        # If you have a custom User model in a different app, adjust 'auth.user' accordingly,
                        # e.g., 'myapp.customuser'
                        ('notes', models.TextField(null=True, blank=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                    ],
                ),
            ]
        ),

        # --- Create Indexes ---
        # Note: You can create indexes via RunSQL, or by defining them in the Model's Meta class.
        # If defined in Meta, makemigrations will automatically generate the AddIndex operation.
        # Here, we keep them in RunSQL for consistency with your request.
        migrations.RunSQL(
            sql="""
            CREATE INDEX idx_stock_transactions_type ON stock_transactions (transaction_type);
            CREATE INDEX idx_stock_transactions_date ON stock_transactions (date);
            CREATE INDEX idx_stock_transactions_stock_date ON stock_transactions (stock_id, date);
            """,
            reverse_sql="""
            DROP INDEX idx_stock_transactions_type;
            DROP INDEX idx_stock_transactions_date;
            DROP INDEX idx_stock_transactions_stock_date;
            """
        ),

        # --- Insert initial data for stock_items ---
        # Note: The subqueries to get 'dishes.id' require that the 'dishes' table
        # and its data are already present when this migration runs.
        # Ensure your dependencies are correctly ordered!
        migrations.RunSQL(
            sql="""
            INSERT INTO stock_items (menu_item_id, name, unit, category) VALUES
            ((SELECT id FROM dishes WHERE name = 'Grilled Salmon'), 'Fresh Salmon Fillet', 'kg', 'INGREDIENT'),
            ((SELECT id FROM dishes WHERE name = 'Ribeye Steak'), 'Prime Ribeye', 'kg', 'INGREDIENT'),
            ((SELECT id FROM dishes WHERE name = 'Caprese Salad'), 'Fresh Mozzarella', 'kg', 'INGREDIENT'),
            ((SELECT id FROM dishes WHERE name = 'Classic Pancakes'), 'Maple Syrup', 'l', 'INGREDIENT'),
            ((SELECT id FROM dishes WHERE name = 'Chocolate Lava Cake'), 'Dark Chocolate', 'kg', 'INGREDIENT'),
            (NULL, 'Extra Virgin Olive Oil', 'l', 'INGREDIENT'),
            (NULL, 'Sea Salt', 'kg', 'INGREDIENT'),
            (NULL, 'Black Peppercorns', 'kg', 'INGREDIENT');

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
            """,
            reverse_sql="""
            -- Reverse deletion for stock_items by name.
            DELETE FROM stock_items WHERE name IN (
                'Fresh Salmon Fillet', 'Prime Ribeye', 'Fresh Mozzarella', 'Maple Syrup', 'Dark Chocolate',
                'Extra Virgin Olive Oil', 'Sea Salt', 'Black Peppercorns',
                'Chef Knife', 'Cutting Board', 'Saucepan 2L', 'Mixing Bowls Set', 'Whisk',
                'Food Storage Container 5L', 'Glass Meal Prep Container', 'Sauce Squeeze Bottle',
                'Plastic Deli Container', 'Vacuum Seal Bag',
                'Disposable Gloves', 'Apron', 'Chef Hat', 'Cleaning Cloth', 'First Aid Kit'
            );
            """
        ),

        # --- Insert initial data for stocks ---
        # Note: This relies on stock_items being populated with specific IDs.
        # The IDs (1-20) are based on the order of insertion in the previous block.
        # This can be fragile if the order of insertion changes.
        # For robustness, you might consider using subqueries to get item_id by name if possible.
        migrations.RunSQL(
            sql="""
            INSERT INTO stocks (item_id, total_stock, optimal_stock_quantity) VALUES
            ((SELECT id FROM stock_items WHERE name = 'Fresh Salmon Fillet'), 15, 10),
            ((SELECT id FROM stock_items WHERE name = 'Prime Ribeye'), 20, 15),
            ((SELECT id FROM stock_items WHERE name = 'Fresh Mozzarella'), 8, 5),
            ((SELECT id FROM stock_items WHERE name = 'Maple Syrup'), 12, 8),
            ((SELECT id FROM stock_items WHERE name = 'Dark Chocolate'), 6, 4),
            ((SELECT id FROM stock_items WHERE name = 'Extra Virgin Olive Oil'), 10, 5),
            ((SELECT id FROM stock_items WHERE name = 'Sea Salt'), 3, 2),
            ((SELECT id FROM stock_items WHERE name = 'Black Peppercorns'), 2, 1),
            ((SELECT id FROM stock_items WHERE name = 'Chef Knife'), 10, 5),
            ((SELECT id FROM stock_items WHERE name = 'Cutting Board'), 15, 10),
            ((SELECT id FROM stock_items WHERE name = 'Saucepan 2L'), 8, 6),
            ((SELECT id FROM stock_items WHERE name = 'Mixing Bowls Set'), 5, 3),
            ((SELECT id FROM stock_items WHERE name = 'Whisk'), 12, 8),
            ((SELECT id FROM stock_items WHERE name = 'Food Storage Container 5L'), 20, 15),
            ((SELECT id FROM stock_items WHERE name = 'Glass Meal Prep Container'), 30, 20),
            ((SELECT id FROM stock_items WHERE name = 'Sauce Squeeze Bottle'), 15, 10),
            ((SELECT id FROM stock_items WHERE name = 'Plastic Deli Container'), 50, 30),
            ((SELECT id FROM stock_items WHERE name = 'Vacuum Seal Bag'), 200, 100),
            ((SELECT id FROM stock_items WHERE name = 'Disposable Gloves'), 10, 5),
            ((SELECT id FROM stock_items WHERE name = 'Apron'), 15, 10);
            """,
            reverse_sql="""
            -- Reverse deletion for stocks. Use item_id to delete.
            DELETE FROM stocks WHERE item_id IN (SELECT id FROM stock_items WHERE name IN (
                'Fresh Salmon Fillet', 'Prime Ribeye', 'Fresh Mozzarella', 'Maple Syrup', 'Dark Chocolate',
                'Extra Virgin Olive Oil', 'Sea Salt', 'Black Peppercorns',
                'Chef Knife', 'Cutting Board', 'Saucepan 2L', 'Mixing Bowls Set', 'Whisk',
                'Food Storage Container 5L', 'Glass Meal Prep Container', 'Sauce Squeeze Bottle',
                'Plastic Deli Container', 'Vacuum Seal Bag',
                'Disposable Gloves', 'Apron'
            ));
            """
        ),

        # --- Insert sample stock_transactions ---
        migrations.RunSQL(
            sql="""
            -- Sample transactions (these are harder to reverse precisely without knowing the IDs
            -- of the stocks they refer to. For initial data, often reversing transactions
            -- means just deleting them, assuming they're illustrative).
            INSERT INTO stock_transactions (stock_id, quantity, transaction_type, notes) VALUES
            ((SELECT id FROM stocks WHERE item_id = (SELECT id FROM stock_items WHERE name = 'Fresh Salmon Fillet')), 5, 'IN', 'Weekly fish delivery from supplier');
            INSERT INTO stock_transactions (stock_id, quantity, transaction_type, notes) VALUES
            ((SELECT id FROM stocks WHERE item_id = (SELECT id FROM stock_items WHERE name = 'Prime Ribeye')), 3, 'OUT', 'Dinner service usage');
            INSERT INTO stock_transactions (stock_id, quantity, transaction_type, notes) VALUES
            ((SELECT id FROM stocks WHERE item_id = (SELECT id FROM stock_items WHERE name = 'Chef Knife')), 2, 'IN', 'Replacement chef knives');
            INSERT INTO stock_transactions (stock_id, quantity, transaction_type, notes) VALUES
            ((SELECT id FROM stocks WHERE item_id = (SELECT id FROM stock_items WHERE name = 'Cutting Board')), 3, 'IN', 'Additional cutting boards');
            INSERT INTO stock_transactions (stock_id, quantity, transaction_type, notes) VALUES
            ((SELECT id FROM stocks WHERE item_id = (SELECT id FROM stock_items WHERE name = 'Extra Virgin Olive Oil')), 4, 'OUT', 'High usage during lunch service');
            INSERT INTO stock_transactions (stock_id, quantity, transaction_type, expires_at, notes) VALUES
            ((SELECT id FROM stocks WHERE item_id = (SELECT id FROM stock_items WHERE name = 'Disposable Gloves')), 5, 'IN', CURRENT_TIMESTAMP + INTERVAL '1 year', 'Quarterly gloves order');
            INSERT INTO stock_transactions (stock_id, quantity, transaction_type, notes) VALUES
            ((SELECT id FROM stocks WHERE item_id = (SELECT id FROM stock_items WHERE name = 'Apron')), 5, 'IN', 'New staff aprons');
            """,
            reverse_sql="""
            -- Deleting all transactions for simplicity in a reverse migration.
            -- In a real scenario, you might want more granular control,
            -- or if transactions update stock levels, you'd need to reverse those updates too.
            DELETE FROM stock_transactions;
            """
        ),
    ]