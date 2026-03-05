from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.shared.response.api_response import ApiResponse
from apps.shared.response.api_response_serializers import ApiResponseSerializer

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "password2"]
        extra_kwargs = {"email": {"required": True}, "first_name": {"required": True}}

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden"}
            )
        return attrs

    def create(self, validated_data):
        validated_data["username"] = validated_data["email"]
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["full_name"] = user.get_full_name()
        return token


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True
    )


class TokenDataSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        help_text="Refresh token for obtaining new access tokens."
    )
    access_token = serializers.CharField(
        help_text="Access token for authenticating subsequent requests."
    )


class ApiResponseWithTokensSerializer(ApiResponseSerializer):
    """
    ApiResponse serializer specifically for authentication responses with tokens.
    """

    class TokenDataSerializer(serializers.Serializer):
        refresh_token = serializers.CharField(help_text="JWT refresh token")
        access_token = serializers.CharField(help_text="JWT access token")

    data = TokenDataSerializer(help_text="Authentication tokens")


class ApiResponseWithUserSerializer(ApiResponseSerializer):
    """
    ApiResponse serializer for user-related responses.
    """

    class UserDataSerializer(serializers.Serializer):
        id = serializers.IntegerField(help_text="User ID")
        email = serializers.EmailField(help_text="User email address")
        username = serializers.CharField(help_text="Username", required=False)
        first_name = serializers.CharField(help_text="First name", required=False)
        last_name = serializers.CharField(help_text="Last name", required=False)

    data = UserDataSerializer(help_text="User information")


class LogoutRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        help_text="Refresh token to be invalidated", required=True, write_only=True
    )


class LogoutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        help_text="Refresh token to be invalidated", required=True, write_only=True
    )


class LogoutResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(
        help_text="Indicates if the logout was successful."
    )
    message = serializers.CharField(
        help_text="Confirmation message for the logout operation."
    )
    data = serializers.JSONField(
        help_text="Additional data (usually null for logout).", allow_null=True
    )
    timestamp = serializers.CharField(help_text="ISO timestamp of the response.")
    status_code = serializers.IntegerField(help_text="HTTP status code.")
    metadata = serializers.DictField(help_text="Additional metadata.", required=False)


class LogoutErrorResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(
        default=False, help_text="Indicates if the request was successful."
    )
    message = serializers.CharField(help_text="Error message describing the issue.")
    data = serializers.JSONField(help_text="Error details (if any).", allow_null=True)
    timestamp = serializers.CharField(help_text="ISO timestamp of the response.")
    status_code = serializers.IntegerField(help_text="HTTP status code.")
    metadata = serializers.DictField(help_text="Additional metadata.", required=False)
