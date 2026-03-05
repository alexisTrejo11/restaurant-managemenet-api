# menu/migrations/000A_orders_and_items.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        # --- Create orders table ---
        migrations.RunSQL(
            sql="""
            CREATE TABLE orders (
                id SERIAL PRIMARY KEY,
                table_id INTEGER,
                status VARCHAR(20) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                end_at TIMESTAMP WITH TIME ZONE,
                FOREIGN KEY (table_id) REFERENCES tables(id) ON DELETE RESTRICT
            );
            """,
            reverse_sql="""
            DROP TABLE orders;
            """,
            state_operations=[
                migrations.CreateModel(
                    name='Order',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('table', models.ForeignKey(
                            on_delete=models.RESTRICT,  # Matches ON DELETE RESTRICT
                            to='tables.table',            # Reference the 'Table' model
                            null=True, blank=True       # table_id is nullable
                        )),
                        ('status', models.CharField(max_length=20)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('end_at', models.DateTimeField(null=True, blank=True)),
                    ],
                ),
            ]
        ),

        # --- Create order_items table ---
        migrations.RunSQL(
            sql="""
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
            """,
            reverse_sql="""
            DROP TABLE order_items;
            """,
            state_operations=[
                migrations.CreateModel(
                    name='OrderItem',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('menu_item', models.ForeignKey(
                            on_delete=models.RESTRICT,  # Matches ON DELETE RESTRICT
                            to='menu.dish',             # Reference the 'Dish' model
                        )),
                        ('order', models.ForeignKey(
                            on_delete=models.CASCADE,   # Matches ON DELETE CASCADE
                            to='orders.order',            # Reference the 'Order' model
                        )),
                        ('added_at', models.DateTimeField(auto_now_add=True)),
                        ('menu_extra', models.ForeignKey(
                            on_delete=models.RESTRICT,  # Matches ON DELETE RESTRICT
                            to='menu.menuextra',        # Reference the 'MenuExtra' model
                            null=True, blank=True       # menu_extra_id is nullable
                        )),
                        ('quantity', models.IntegerField(default=1)),
                        ('notes', models.TextField(null=True, blank=True)),
                        ('is_delivered', models.BooleanField(default=False)),
                    ],
                ),
            ]
        ),

        # --- Insert initial data for orders and order_items ---
        # Note: The subqueries to get IDs (tables.id, dishes.id, menu_extras.id)
        # require these tables and their data to be present.
        # Ensure your dependencies are correctly ordered!
        migrations.RunSQL(
            sql="""
            --1. Completed Dine-in Order
            INSERT INTO orders (table_id, status, created_at, end_at)
            VALUES (
                (SELECT id FROM tables WHERE number = 'T2'),
                'COMPLETED',
                CURRENT_TIMESTAMP - INTERVAL '3 hours',
                CURRENT_TIMESTAMP - INTERVAL '2 hours'
            );
            INSERT INTO order_items (menu_item_id, order_id, menu_extra_id, quantity, notes, is_delivered)
            VALUES
            ((SELECT id FROM dishes WHERE name = 'Grilled Salmon'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'T2') ORDER BY created_at DESC LIMIT 1), NULL, 1, 'Medium rare, extra lemon', true),
            ((SELECT id FROM dishes WHERE name = 'Mushroom Risotto'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'T2') ORDER BY created_at DESC LIMIT 1), NULL, 1, 'No onions', true),
            ((SELECT id FROM dishes WHERE name = 'Sparkling Water'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'T2') ORDER BY created_at DESC LIMIT 1), NULL, 2, 'With lime wedge', true),
            ((SELECT id FROM dishes WHERE name = 'Tiramisu'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'T2') ORDER BY created_at DESC LIMIT 1), NULL, 1, 'Extra cream on side', true);


            --2. Refunded Takeaway Order
            INSERT INTO orders (table_id, status, created_at, end_at)
            VALUES (
                NULL,
                'COMPLETED',
                CURRENT_TIMESTAMP - INTERVAL '25 hours',
                CURRENT_TIMESTAMP - INTERVAL '24 hours'
            );
            INSERT INTO order_items (menu_item_id, order_id, menu_extra_id, quantity, notes, is_delivered)
            VALUES
            ((SELECT id FROM dishes WHERE name = 'Ribeye Steak'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1), NULL, 1, 'Medium well, peppercorn sauce', true),
            ((SELECT id FROM dishes WHERE name = 'Calamari'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1), NULL, 1, '', true),
            ((SELECT id FROM dishes WHERE name = 'House Red Wine'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1), NULL, 1, 'Corked - refund issued', true);


            -- 3. Cancelled Online Order
            INSERT INTO orders (table_id, status, created_at, end_at)
            VALUES (
                NULL,
                'CANCELLED',
                CURRENT_TIMESTAMP - INTERVAL '45 minutes',
                CURRENT_TIMESTAMP - INTERVAL '30 minutes'
            );
            INSERT INTO order_items (menu_item_id, order_id, menu_extra_id, quantity, notes, is_delivered)
            VALUES
            ((SELECT id FROM dishes WHERE name = 'Chicken Parmesan'), (SELECT id FROM orders WHERE status = 'CANCELLED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1), NULL, 1, 'Extra marinara', false),
            ((SELECT id FROM dishes WHERE name = 'Shrimp Scampi'), (SELECT id FROM orders WHERE status = 'CANCELLED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1), NULL, 2, 'Extra garlic butter', false),
            ((SELECT id FROM dishes WHERE name = 'Iced Tea'), (SELECT id FROM orders WHERE status = 'CANCELLED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1), NULL, 1, 'No lemon', false);


            -- 4. Completed Breakfast Order with Discount
            INSERT INTO orders (table_id, status, created_at, end_at)
            VALUES (
                (SELECT id FROM tables WHERE number = 'Booth-A'),
                'COMPLETED',
                CURRENT_TIMESTAMP - INTERVAL '4 hours',
                CURRENT_TIMESTAMP - INTERVAL '3 hours'
            );
            INSERT INTO order_items (menu_item_id, order_id, menu_extra_id, quantity, notes, is_delivered)
            VALUES
            ((SELECT id FROM dishes WHERE name = 'Classic Pancakes'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1), NULL, 2, 'Maple syrup on side', true),
            ((SELECT id FROM dishes WHERE name = 'Avocado Toast'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1), NULL, 1, 'Eggs poached hard', true),
            ((SELECT id FROM dishes WHERE name = 'Fresh Orange Juice'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1), NULL, 3, 'No ice', true),
            ((SELECT id FROM dishes WHERE name = 'Chocolate Lava Cake'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1), NULL, 1, 'For dessert', true),
            ((SELECT id FROM dishes WHERE name = 'Chicken Wings'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1), (SELECT id FROM menu_extras WHERE name = 'Side Salad'), 2, 'Balsamic dressing', true),
            ((SELECT id FROM dishes WHERE name = 'Caprese Salad'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1), (SELECT id FROM menu_extras WHERE name = 'Extra Cheese'), 3, 'For avocado toast', true);

            -- 5. Refunded Partial Order
            INSERT INTO orders (table_id, status, created_at, end_at)
            VALUES (
                (SELECT id FROM tables WHERE number = 'Window-1'),
                'COMPLETED',
                CURRENT_TIMESTAMP - INTERVAL '6 hours',
                CURRENT_TIMESTAMP - INTERVAL '5 hours'
            );
            INSERT INTO order_items (menu_item_id, order_id, menu_extra_id, quantity, notes, is_delivered)
            VALUES
            ((SELECT id FROM dishes WHERE name = 'Vegetable Curry'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Window-1') ORDER BY created_at DESC LIMIT 1), NULL, 1, 'Mild spice', true),
            ((SELECT id FROM dishes WHERE name = 'Grilled Salmon'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Window-1') ORDER BY created_at DESC LIMIT 1), NULL, 1, 'Wrong item delivered - refunded', false),
            ((SELECT id FROM dishes WHERE name = 'Sparkling Water'), (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Window-1') ORDER BY created_at DESC LIMIT 1), NULL, 1, NULL, true);
            """,
            reverse_sql="""
            -- Reverse deletion for orders and order_items.
            -- Deleting orders will cascade delete order_items due to ON DELETE CASCADE.
            -- It's simplest to delete orders based on criteria you can identify from the initial inserts.
            -- Note: Using 'status' and 'created_at' as discriminators is an example.
            -- If you run this migration multiple times, these 'reverse_sql' DELETEs might
            -- become more complex or potentially delete data from other runs.
            DELETE FROM orders
            WHERE (status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'T2'))
            OR (status = 'COMPLETED' AND table_id IS NULL AND created_at = CURRENT_TIMESTAMP - INTERVAL '25 hours')
            OR (status = 'CANCELLED' AND table_id IS NULL AND created_at = CURRENT_TIMESTAMP - INTERVAL '45 minutes')
            OR (status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A'))
            OR (status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Window-1'));
            """
        ),
    ]