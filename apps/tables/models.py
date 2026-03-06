from django.db import models
from django.core.validators import RegexValidator


class Table(models.Model):
    capacity = models.IntegerField()
    number = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]-\d{2}$',
                message='Use format like T-01, B-02, etc.',
                code='invalid_table_number'
            )
        ]
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tables"
        verbose_name = "Table"
        verbose_name_plural = "Tables"
        ordering = ["number"]
        indexes = [
            models.Index(fields=["number"]),
            models.Index(fields=["is_available"]),
        ]

    def __str__(self):
        return f"Table {self.number} ({self.capacity} capacity)"
