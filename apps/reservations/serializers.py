from rest_framework import serializers
from .models import Reservation

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            'id', 'name', 'phone_number', 'customer_number', 
            'email', 'table', 'reservation_date', 'status', 
            'created_at', 'cancelled_at'
        ]
        read_only_fields = ['created_at', 'cancelled_at', 'table', 'status']

    def validate_email(self, value):
        """
        Check if the email format is valid.
        """
        if not serializers.EmailField().to_internal_value(value):
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def validate_phone_number(self, value):
        """
        Basic validation for phone number format (e.g., digits only, or a common pattern).
        """
        if not all(char.isdigit() or char == '+' for char in value):
            raise serializers.ValidationError("Phone number must contain only digits and optionally a '+' sign.")
        return value

    def validate_customer_number(self, value):
        """
        Ensure customer_number is a positive integer.
        """
        if value <= 0:
            raise serializers.ValidationError("Customer number must be a positive integer.")
        return value

    def validate_reservation_date(self, value):
        """
        Ensure reservation_date is in the future for new reservations,
        or handle past dates appropriately for updates (if needed).
        """
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError("Reservation date cannot be in the past.")
        return value
