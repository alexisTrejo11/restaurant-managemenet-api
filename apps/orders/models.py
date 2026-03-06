from django.db import models
from django.utils import timezone


class Order(models.Model):
    STATUS_CHOICES = [
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    table = models.ForeignKey(
        "tables.Table",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    end_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "orders"
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order {self.id} - Table {self.table.number}"

    def set_as_complete(self):
        self.status = "COMPLETED"
        self.end_at = timezone.now()

    def set_as_cancelled(self):
        self.status = "CANCELLED"
        self.end_at = timezone.now()


class OrderItem(models.Model):
    menu_item = models.ForeignKey(
        "menu.Dish", on_delete=models.PROTECT, related_name="order_items"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items", default=""
    )
    added_at = models.DateTimeField(auto_now_add=True)
    menu_extra = models.ForeignKey(
        "menu.MenuExtra",
        on_delete=models.PROTECT,
        related_name="order_items",
        null=True,
    )
    quantity = models.IntegerField(default=1)
    notes = models.TextField(null=True, blank=True)
    is_delivered = models.BooleanField(default=False)

    def set_as_delivered(self):
        self.is_delivered = True

    class Meta:
        db_table = "order_items"
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f'{self.menu_item.name} - Order {self.order.id if self.order else "Unknown"}'
