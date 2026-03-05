from apps.users.models import User
from apps.shared.utils.result import Result


class AuthService:
    @staticmethod
    def validate_signup_data(validated_data) -> Result:
        """Validates registration data before creating the user"""
        email = validated_data["email"]
        password = validated_data["password"]
        password2 = validated_data["password2"]

        if User.objects.filter(email=email).exists():
            return Result.error("The email is already registered")

        if password != password2:
            return Result.error("Passwords do not match")

        return Result.success()

    @staticmethod
    def authenticate_user(validated_data) -> Result:
        email = validated_data["email"]
        password = validated_data["password"]

        user = User.objects.filter(email=email).first()
        if not user:
            return Result.error("Invalid credentials")

        if not user.check_password(password):
            return Result.error("Invalid credentials")

        if not user.is_active:
            return Result.error("Account is disabled.")

        return Result.success(data=user)
