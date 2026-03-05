# menu/migrations/000C_create_reservations_table.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        # --- Create reservations table ---
        migrations.RunSQL(
            sql="""
            CREATE TABLE reservations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phone_number VARCHAR(255) NOT NULL,
                customer_number INTEGER NOT NULL,
                email VARCHAR(255) NOT NULL,
                table_id INTEGER NOT NULL,
                reservation_date TIMESTAMP WITH TIME ZONE NOT NULL,
                status VARCHAR(20) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                cancelled_at TIMESTAMP WITH TIME ZONE,
                FOREIGN KEY (table_id) REFERENCES tables(id) ON DELETE RESTRICT,
                CONSTRAINT chk_reservation_status CHECK (status IN ('PENDING', 'BOOKED', 'ATTENDED', 'NOT_ATTENDED', 'CANCELLED'))
            );
            """,
            reverse_sql="""
            DROP TABLE reservations;
            """,
            state_operations=[
                migrations.CreateModel(
                    name='Reservation',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=255)),
                        ('phone_number', models.CharField(max_length=255)),
                        ('customer_number', models.IntegerField()),
                        ('email', models.CharField(max_length=255)),
                        ('table', models.ForeignKey(
                            on_delete=models.RESTRICT, # Matches ON DELETE RESTRICT
                            to='tables.table',           # Reference the 'Table' model
                        )),
                        ('reservation_date', models.DateTimeField()),
                        ('status', models.CharField(max_length=20)), # Django handles CHECK constraints often through application logic or choices
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('cancelled_at', models.DateTimeField(null=True, blank=True)),
                    ],
                ),
            ]
        ),

        # --- Insert initial data for reservations ---
        migrations.RunSQL(
            sql="""
            INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status)
            VALUES (
                'John Smith',
                '+15551234567',
                4,
                'john.smith@example.com',
                (SELECT id FROM tables WHERE number = 'T2'),
                CURRENT_TIMESTAMP + INTERVAL '2 days 19:00',
                'BOOKED'
            );

            INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status, created_at)
            VALUES (
                'Emily Johnson',
                '+15559876543',
                2,
                'emily.j@example.com',
                (SELECT id FROM tables WHERE number = 'Window-1'),
                CURRENT_TIMESTAMP - INTERVAL '3 days 19:30',
                'ATTENDED',
                CURRENT_TIMESTAMP - INTERVAL '5 days'
            );

            INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status, cancelled_at)
            VALUES (
                'Michael Brown',
                '+15555551234',
                6,
                'michael.b@example.com',
                (SELECT id FROM tables WHERE number = 'Round-1'),
                CURRENT_TIMESTAMP + INTERVAL '1 day 20:00',
                'CANCELLED',
                CURRENT_TIMESTAMP - INTERVAL '2 hours'
            );

            INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status)
            VALUES (
                'Sarah Wilson',
                '+15553334455',
                3,
                'sarah.w@example.com',
                (SELECT id FROM tables WHERE number = 'Booth-A'),
                CURRENT_TIMESTAMP - INTERVAL '1 day 18:45',
                'NOT_ATTENDED'
            );

            -- This is a duplicate of the previous Sarah Wilson entry, if you intend to keep it unique, remove this one.
            INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status)
            VALUES (
                'Sarah Wilson',
                '+15553334455',
                3,
                'sarah.w@example.com',
                (SELECT id FROM tables WHERE number = 'Booth-A'),
                CURRENT_TIMESTAMP - INTERVAL '1 day 18:45',
                'NOT_ATTENDED'
            );

            INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status)
            VALUES (
                'David Lee',
                '+15557778899',
                5,
                'david.lee@example.com',
                (SELECT id FROM tables WHERE number = 'Private-1'),
                CURRENT_TIMESTAMP + INTERVAL '3 days 20:30',
                'PENDING'
            );

            INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status)
            VALUES (
                'Robert and Maria Garcia',
                '+15556667777',
                2,
                'garcia.family@example.com',
                (SELECT id FROM tables WHERE number = 'Corner-2'),
                CURRENT_TIMESTAMP + INTERVAL '1 week 19:00',
                'BOOKED'
            );

            INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status, created_at)
            VALUES (
                'TechSolutions Inc.',
                '+15552468013',
                4,
                'events@techsolutions.com',
                (SELECT id FROM tables WHERE number = 'T3'),
                CURRENT_TIMESTAMP - INTERVAL '5 hours',
                'ATTENDED',
                CURRENT_TIMESTAMP - INTERVAL '2 days'
            );

            INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status, cancelled_at)
            VALUES (
                'Jessica Taylor',
                '+15558765432',
                8,
                'jessica.t@example.com',
                (SELECT id FROM tables WHERE number = 'Round-1'),
                CURRENT_TIMESTAMP + INTERVAL '1 hour',
                'CANCELLED',
                CURRENT_TIMESTAMP - INTERVAL '30 minutes'
            );

            INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status, created_at)
            VALUES (
                'Thomas Anderson',
                '+15551231234',
                4,
                'thomas.a@example.com',
                (SELECT id FROM tables WHERE number = 'Window-1'),
                CURRENT_TIMESTAMP - INTERVAL '1 week 19:15',
                'ATTENDED',
                CURRENT_TIMESTAMP - INTERVAL '2 weeks'
            );

            INSERT INTO reservations (name, phone_number, customer_number, email, table_id, reservation_date, status)
            VALUES (
                'Smith Family Reunion',
                '+15554443322',
                12,
                'smith.family@example.com',
                (SELECT id FROM tables WHERE number = 'Private-1'),
                CURRENT_TIMESTAMP + INTERVAL '2 weeks 12:00',
                'BOOKED'
            );
            """,
            reverse_sql="""
            -- Reverse deletion for reservations.
            -- This DELETE statement will attempt to remove the inserted records based on their email and phone_number.
            -- If you intend to run this multiple times and need more granular control,
            -- you might need to add more unique identifiers or handle it differently.
            DELETE FROM reservations WHERE email IN (
                'john.smith@example.com',
                'emily.j@example.com',
                'michael.b@example.com',
                'sarah.w@example.com', -- Will delete both Sarah Wilson entries
                'david.lee@example.com',
                'garcia.family@example.com',
                'events@techsolutions.com',
                'jessica.t@example.com',
                'thomas.a@example.com',
                'smith.family@example.com'
            );
            """
        ),
    ]