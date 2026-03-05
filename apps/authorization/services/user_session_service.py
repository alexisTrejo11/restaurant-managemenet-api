from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from django.utils import timezone


class SessionService:
    @staticmethod
    def invalidate_all_sessions(user):
        try:
            tokens = OutstandingToken.objects.filter(user=user)
            for token in tokens:
                if not BlacklistedToken.objects.filter(token=token).exists():
                    BlacklistedToken.objects.create(token=token)

            # Delete outstanding tokens --> tokens.delete()
            return True
        except Exception as e:
            raise Exception(f"Error invalidating all tokens: {str(e)}")

    @staticmethod
    def invalidate_session(refresh_token: str) -> bool:
        if (
            not refresh_token
            or not isinstance(refresh_token, str)
            or refresh_token.strip() == ""
        ):
            raise ValueError("Invalid refresh token provided")

        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()

            access_token = AccessToken(refresh.access_token)
            access_token.set_exp(from_time=timezone.now())

            return True
        except TokenError as e:
            raise Exception(f"Token error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error invalidating current tokens: {str(e)}")

    @staticmethod
    def refresh_session(refresh_token, user):
        """
        Refreshes the session by generating a new access token.
        """
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = refresh.access_token

            new_access_token["user_id"] = user.id
            new_access_token["email"] = user.email
            new_access_token["role"] = user.role

            return {
                "refresh_token": refresh_token,
                "access_token": str(new_access_token),
            }
        except Exception as e:
            raise Exception(f"Error refreshing the session: {str(e)}")

    @staticmethod
    def create_session(user) -> dict:
        refresh_token = RefreshToken.for_user(user)
        access_token = AccessToken.for_user(user)

        access_token["user_id"] = user.id
        access_token["email"] = user.email
        access_token["role"] = user.role

        return {
            "refresh_token": str(refresh_token),
            "access_token": str(access_token),
        }
