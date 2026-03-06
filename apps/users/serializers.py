from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from apps.shared.response.serializers import (
    CreatedResponseSerializer,
    SuccessResponseSerializer,
    PaginatedResponseSerializer,
)
from .models import User


class UserResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with comprehensive field documentation.

    Used for retrieving user data in responses.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "email",
            "birth_date",
            "role",
            "joined_at",
            "last_login",
            "phone_number",
        ]
        read_only_fields = ["id", "joined_at", "last_login"]
        extra_kwargs = {
            "first_name": {
                "help_text": "User's first name",
            },
            "last_name": {
                "help_text": "User's last name",
            },
            "email": {
                "help_text": "User's email address",
            },
            "phone_number": {
                "help_text": "User's phone number",
            },
            "gender": {
                "help_text": "User's gender",
            },
            "role": {
                "help_text": "User's role in the system",
            },
            "birth_date": {
                "help_text": "User's birth date",
            },
            "joined_at": {
                "help_text": "Account creation timestamp",
            },
            "last_login": {
                "help_text": "Last login timestamp",
            },
        }


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating User instances.

    Handles password hashing and validation.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="User password (minimum 8 characters)",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "email",
            "password",
            "birth_date",
            "role",
            "phone_number",
        ]
        extra_kwargs = {
            "email": {
                "required": True,
                "help_text": "Unique email address",
            },
            "role": {
                "required": True,
                "help_text": "User role (admin, staff, user)",
            },
            "first_name": {
                "help_text": "User's first name",
            },
            "last_name": {
                "help_text": "User's last name",
            },
            "birth_date": {
                "required": False,
                "help_text": "User's date of birth",
            },
            "gender": {
                "required": False,
                "help_text": "User's gender (M/F/O)",
            },
            "phone_number": {
                "required": False,
                "help_text": "User's contact phone number",
            },
        }

    def validate_email(self, value):
        """Ensure email is unique in the system."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        """Validate password meets security requirements."""
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        if value.isdigit():
            raise serializers.ValidationError("Password cannot contain only numbers.")
        return value

    def create(self, validated_data):
        """Hash password before creating user."""
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Hash password if provided during update."""
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().update(instance, validated_data)


# Response Serializers


class BaseSingleUserResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing a single user."""

    data = UserResponseSerializer(help_text="User details", required=True, many=False)

    class Meta:
        abstract = True


class BaseUserListResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing multiple users."""

    data = UserResponseSerializer(help_text="List of users", required=True, many=True)

    class Meta:
        abstract = True


class CreateUserResponseSerializer(
    CreatedResponseSerializer, BaseSingleUserResponseSerializer
):
    """
    Response serializer for user creation (201 Created).

    Example:
        {
            "data": {
                "id": 1,
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "admin",
                "joined_at": "2024-01-01T12:00:00Z",
                "last_login": null,
                "phone_number": "+1234567890",
                "birth_date": "1990-01-15",
                "gender": "M"
            },
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 201,
            "message": "User successfully created",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message",
        default="User successfully created",
    )

    class Meta:
        ref_name = "CreateUserResponse"


class UpdateUserResponseSerializer(BaseSingleUserResponseSerializer):
    """
    Response serializer for user update (200 OK).

    Example:
        {
            "data": {
                "id": 1,
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "admin",
                "joined_at": "2024-01-01T12:00:00Z",
                "last_login": "2024-03-06T10:30:00Z",
                "phone_number": "+1234567890",
                "birth_date": "1990-01-15",
                "gender": "M"
            },
            "timestamp": "2024-03-06T10:30:00Z",
            "success": true,
            "status_code": 200,
            "message": "User successfully updated",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message",
        default="User successfully updated",
    )

    class Meta:
        ref_name = "UpdateUserResponse"


class RetrieveUserResponseSerializer(BaseSingleUserResponseSerializer):
    """
    Response serializer for single user retrieval (200 OK).

    Example:
        {
            "data": {
                "id": 1,
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "admin",
                "joined_at": "2024-01-01T12:00:00Z",
                "last_login": "2024-03-06T10:30:00Z",
                "phone_number": "+1234567890",
                "birth_date": "1990-01-15",
                "gender": "M"
            },
            "timestamp": "2024-03-06T10:30:00Z",
            "success": true,
            "status_code": 200,
            "message": "User successfully retrieved",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message",
        default="User successfully retrieved",
    )

    class Meta:
        ref_name = "RetrieveUserResponse"


class ListUserResponseSerializer(BaseUserListResponseSerializer):
    """
    Response serializer for multiple users retrieval (200 OK).

    Example:
        {
            "data": [
                {
                    "id": 1,
                    "email": "john.doe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "role": "admin",
                    "joined_at": "2024-01-01T12:00:00Z",
                    "last_login": "2024-03-06T10:30:00Z",
                    "phone_number": "+1234567890",
                    "birth_date": "1990-01-15",
                    "gender": "M"
                }
            ],
            "timestamp": "2024-03-06T10:30:00Z",
            "success": true,
            "status_code": 200,
            "message": "Users successfully retrieved",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message",
        default="Users successfully retrieved",
    )

    class Meta:
        ref_name = "ListUserResponse"


class PaginatedUsersResponseSerializer(PaginatedResponseSerializer):
    """
    Response serializer for paginated user list (200 OK).

    Example:
        {
            "data": [
                {
                    "id": 1,
                    "email": "john.doe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "role": "admin",
                    "joined_at": "2024-01-01T12:00:00Z",
                    "last_login": "2024-03-06T10:30:00Z",
                    "phone_number": "+1234567890",
                    "birth_date": "1990-01-15",
                    "gender": "M"
                }
            ],
            "timestamp": "2024-03-06T10:30:00Z",
            "success": true,
            "status_code": 200,
            "message": "Users successfully retrieved",
            "metadata": {
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total_count": 100,
                    "total_pages": 5,
                    "has_next": true,
                    "has_previous": false
                }
            }
        }
    """

    data = UserResponseSerializer(
        help_text="Paginated list of users", required=True, many=True
    )

    message = serializers.CharField(
        help_text="Success message",
        default="Users successfully retrieved",
    )

    class Meta:
        ref_name = "PaginatedUsersResponse"
