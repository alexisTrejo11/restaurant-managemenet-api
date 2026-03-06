from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.menu.models import Dish, MenuExtra
from apps.tables.models import Table
from apps.stock.models import StockItem, Stock, StockTransaction
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment, PaymentItem
from apps.reservations.models import Reservation


class Command(BaseCommand):
    help = "Populate database with demo data"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting demo data population..."))

        # Check if data already exists
        if Dish.objects.exists() or Table.objects.exists():
            self.stdout.write(self.style.WARNING("Data already exists in database."))
            confirm = input(
                "Do you want to continue? This will skip existing records. (yes/no): "
            )
            if confirm.lower() != "yes":
                self.stdout.write(self.style.ERROR("Operation cancelled."))
                return

        self.populate_dishes()
        self.populate_menu_extras()
        self.populate_tables()
        self.populate_stock_items()
        self.populate_stocks()
        self.populate_stock_transactions()
        self.populate_orders_and_items()
        self.populate_payments()
        self.populate_reservations()

        self.stdout.write(self.style.SUCCESS("Demo data populated successfully!"))

    def populate_dishes(self):
        self.stdout.write("Populating dishes...")

        dishes_data = [
            # Drinks (Non-Alcoholic)
            (
                "Sparkling Water",
                2.50,
                "Carbonated mineral water with lemon slice",
                "DRINKS",
                "ACTIVE",
            ),
            (
                "Fresh Orange Juice",
                4.00,
                "Freshly squeezed orange juice",
                "DRINKS",
                "ACTIVE",
            ),
            ("Iced Tea", 3.50, "House brewed black tea with lemon", "DRINKS", "ACTIVE"),
            (
                "Espresso",
                3.00,
                "Single shot of premium Italian espresso",
                "DRINKS",
                "ACTIVE",
            ),
            (
                "Cappuccino",
                4.50,
                "Espresso with steamed milk and foam",
                "DRINKS",
                "ACTIVE",
            ),
            # Alcohol Drinks
            (
                "House Red Wine",
                8.00,
                "Glass of our signature Cabernet Sauvignon",
                "ALCOHOL_DRINKS",
                "ACTIVE",
            ),
            (
                "Craft Beer",
                6.50,
                "Local IPA with citrus notes",
                "ALCOHOL_DRINKS",
                "ACTIVE",
            ),
            (
                "Classic Mojito",
                10.00,
                "White rum, fresh mint, lime, sugar and soda",
                "ALCOHOL_DRINKS",
                "ACTIVE",
            ),
            (
                "Chardonnay",
                9.00,
                "Glass of Californian Chardonnay",
                "ALCOHOL_DRINKS",
                "ACTIVE",
            ),
            (
                "Whiskey Sour",
                12.00,
                "Bourbon, lemon juice, sugar and angostura",
                "ALCOHOL_DRINKS",
                "ACTIVE",
            ),
            # Breakfast
            (
                "Classic Pancakes",
                8.50,
                "Stack of three buttermilk pancakes with maple syrup",
                "BREAKFASTS",
                "ACTIVE",
            ),
            (
                "Avocado Toast",
                9.00,
                "Sourdough bread with smashed avocado and poached eggs",
                "BREAKFASTS",
                "ACTIVE",
            ),
            (
                "Full English",
                12.50,
                "Eggs, bacon, sausages, beans, mushrooms and toast",
                "BREAKFASTS",
                "ACTIVE",
            ),
            (
                "Greek Yogurt Parfait",
                7.00,
                "With granola, honey and fresh berries",
                "BREAKFASTS",
                "ACTIVE",
            ),
            (
                "Breakfast Burrito",
                10.50,
                "Scrambled eggs, cheese, beans and salsa in tortilla",
                "BREAKFASTS",
                "ACTIVE",
            ),
            # Starters
            (
                "Bruschetta",
                7.50,
                "Toasted bread topped with tomatoes, garlic and basil",
                "STARTERS",
                "ACTIVE",
            ),
            (
                "Calamari",
                9.00,
                "Crispy fried squid with lemon aioli",
                "STARTERS",
                "ACTIVE",
            ),
            (
                "Caprese Salad",
                8.50,
                "Fresh mozzarella, tomatoes and basil",
                "STARTERS",
                "ACTIVE",
            ),
            (
                "French Onion Soup",
                7.00,
                "Caramelized onions in rich beef broth with cheese toast",
                "STARTERS",
                "ACTIVE",
            ),
            (
                "Chicken Wings",
                8.50,
                "Crispy wings with choice of BBQ or Buffalo sauce",
                "STARTERS",
                "ACTIVE",
            ),
            # Meals
            (
                "Grilled Salmon",
                18.50,
                "With lemon butter sauce and seasonal vegetables",
                "MEALS",
                "ACTIVE",
            ),
            (
                "Ribeye Steak",
                24.00,
                "12oz prime cut with mashed potatoes and red wine jus",
                "MEALS",
                "ACTIVE",
            ),
            (
                "Mushroom Risotto",
                16.00,
                "Creamy arborio rice with wild mushrooms and parmesan",
                "MEALS",
                "ACTIVE",
            ),
            (
                "Chicken Parmesan",
                17.50,
                "Breaded chicken with marinara and mozzarella, served with pasta",
                "MEALS",
                "ACTIVE",
            ),
            (
                "Vegetable Curry",
                15.00,
                "Spicy coconut curry with seasonal vegetables and rice",
                "MEALS",
                "ACTIVE",
            ),
            # Desserts
            (
                "Chocolate Lava Cake",
                7.50,
                "Warm chocolate cake with molten center and vanilla ice cream",
                "DESSERTS",
                "ACTIVE",
            ),
            (
                "Cheesecake",
                6.50,
                "New York style with berry compote",
                "DESSERTS",
                "ACTIVE",
            ),
            (
                "Tiramisu",
                7.00,
                "Classic Italian dessert with coffee and mascarpone",
                "DESSERTS",
                "ACTIVE",
            ),
            (
                "Crème Brûlée",
                6.50,
                "Vanilla custard with caramelized sugar top",
                "DESSERTS",
                "ACTIVE",
            ),
            (
                "Fruit Sorbet",
                5.50,
                "Selection of seasonal fruit sorbets",
                "DESSERTS",
                "ACTIVE",
            ),
            # Draft Items
            (
                "Pumpkin Spice Latte",
                5.00,
                "Seasonal autumn coffee drink",
                "DRINKS",
                "DRAFT",
            ),
            (
                "Holiday Eggnog",
                6.50,
                "Traditional Christmas drink with rum",
                "ALCOHOL_DRINKS",
                "DRAFT",
            ),
            (
                "Summer Berry Salad",
                14.00,
                "Seasonal salad with fresh berries and goat cheese",
                "MEALS",
                "DRAFT",
            ),
            # Inactive
            (
                "Shrimp Scampi",
                19.50,
                "Pasta with garlic butter shrimp (discontinued)",
                "MEALS",
                "INACTIVE",
            ),
            (
                "Peach Melba",
                6.00,
                "Classic dessert with peaches and raspberry sauce (seasonal)",
                "DESSERTS",
                "INACTIVE",
            ),
        ]

        for name, price, description, category, status in dishes_data:
            Dish.objects.get_or_create(
                name=name,
                defaults={
                    "price": Decimal(str(price)),
                    "description": description,
                    "category": category,
                    "status": status,
                },
            )

        self.stdout.write(self.style.SUCCESS(f"  Created {len(dishes_data)} dishes"))

    def populate_menu_extras(self):
        self.stdout.write("Populating menu extras...")

        extras_data = [
            ("Side Salad", 3.50, "Mixed greens with balsamic vinaigrette"),
            ("Garlic Bread", 2.50, "Toasted bread with garlic butter"),
            ("French Fries", 4.00, "Crispy golden fries with sea salt"),
            ("Truffle Oil Drizzle", 1.50, "For pasta or risotto dishes"),
            ("Extra Cheese", 1.00, "For any dish that needs more cheese"),
        ]

        for name, price, description in extras_data:
            MenuExtra.objects.get_or_create(
                name=name,
                defaults={"price": Decimal(str(price)), "description": description},
            )

        self.stdout.write(
            self.style.SUCCESS(f"  Created {len(extras_data)} menu extras")
        )

    def populate_tables(self):
        self.stdout.write("Populating tables...")

        tables_data = [
            (2, "T1", True),
            (4, "T2", True),
            (6, "T3", True),
            (2, "Window-1", True),
            (4, "Booth-A", True),
            (4, "Bar-1", True),
            (8, "Round-1", True),
            (4, "Patio-3", True),
            (10, "Private-1", True),
            (2, "Corner-2", True),
        ]

        for capacity, number, is_available in tables_data:
            Table.objects.get_or_create(
                number=number,
                defaults={"capacity": capacity, "is_available": is_available},
            )

        self.stdout.write(self.style.SUCCESS(f"  Created {len(tables_data)} tables"))

    def populate_stock_items(self):
        self.stdout.write("Populating stock items...")

        # Get dishes for foreign keys
        grilled_salmon = Dish.objects.filter(name="Grilled Salmon").first()
        ribeye_steak = Dish.objects.filter(name="Ribeye Steak").first()
        caprese_salad = Dish.objects.filter(name="Caprese Salad").first()
        classic_pancakes = Dish.objects.filter(name="Classic Pancakes").first()
        chocolate_lava = Dish.objects.filter(name="Chocolate Lava Cake").first()

        stock_items_data = [
            # Ingredients
            ("Fresh Salmon Fillet", "kg", "INGREDIENT", grilled_salmon),
            ("Prime Ribeye", "kg", "INGREDIENT", ribeye_steak),
            ("Fresh Mozzarella", "kg", "INGREDIENT", caprese_salad),
            ("Maple Syrup", "l", "INGREDIENT", classic_pancakes),
            ("Dark Chocolate", "kg", "INGREDIENT", chocolate_lava),
            ("Extra Virgin Olive Oil", "l", "INGREDIENT", None),
            ("Sea Salt", "kg", "INGREDIENT", None),
            ("Black Peppercorns", "kg", "INGREDIENT", None),
            # Utensils
            ("Chef Knife", "pc", "UTENSIL", None),
            ("Cutting Board", "pc", "UTENSIL", None),
            ("Saucepan 2L", "pc", "UTENSIL", None),
            ("Mixing Bowls Set", "set", "UTENSIL", None),
            ("Whisk", "pc", "UTENSIL", None),
            # Containers
            ("Food Storage Container 5L", "pc", "CONTAINER", None),
            ("Glass Meal Prep Container", "pc", "CONTAINER", None),
            ("Sauce Squeeze Bottle", "pc", "CONTAINER", None),
            ("Plastic Deli Container", "pc", "CONTAINER", None),
            ("Vacuum Seal Bag", "pc", "CONTAINER", None),
            # Other
            ("Disposable Gloves", "box", "OTHER", None),
            ("Apron", "pc", "OTHER", None),
            ("Chef Hat", "pc", "OTHER", None),
            ("Cleaning Cloth", "pc", "OTHER", None),
            ("First Aid Kit", "pc", "OTHER", None),
        ]

        for name, unit, category, menu_item in stock_items_data:
            StockItem.objects.get_or_create(
                name=name,
                defaults={"unit": unit, "category": category, "menu_item": menu_item},
            )

        self.stdout.write(
            self.style.SUCCESS(f"  Created {len(stock_items_data)} stock items")
        )

    def populate_stocks(self):
        self.stdout.write("Populating stocks...")

        stock_data = [
            ("Fresh Salmon Fillet", 15, 10),
            ("Prime Ribeye", 20, 15),
            ("Fresh Mozzarella", 8, 5),
            ("Maple Syrup", 12, 8),
            ("Dark Chocolate", 6, 4),
            ("Extra Virgin Olive Oil", 10, 5),
            ("Sea Salt", 3, 2),
            ("Black Peppercorns", 2, 1),
            ("Chef Knife", 10, 5),
            ("Cutting Board", 15, 10),
            ("Saucepan 2L", 8, 6),
            ("Mixing Bowls Set", 5, 3),
            ("Whisk", 12, 8),
            ("Food Storage Container 5L", 20, 15),
            ("Glass Meal Prep Container", 30, 20),
            ("Sauce Squeeze Bottle", 15, 10),
            ("Plastic Deli Container", 50, 30),
            ("Vacuum Seal Bag", 200, 100),
            ("Disposable Gloves", 10, 5),
            ("Apron", 15, 10),
        ]

        for item_name, total_stock, optimal_stock_quantity in stock_data:
            item = StockItem.objects.filter(name=item_name).first()
            if item:
                Stock.objects.get_or_create(
                    item=item,
                    defaults={
                        "total_stock": total_stock,
                        "optimal_stock_quantity": optimal_stock_quantity,
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(f"  Created {len(stock_data)} stock records")
        )

    def populate_stock_transactions(self):
        self.stdout.write("Populating stock transactions...")

        # Get stock items
        salmon_stock = Stock.objects.filter(item__name="Fresh Salmon Fillet").first()
        ribeye_stock = Stock.objects.filter(item__name="Prime Ribeye").first()
        chef_knife_stock = Stock.objects.filter(item__name="Chef Knife").first()
        cutting_board_stock = Stock.objects.filter(item__name="Cutting Board").first()
        olive_oil_stock = Stock.objects.filter(
            item__name="Extra Virgin Olive Oil"
        ).first()
        gloves_stock = Stock.objects.filter(item__name="Disposable Gloves").first()
        apron_stock = Stock.objects.filter(item__name="Apron").first()

        transactions_data = [
            (salmon_stock, 5, "IN", "Weekly fish delivery from supplier", None),
            (ribeye_stock, 3, "OUT", "Dinner service usage", None),
            (chef_knife_stock, 2, "IN", "Replacement chef knives", None),
            (cutting_board_stock, 3, "IN", "Additional cutting boards", None),
            (olive_oil_stock, 4, "OUT", "High usage during lunch service", None),
            (
                gloves_stock,
                5,
                "IN",
                "Quarterly gloves order",
                timezone.now() + timedelta(days=365),
            ),
            (apron_stock, 5, "IN", "New staff aprons", None),
        ]

        for stock, quantity, transaction_type, notes, expires_at in transactions_data:
            if stock:
                StockTransaction.objects.get_or_create(
                    stock=stock,
                    quantity=quantity,
                    transaction_type=transaction_type,
                    defaults={"notes": notes, "expires_at": expires_at},
                )

        self.stdout.write(
            self.style.SUCCESS(f"  Created {len(transactions_data)} stock transactions")
        )

    def populate_orders_and_items(self):
        self.stdout.write("Populating orders and order items...")

        # Order 1: Completed Dine-in
        table_t2 = Table.objects.filter(number="T2").first()
        if (
            table_t2
            and not Order.objects.filter(table=table_t2, status="COMPLETED").exists()
        ):
            order1 = Order.objects.create(
                table=table_t2,
                status="COMPLETED",
                created_at=timezone.now() - timedelta(hours=3),
                end_at=timezone.now() - timedelta(hours=2),
            )

            OrderItem.objects.create(
                menu_item=Dish.objects.get(name="Grilled Salmon"),
                order=order1,
                quantity=1,
                notes="Medium rare, extra lemon",
                is_delivered=True,
            )
            OrderItem.objects.create(
                menu_item=Dish.objects.get(name="Mushroom Risotto"),
                order=order1,
                quantity=1,
                notes="No onions",
                is_delivered=True,
            )
            OrderItem.objects.create(
                menu_item=Dish.objects.get(name="Sparkling Water"),
                order=order1,
                quantity=2,
                notes="With lime wedge",
                is_delivered=True,
            )
            OrderItem.objects.create(
                menu_item=Dish.objects.get(name="Tiramisu"),
                order=order1,
                quantity=1,
                notes="Extra cream on side",
                is_delivered=True,
            )

        # Order 2: Refunded Takeaway (no table)
        if not Order.objects.filter(table__isnull=True, status="COMPLETED").exists():
            order2 = Order.objects.create(
                table=None,
                status="COMPLETED",
                created_at=timezone.now() - timedelta(hours=25),
                end_at=timezone.now() - timedelta(hours=24),
            )

            OrderItem.objects.create(
                menu_item=Dish.objects.get(name="Ribeye Steak"),
                order=order2,
                quantity=1,
                notes="Medium well, peppercorn sauce",
                is_delivered=True,
            )
            OrderItem.objects.create(
                menu_item=Dish.objects.get(name="Calamari"),
                order=order2,
                quantity=1,
                notes="",
                is_delivered=True,
            )
            OrderItem.objects.create(
                menu_item=Dish.objects.get(name="House Red Wine"),
                order=order2,
                quantity=1,
                notes="Corked - refund issued",
                is_delivered=True,
            )

        # Order 3: Cancelled Online Order
        order3, created = Order.objects.get_or_create(
            status="CANCELLED",
            table__isnull=True,
            defaults={
                "table": None,
                "created_at": timezone.now() - timedelta(minutes=45),
                "end_at": timezone.now() - timedelta(minutes=30),
            },
        )

        if created:
            OrderItem.objects.create(
                menu_item=Dish.objects.get(name="Chicken Parmesan"),
                order=order3,
                quantity=1,
                notes="Extra marinara",
                is_delivered=False,
            )
            OrderItem.objects.create(
                menu_item=Dish.objects.get(name="Shrimp Scampi"),
                order=order3,
                quantity=2,
                notes="Extra garlic butter",
                is_delivered=False,
            )
            OrderItem.objects.create(
                menu_item=Dish.objects.get(name="Iced Tea"),
                order=order3,
                quantity=1,
                notes="No lemon",
                is_delivered=False,
            )

        # Order 4: Completed Breakfast with discount
        booth_a = Table.objects.filter(number="Booth-A").first()
        if booth_a:
            order4, created = Order.objects.get_or_create(
                table=booth_a,
                status="COMPLETED",
                defaults={
                    "created_at": timezone.now() - timedelta(hours=4),
                    "end_at": timezone.now() - timedelta(hours=3),
                },
            )

            if created:
                OrderItem.objects.create(
                    menu_item=Dish.objects.get(name="Classic Pancakes"),
                    order=order4,
                    quantity=2,
                    notes="Maple syrup on side",
                    is_delivered=True,
                )
                OrderItem.objects.create(
                    menu_item=Dish.objects.get(name="Avocado Toast"),
                    order=order4,
                    quantity=1,
                    notes="Eggs poached hard",
                    is_delivered=True,
                )
                OrderItem.objects.create(
                    menu_item=Dish.objects.get(name="Fresh Orange Juice"),
                    order=order4,
                    quantity=3,
                    notes="No ice",
                    is_delivered=True,
                )
                OrderItem.objects.create(
                    menu_item=Dish.objects.get(name="Chocolate Lava Cake"),
                    order=order4,
                    quantity=1,
                    notes="For dessert",
                    is_delivered=True,
                )
                side_salad = MenuExtra.objects.filter(name="Side Salad").first()
                if side_salad:
                    OrderItem.objects.create(
                        menu_item=Dish.objects.get(name="Chicken Wings"),
                        order=order4,
                        menu_extra=side_salad,
                        quantity=2,
                        notes="Balsamic dressing",
                        is_delivered=True,
                    )
                extra_cheese = MenuExtra.objects.filter(name="Extra Cheese").first()
                if extra_cheese:
                    OrderItem.objects.create(
                        menu_item=Dish.objects.get(name="Caprese Salad"),
                        order=order4,
                        menu_extra=extra_cheese,
                        quantity=3,
                        notes="For avocado toast",
                        is_delivered=True,
                    )

        # Order 5: Refunded Partial Order
        window_1 = Table.objects.filter(number="Window-1").first()
        if window_1:
            order5, created = Order.objects.get_or_create(
                table=window_1,
                status="COMPLETED",
                defaults={
                    "created_at": timezone.now() - timedelta(hours=6),
                    "end_at": timezone.now() - timedelta(hours=5),
                },
            )

            if created:
                OrderItem.objects.create(
                    menu_item=Dish.objects.get(name="Vegetable Curry"),
                    order=order5,
                    quantity=1,
                    notes="Mild spice",
                    is_delivered=True,
                )
                OrderItem.objects.create(
                    menu_item=Dish.objects.get(name="Grilled Salmon"),
                    order=order5,
                    quantity=1,
                    notes="Wrong item delivered - refunded",
                    is_delivered=False,
                )
                OrderItem.objects.create(
                    menu_item=Dish.objects.get(name="Sparkling Water"),
                    order=order5,
                    quantity=1,
                    is_delivered=True,
                )

        self.stdout.write(self.style.SUCCESS("  Created orders and order items"))

    def populate_payments(self):
        self.stdout.write("Populating payments and payment items...")

        # Get orders
        orders = Order.objects.all()[:5]

        if len(orders) >= 1:
            order1 = orders[0]
            if not hasattr(order1, "payment"):
                payment1 = Payment.objects.create(
                    order=order1,
                    payment_method="CARD",
                    payment_status="COMPLETED",
                    sub_total=Decimal("42.50"),
                    discount=Decimal("0.00"),
                    vat_rate=Decimal("10.00"),
                    vat=Decimal("4.25"),
                    currency_type="USD",
                    total=Decimal("46.75"),
                    paid_at=timezone.now() - timedelta(hours=2),
                )

                PaymentItem.objects.create(
                    payment=payment1,
                    menu_item=Dish.objects.get(name="Grilled Salmon"),
                    price=Decimal("18.50"),
                    quantity=1,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("18.50"),
                    charge_description="Grilled Salmon",
                )
                PaymentItem.objects.create(
                    payment=payment1,
                    menu_item=Dish.objects.get(name="Mushroom Risotto"),
                    price=Decimal("16.00"),
                    quantity=1,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("16.00"),
                    charge_description="Mushroom Risotto",
                )
                PaymentItem.objects.create(
                    payment=payment1,
                    menu_item=Dish.objects.get(name="Sparkling Water"),
                    price=Decimal("2.50"),
                    quantity=2,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("5.00"),
                    charge_description="Sparkling Water x2",
                )
                PaymentItem.objects.create(
                    payment=payment1,
                    menu_item=Dish.objects.get(name="Tiramisu"),
                    price=Decimal("7.00"),
                    quantity=1,
                    extras_charges=Decimal("3.00"),
                    total=Decimal("10.00"),
                    charge_description="Tiramisu + Extra Cream",
                )

        if len(orders) >= 2:
            order2 = orders[1]
            if not hasattr(order2, "payment"):
                payment2 = Payment.objects.create(
                    order=order2,
                    payment_method="CARD",
                    payment_status="REFUNDED",
                    sub_total=Decimal("35.50"),
                    discount=Decimal("0.00"),
                    vat_rate=Decimal("10.00"),
                    vat=Decimal("3.55"),
                    currency_type="USD",
                    total=Decimal("39.05"),
                    paid_at=timezone.now() - timedelta(days=1),
                    deleted_at=timezone.now() - timedelta(hours=23),
                )

                PaymentItem.objects.create(
                    payment=payment2,
                    menu_item=Dish.objects.get(name="Ribeye Steak"),
                    price=Decimal("24.00"),
                    quantity=1,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("24.00"),
                    charge_description="Ribeye Steak",
                )
                PaymentItem.objects.create(
                    payment=payment2,
                    menu_item=Dish.objects.get(name="Calamari"),
                    price=Decimal("4.00"),
                    quantity=1,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("4.00"),
                    charge_description="French Fries",
                )
                PaymentItem.objects.create(
                    payment=payment2,
                    menu_item=Dish.objects.get(name="House Red Wine"),
                    price=Decimal("8.00"),
                    quantity=1,
                    extras_charges=Decimal("-4.00"),
                    total=Decimal("4.00"),
                    charge_description="House Red Wine (half refund for corked bottle)",
                )
                PaymentItem.objects.create(
                    payment=payment2,
                    menu_item=None,
                    price=Decimal("0.00"),
                    quantity=1,
                    extras_charges=Decimal("3.50"),
                    total=Decimal("3.50"),
                    charge_description="Delivery Fee",
                )

        if len(orders) >= 3:
            order3 = orders[2]
            if not hasattr(order3, "payment"):
                payment3 = Payment.objects.create(
                    order=order3,
                    payment_method="ONLINE",
                    payment_status="CANCELLED",
                    sub_total=Decimal("28.00"),
                    discount=Decimal("0.00"),
                    vat_rate=Decimal("10.00"),
                    vat=Decimal("2.80"),
                    currency_type="USD",
                    total=Decimal("30.80"),
                    deleted_at=timezone.now() - timedelta(minutes=30),
                )

                PaymentItem.objects.create(
                    payment=payment3,
                    menu_item=Dish.objects.get(name="Chicken Parmesan"),
                    price=Decimal("17.50"),
                    quantity=1,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("17.50"),
                    charge_description="Chicken Parmesan",
                )
                garlic_bread = Dish.objects.filter(name="Garlic Bread").first()
                if not garlic_bread:
                    garlic_bread = MenuExtra.objects.filter(name="Garlic Bread").first()
                PaymentItem.objects.create(
                    payment=payment3,
                    menu_item=None,
                    menu_item_extra=(
                        garlic_bread if isinstance(garlic_bread, MenuExtra) else None
                    ),
                    price=Decimal("2.50"),
                    quantity=2,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("5.00"),
                    charge_description="Garlic Bread x2",
                )
                PaymentItem.objects.create(
                    payment=payment3,
                    menu_item=Dish.objects.get(name="Iced Tea"),
                    price=Decimal("3.50"),
                    quantity=1,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("3.50"),
                    charge_description="Iced Tea",
                )
                PaymentItem.objects.create(
                    payment=payment3,
                    menu_item=None,
                    price=Decimal("0.00"),
                    quantity=1,
                    extras_charges=Decimal("2.00"),
                    total=Decimal("2.00"),
                    charge_description="Service Fee (refunded)",
                )

        if len(orders) >= 4:
            order4 = orders[3]
            if not hasattr(order4, "payment"):
                payment4 = Payment.objects.create(
                    order=order4,
                    payment_method="CASH",
                    payment_status="COMPLETED",
                    sub_total=Decimal("60.50"),
                    discount=Decimal("10.00"),
                    vat_rate=Decimal("10.00"),
                    vat=Decimal("5.05"),
                    currency_type="USD",
                    total=Decimal("55.55"),
                    paid_at=timezone.now() - timedelta(hours=3),
                )

                PaymentItem.objects.create(
                    payment=payment4,
                    menu_item=Dish.objects.get(name="Classic Pancakes"),
                    price=Decimal("8.50"),
                    quantity=2,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("17.00"),
                    charge_description="Classic Pancakes x2",
                )
                PaymentItem.objects.create(
                    payment=payment4,
                    menu_item=Dish.objects.get(name="Avocado Toast"),
                    price=Decimal("9.00"),
                    quantity=1,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("9.00"),
                    charge_description="Avocado Toast",
                )
                PaymentItem.objects.create(
                    payment=payment4,
                    menu_item=Dish.objects.get(name="Fresh Orange Juice"),
                    price=Decimal("4.00"),
                    quantity=3,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("12.00"),
                    charge_description="Orange Juice x3",
                )
                PaymentItem.objects.create(
                    payment=payment4,
                    menu_item=Dish.objects.get(name="Chocolate Lava Cake"),
                    price=Decimal("7.50"),
                    quantity=1,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("7.50"),
                    charge_description="Chocolate Lava Cake",
                )
                PaymentItem.objects.create(
                    payment=payment4,
                    menu_item=None,
                    menu_item_extra=MenuExtra.objects.filter(
                        name="Chicken Wings"
                    ).first(),
                    price=Decimal("3.50"),
                    quantity=2,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("7.00"),
                    charge_description="Chicken Wings x2",
                )
                PaymentItem.objects.create(
                    payment=payment4,
                    menu_item=None,
                    menu_item_extra=MenuExtra.objects.filter(
                        name="Extra Cheese"
                    ).first(),
                    price=Decimal("1.00"),
                    quantity=3,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("3.00"),
                    charge_description="Extra Cheese x3",
                )

        if len(orders) >= 5:
            order5 = orders[4]
            if not hasattr(order5, "payment"):
                payment5 = Payment.objects.create(
                    order=order5,
                    payment_method="CARD",
                    payment_status="REFUNDED",
                    sub_total=Decimal("31.00"),
                    discount=Decimal("0.00"),
                    vat_rate=Decimal("10.00"),
                    vat=Decimal("3.10"),
                    currency_type="USD",
                    total=Decimal("34.10"),
                    paid_at=timezone.now() - timedelta(hours=5),
                    deleted_at=timezone.now() - timedelta(hours=4),
                )

                PaymentItem.objects.create(
                    payment=payment5,
                    menu_item=Dish.objects.get(name="Vegetable Curry"),
                    price=Decimal("15.00"),
                    quantity=1,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("15.00"),
                    charge_description="Vegetable Curry (correct item)",
                )
                PaymentItem.objects.create(
                    payment=payment5,
                    menu_item=Dish.objects.get(name="Grilled Salmon"),
                    price=Decimal("18.50"),
                    quantity=1,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("0.00"),
                    charge_description="Grilled Salmon (refunded - wrong item)",
                )
                PaymentItem.objects.create(
                    payment=payment5,
                    menu_item=Dish.objects.get(name="Sparkling Water"),
                    price=Decimal("2.50"),
                    quantity=1,
                    extras_charges=Decimal("0.00"),
                    total=Decimal("2.50"),
                    charge_description="Sparkling Water",
                )
                PaymentItem.objects.create(
                    payment=payment5,
                    menu_item=None,
                    price=Decimal("0.00"),
                    quantity=1,
                    extras_charges=Decimal("15.00"),
                    total=Decimal("15.00"),
                    charge_description="Partial refund + compensation",
                )

        self.stdout.write(self.style.SUCCESS("  Created payments and payment items"))

    def populate_reservations(self):
        self.stdout.write("Populating reservations...")

        reservations_data = [
            (
                "John Smith",
                "+15551234567",
                4,
                "john.smith@example.com",
                "T2",
                timezone.now() + timedelta(days=2, hours=19),
                "BOOKED",
                None,
                None,
            ),
            (
                "Emily Johnson",
                "+15559876543",
                2,
                "emily.j@example.com",
                "Window-1",
                timezone.now() - timedelta(days=3, hours=-19, minutes=-30),
                "ATTENDED",
                timezone.now() - timedelta(days=5),
                None,
            ),
            (
                "Michael Brown",
                "+15555551234",
                6,
                "michael.b@example.com",
                "Round-1",
                timezone.now() + timedelta(days=1, hours=20),
                "CANCELLED",
                None,
                timezone.now() - timedelta(hours=2),
            ),
            (
                "Sarah Wilson",
                "+15553334455",
                3,
                "sarah.w@example.com",
                "Booth-A",
                timezone.now() - timedelta(days=1, hours=-18, minutes=-45),
                "NOT_ATTENDED",
                None,
                None,
            ),
            (
                "David Lee",
                "+15557778899",
                5,
                "david.lee@example.com",
                "Private-1",
                timezone.now() + timedelta(days=3, hours=20, minutes=30),
                "PENDING",
                None,
                None,
            ),
            (
                "Robert and Maria Garcia",
                "+15556667777",
                2,
                "garcia.family@example.com",
                "Corner-2",
                timezone.now() + timedelta(weeks=1, hours=19),
                "BOOKED",
                None,
                None,
            ),
            (
                "TechSolutions Inc.",
                "+15552468013",
                4,
                "events@techsolutions.com",
                "T3",
                timezone.now() - timedelta(hours=5),
                "ATTENDED",
                timezone.now() - timedelta(days=2),
                None,
            ),
            (
                "Jessica Taylor",
                "+15558765432",
                8,
                "jessica.t@example.com",
                "Round-1",
                timezone.now() + timedelta(hours=1),
                "CANCELLED",
                None,
                timezone.now() - timedelta(minutes=30),
            ),
            (
                "Thomas Anderson",
                "+15551231234",
                4,
                "thomas.a@example.com",
                "Window-1",
                timezone.now() - timedelta(weeks=1, hours=-19, minutes=-15),
                "ATTENDED",
                timezone.now() - timedelta(weeks=2),
                None,
            ),
            (
                "Smith Family Reunion",
                "+15554443322",
                12,
                "smith.family@example.com",
                "Private-1",
                timezone.now() + timedelta(weeks=2, hours=12),
                "BOOKED",
                None,
                None,
            ),
        ]

        for (
            name,
            phone,
            customer_num,
            email,
            table_num,
            res_date,
            status,
            created,
            cancelled,
        ) in reservations_data:
            table = Table.objects.filter(number=table_num).first()
            if table:
                res, created_flag = Reservation.objects.get_or_create(
                    name=name,
                    phone_number=phone,
                    email=email,
                    table=table,
                    reservation_date=res_date,
                    defaults={
                        "customer_number": customer_num,
                        "status": status,
                        "cancelled_at": cancelled,
                    },
                )
                if created_flag and created:
                    res.created_at = created
                    res.save()

        self.stdout.write(
            self.style.SUCCESS(f"  Created {len(reservations_data)} reservations")
        )
