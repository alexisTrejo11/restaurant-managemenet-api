from rest_framework import serializers
from decimal import Decimal
from .models import Dish
from .services import DishService
from django.core.exceptions import ValidationError


class DishSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )

    class Meta:
        model = Dish
        fields = [
            "id",
            "image",
            "name",
            "price",
            "description",
            "category",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "name": {"trim_whitespace": True, "min_length": 3, "max_length": 255},
            "description": {
                "trim_whitespace": True,
                "allow_blank": True,
                "required": False,
            },
        }

    def validate(self, attrs):
        """Validación cruzada entre campos"""
        if attrs.get("status") == "INACTIVE" and attrs.get("price", 0) > 100000:
            raise serializers.ValidationError(
                {"price": "Inactive items cannot have price > 100,000"}
            )
        return attrs

    def validate_name(self, value):
        """Validación personalizada del nombre"""
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long")
        return value.title()

    def validate_price(self, value):
        """Valida que el precio sea positivo"""
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("El precio debe ser mayor a 0")
        return value

    def validate_category(self, value):
        """Valida que la categoría sea válida (case-insensitive)"""
        return DishService.validate_category(value.upper())

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Actualiza un ítem del menú con validación de negocio"""
        try:
            return DishService.update_menu_item(instance, **validated_data)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
