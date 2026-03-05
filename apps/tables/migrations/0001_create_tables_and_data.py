# menu/migrations/000Y_create_tables_and_data.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        # --- Create tables table ---
        migrations.RunSQL(
            sql="""
            CREATE TABLE tables (
                id SERIAL PRIMARY KEY,
                capacity INTEGER NOT NULL,
                number VARCHAR(255) UNIQUE NOT NULL,
                is_available BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """,
            reverse_sql="""
            DROP TABLE tables;
            """,
            state_operations=[
                migrations.CreateModel(
                    name='Table',
                    fields=[
                        ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('capacity', models.IntegerField()),
                        ('number', models.CharField(max_length=255, unique=True)),
                        ('is_available', models.BooleanField(default=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                ),
            ]
        ),

        # --- Insert data into tables ---
        migrations.RunSQL(
            sql="""
            -- Table for 2 (small intimate table)
            INSERT INTO tables (capacity, number, is_available) VALUES (2, 'T1', true);
            -- Table for 4 (standard dining table)
            INSERT INTO tables (capacity, number, is_available) VALUES (4, 'T2', true);
            -- Table for 6 (larger group table)
            INSERT INTO tables (capacity, number, is_available) VALUES (6, 'T3', true);
            -- Window-side table for 2 with nice view
            INSERT INTO tables (capacity, number, is_available) VALUES (2, 'Window-1', true);
            -- Booth seating for 4 people
            INSERT INTO tables (capacity, number, is_available) VALUES (4, 'Booth-A', true);
            -- High-top table for 4 at the bar area
            INSERT INTO tables (capacity, number, is_available) VALUES (4, 'Bar-1', true);
            -- Large round table for 8 (for big groups)
            INSERT INTO tables (capacity, number, is_available) VALUES (8, 'Round-1', true);
            -- Outdoor patio table for 4
            INSERT INTO tables (capacity, number, is_available) VALUES (4, 'Patio-3', true);
            -- Private room table for 10 (for special events)
            INSERT INTO tables (capacity, number, is_available) VALUES (10, 'Private-1', true);
            -- Corner table for 2 (popular romantic spot)
            INSERT INTO tables (capacity, number, is_available) VALUES (2, 'Corner-2', true);
            """,
            reverse_sql="""
            -- SQL para revertir la inserción de datos.
            -- De nuevo, la forma más segura es eliminar por 'number' ya que es UNIQUE.
            DELETE FROM tables WHERE number IN (
                'T1', 'T2', 'T3', 'Window-1', 'Booth-A', 'Bar-1', 'Round-1', 'Patio-3', 'Private-1', 'Corner-2'
            );
            """
        ),
    ]