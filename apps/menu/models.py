from django.db import models

class Dish(models.Model):
    CATEGORY_CHOICES = [
        ('DRINKS', 'Drinks'),
        ('ALCOHOL_DRINKS', 'Alcohol Drinks'),
        ('BREAKFASTS', 'Breakfasts'),
        ('STARTERS', 'Starters'),
        ('MEALS', 'Meals'),
        ('DESSERTS', 'Desserts'),
        ('EXTRAS', 'Extras'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('DRAFT', 'Draft'),
    ]
    
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=255, blank=True, default='')
    description = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        db_table = 'dishes'
        verbose_name = 'Dish'
        verbose_name_plural = 'Dishes'

    def __str__(self):
        return self.name


class MenuExtra(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        db_table = 'menu_extras'
        verbose_name = 'Menu Extra'
        verbose_name_plural = 'Menu Extras'

    def __str__(self):
        return self.name