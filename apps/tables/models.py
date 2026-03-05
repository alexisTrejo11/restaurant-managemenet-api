from django.db import models

class Table(models.Model):
    capacity = models.IntegerField()
    number = models.CharField(unique=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        db_table = 'tables'
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'

    def __str__(self):
        return f'Table {self.number} ({self.capacity} capacity)'

