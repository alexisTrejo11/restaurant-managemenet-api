# menu/migrations/000B_payments_tables.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        # --- Create payments table ---
        migrations.RunSQL(
            sql="""
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
            """,
            reverse_sql="""
            DROP TABLE payments;
            """,
            state_operations=[
                migrations.CreateModel(
                    name='Payment',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('order', models.OneToOneField( # OneToOneField as order_id is UNIQUE
                            on_delete=models.RESTRICT,  # Matches ON DELETE RESTRICT
                            to='orders.order',            # Reference the 'Order' model
                            null=True, blank=True # order_id can be null if a payment isn't directly linked to an order initially
                        )),
                        ('payment_method', models.CharField(max_length=20, null=True, blank=True)), # Payment method can be null if not set
                        ('payment_status', models.CharField(max_length=20)),
                        ('sub_total', models.DecimalField(max_digits=10, decimal_places=2, default=0.00)),
                        ('discount', models.DecimalField(max_digits=10, decimal_places=2, default=0.00)),
                        ('vat_rate', models.DecimalField(max_digits=5, decimal_places=2, default=0.00)),
                        ('vat', models.DecimalField(max_digits=10, decimal_places=2, default=0.00)),
                        ('currency_type', models.CharField(max_length=3)),
                        ('total', models.DecimalField(max_digits=10, decimal_places=2, default=0.00)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('paid_at', models.DateTimeField(null=True, blank=True)),
                        ('deleted_at', models.DateTimeField(null=True, blank=True)),
                    ],
                ),
            ]
        ),

        # --- Create payment_items table ---
        migrations.RunSQL(
            sql="""
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
            """,
            reverse_sql="""
            DROP TABLE payment_items;
            """,
            state_operations=[
                migrations.CreateModel(
                    name='PaymentItem',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('payment', models.ForeignKey(
                            on_delete=models.CASCADE,   # Matches ON DELETE CASCADE
                            to='payments.payment',          # Reference the 'Payment' model
                        )),
                        ('order_item', models.OneToOneField( # OneToOneField as order_item_id is UNIQUE
                            on_delete=models.RESTRICT,  # Matches ON DELETE RESTRICT
                            to='orders.orderitem',        # Reference the 'OrderItem' model
                            null=True, blank=True
                        )),
                        ('menu_item', models.ForeignKey(
                            on_delete=models.RESTRICT,  # Matches ON DELETE RESTRICT
                            to='menu.dish',             # Reference the 'Dish' model
                            null=True, blank=True # Nullable in case it's a charge not linked to a specific dish
                        )),
                        ('menu_item_extra', models.ForeignKey(
                            on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL
                            to='menu.menuextra',        # Reference the 'MenuExtra' model
                            null=True, blank=True       # menu_item_extra_id is nullable
                        )),
                        ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                        ('quantity', models.IntegerField()),
                        ('extras_charges', models.DecimalField(max_digits=10, decimal_places=2, default=0.00)),
                        ('total', models.DecimalField(max_digits=10, decimal_places=2)),
                        ('charge_description', models.CharField(max_length=255, default='')),
                    ],
                ),
            ]
        ),

        # --- Insert initial data for payments and payment_items ---
        # Note: These inserts heavily rely on the 'orders', 'dishes', and 'menu_extras'
        # tables and their data being present and correctly populated.
        migrations.RunSQL(
            sql="""
            -- 1. Completed Payment (Dine-in)
            INSERT INTO payments (order_id, payment_method, payment_status, sub_total, discount, vat_rate, vat, currency_type, total, paid_at)
            VALUES (
                (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'T2') ORDER BY created_at DESC LIMIT 1),
                'CARD', 'COMPLETED', 42.50, 0.00, 10.00, 4.25, 'USD', 46.75, CURRENT_TIMESTAMP - INTERVAL '2 hours'
            );

            INSERT INTO payment_items (payment_id, menu_item_id, price, quantity, extras_charges, total, charge_description)
            VALUES
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'T2') ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Grilled Salmon'), 18.50, 1, 0.00, 18.50, 'Grilled Salmon'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'T2') ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Mushroom Risotto'), 16.00, 1, 0.00, 16.00, 'Mushroom Risotto'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'T2') ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Sparkling Water'), 2.50, 2, 0.00, 5.00, 'Sparkling Water x2'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'T2') ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Tiramisu'), 7.00, 1, 3.00, 10.00, 'Tiramisu + Extra Cream');

            -- 2. Refunded Payment (Takeaway order with issues)
            INSERT INTO payments (order_id, payment_method, payment_status, sub_total, discount, vat_rate, vat, currency_type, total, paid_at, deleted_at)
            VALUES (
                (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1),
                'CARD', 'REFUNDED', 35.50, 0.00, 10.00, 3.55, 'USD', 39.05, CURRENT_TIMESTAMP - INTERVAL '1 day', CURRENT_TIMESTAMP - INTERVAL '23 hours'
            );

            INSERT INTO payment_items (payment_id, menu_item_id, price, quantity, extras_charges, total, charge_description)
            VALUES
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Ribeye Steak'), 24.00, 1, 0.00, 24.00, 'Ribeye Steak'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Calamari'), 4.00, 1, 0.00, 4.00, 'French Fries'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'House Red Wine'), 8.00, 1, -4.00, 4.00, 'House Red Wine (half refund for corked bottle)'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1)), NULL, 0.00, 1, 3.50, 3.50, 'Delivery Fee');

            -- 3. Cancelled Payment (Online order cancelled before preparation)
            INSERT INTO payments (order_id, payment_method, payment_status, sub_total, discount, vat_rate, vat, currency_type, total, deleted_at)
            VALUES (
                (SELECT id FROM orders WHERE status = 'CANCELLED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1),
                'ONLINE', 'CANCELLED', 28.00, 0.00, 10.00, 2.80, 'USD', 30.80, CURRENT_TIMESTAMP - INTERVAL '30 minutes'
            );

            INSERT INTO payment_items (payment_id, menu_item_id, price, quantity, extras_charges, total, charge_description)
            VALUES
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'CANCELLED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Chicken Parmesan'), 17.50, 1, 0.00, 17.50, 'Chicken Parmesan'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'CANCELLED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Garlic Bread'), 2.50, 2, 0.00, 5.00, 'Garlic Bread x2'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'CANCELLED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Iced Tea'), 3.50, 1, 0.00, 3.50, 'Iced Tea'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'CANCELLED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1)), NULL, 0.00, 1, 2.00, 2.00, 'Service Fee (refunded)');


            -- 4. Completed Payment with Discount (Loyalty Customer)
            INSERT INTO payments (order_id, payment_method, payment_status, sub_total, discount, vat_rate, vat, currency_type, total, paid_at)
            VALUES (
                (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1),
                'CASH', 'COMPLETED', 60.50, 10.00, 10.00, 5.05, 'USD', 55.55, CURRENT_TIMESTAMP - INTERVAL '3 hours'
            );

            INSERT INTO payment_items (payment_id, menu_item_id, menu_item_extra_id, price, quantity, extras_charges, total, charge_description)
            VALUES
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Classic Pancakes'), NULL, 8.50, 2, 0.00, 17.00, 'Classic Pancakes x2'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Avocado Toast'), NULL, 9.00, 1, 0.00, 9.00, 'Avocado Toast'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Fresh Orange Juice'), NULL, 4.00, 3, 0.00, 12.00, 'Orange Juice x3'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Chocolate Lava Cake'), NULL, 7.50, 1, 0.00, 7.50, 'Chocolate Lava Cake'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1)), NULL, (SELECT id FROM menu_extras WHERE name = 'Side Salad'), 3.50, 2, 0.00, 7.00, 'Chicken Wingsx2'), -- The original prompt had Chicken Wings, but this refers to Side Salad extra
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1)), NULL, (SELECT id FROM menu_extras WHERE name = 'Extra Cheese'), 1.00, 3, 0.00, 3.00, 'Caprese Saladx3'); -- The original prompt had Caprese Salad, but this refers to Extra Cheese extra


            -- 5. Refunded Partial Payment (Wrong item delivered)
            INSERT INTO payments (order_id, payment_method, payment_status, sub_total, discount, vat_rate, vat, currency_type, total, paid_at, deleted_at)
            VALUES (
                (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Window-1') ORDER BY created_at DESC LIMIT 1),
                'CARD', 'REFUNDED', 31.00, 0.00, 10.00, 3.10, 'USD', 34.10, CURRENT_TIMESTAMP - INTERVAL '5 hours', CURRENT_TIMESTAMP - INTERVAL '4 hours'
            );

            INSERT INTO payment_items (payment_id, menu_item_id, price, quantity, extras_charges, total, charge_description)
            VALUES
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Window-1') ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Vegetable Curry'), 15.00, 1, 0.00, 15.00, 'Vegetable Curry (correct item)'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Window-1') ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Grilled Salmon'), 18.50, 1, 0.00, 0.00, 'Grilled Salmon (refunded - wrong item)'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Window-1') ORDER BY created_at DESC LIMIT 1)), (SELECT id FROM dishes WHERE name = 'Sparkling Water'), 2.50, 1, 0.00, 2.50, 'Sparkling Water'),
            ((SELECT id FROM payments WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Window-1') ORDER BY created_at DESC LIMIT 1)), NULL, 0.00, 1, 15.00, 15.00, 'Partial refund + compensation');
            """,
            reverse_sql="""
            -- Reversing initial data for payments and payment_items.
            -- Deleting payments will cascade delete payment_items due to ON DELETE CASCADE.
            -- Be cautious with these DELETE statements, as they rely on time intervals
            -- and specific data conditions which might not be perfectly unique if the migration
            -- is run multiple times or at different times.
            DELETE FROM payments
            WHERE order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'T2') ORDER BY created_at DESC LIMIT 1)
            OR order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1)
            OR order_id = (SELECT id FROM orders WHERE status = 'CANCELLED' AND table_id IS NULL ORDER BY created_at DESC LIMIT 1)
            OR order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Booth-A') ORDER BY created_at DESC LIMIT 1)
            OR order_id = (SELECT id FROM orders WHERE status = 'COMPLETED' AND table_id = (SELECT id FROM tables WHERE number = 'Window-1') ORDER BY created_at DESC LIMIT 1);
            """
        ),
    ]