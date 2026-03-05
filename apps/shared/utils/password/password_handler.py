from django.contrib.auth.hashers import make_password, check_password

class PasswordService:
    @staticmethod
    def hash_password(plain_password: str) -> str:
        """
        Hash a password using Django's password hasher
        """
        return make_password(plain_password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against Django's hashed password
        """
        return check_password(plain_password, hashed_password)
