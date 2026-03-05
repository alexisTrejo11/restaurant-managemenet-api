from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User

class UserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'gender',
            'email',
            'password',
            'birth_date',
            'role',
            'phone_number',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'role': {'required': True},
        }

    def validate_email(self, value):
        """Valida que el email sea único (el modelo ya lo hace, pero DRF muestra mejor error)."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    def validate_password(self, value):
        """Ejemplo de validación básica de contraseña (ajusta según tus requisitos)."""
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return value

    def create(self, validated_data):
        """Hashea la contraseña antes de guardar (esto es estándar de Django, no lógica de negocio)."""
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Hashea la contraseña si se proporciona en la actualización."""
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)
    
class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'gender',
            'email',
            'birth_date',
            'role',
            'joined_at',
            'last_login',
            'phone_number',
        ]
        read_only_fields = ['joined_at', 'last_login']
