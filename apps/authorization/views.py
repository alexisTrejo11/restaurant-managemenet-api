import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import (
    SignUpSerializer,
    LoginSerializer,
    TokenDataSerializer,
    LogoutRequestSerializer,
    SignupResponseSerializer,
    LoginResponseSerializer,
    LogoutResponseSerializer,
    LogoutAllResponseSerializer,
)
from .services import AuthService, SessionService
from apps.shared.response.serializers import ApiResponseSerializer

logger = logging.getLogger(__name__)

# Global error response mapping to reduce verbosity
COMMON_RESPONSES = {
    status.HTTP_400_BAD_REQUEST: ApiResponseSerializer,
    status.HTTP_401_UNAUTHORIZED: ApiResponseSerializer,
    status.HTTP_500_INTERNAL_SERVER_ERROR: ApiResponseSerializer,
}


@extend_schema(
    operation_id="signup",
    summary="User registration",
    description="Create a new user account. Validates email uniqueness and password strength. Returns user data with authentication tokens upon successful registration.",
    request=SignUpSerializer,
    responses={
        201: SignupResponseSerializer,
        **COMMON_RESPONSES,
    },
    tags=["Authentication"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    """
    Register a new user account.

    Validates that:
    - Email is unique and valid
    - Password meets security requirements
    - Password confirmation matches

    Returns user account information with JWT tokens for session management.
    """
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    validation_result = AuthService.validate_signup_data(serializer.validated_data)
    if validation_result.is_failure():
        return Response(
            {
                "success": False,
                "message": validation_result.get_error_msg(),
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = serializer.save()
    user_session = SessionService.create_session(user)

    logger.info(f"User {user.id} successfully registered.")

    response_data = SignupResponseSerializer(
        {
            "data": user_session,
            "message": "Account successfully created",
        }
    ).data
    return Response(response_data, status=status.HTTP_201_CREATED)


@extend_schema(
    operation_id="login",
    summary="User login",
    description="Authenticate user with email and password. Returns user information with JWT tokens upon successful authentication.",
    request=LoginSerializer,
    responses={
        200: LoginResponseSerializer,
        **COMMON_RESPONSES,
    },
    tags=["Authentication"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Authenticate user and create session.

    Validates credentials against database and creates JWT tokens for subsequent requests.
    Returns user account data along with refresh and access tokens.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    auth_result = AuthService.authenticate_user(serializer.validated_data)
    if auth_result.is_failure():
        return Response(
            {
                "success": False,
                "message": auth_result.get_error_msg(),
                "data": None,
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user = auth_result.get_data()
    user_session = SessionService.create_session(user)

    logger.info(f"User {user.id} successfully logged in.")

    response_data = LoginResponseSerializer(
        {
            "data": user_session,
            "message": "Login successful",
        }
    ).data
    return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id="logout",
    summary="User logout",
    description="Invalidate a specific user session using the provided refresh token. User remains authenticated otherwise.",
    request=LogoutRequestSerializer,
    responses={
        200: LogoutResponseSerializer,
        **COMMON_RESPONSES,
    },
    tags=["Authentication"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user from current session.

    Invalidates the refresh token, preventing further use of the associated access token after expiration.
    User must provide the refresh token to be invalidated.
    """
    serializer = LogoutRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    refresh_token = serializer.validated_data.get("refresh_token")
    SessionService.invalidate_session(refresh_token)

    user_id = getattr(request.user, "id", "Anonymous")
    logger.info(f"User {user_id} logged out from one session.")

    response_data = LogoutResponseSerializer(
        {
            "data": {"message": "Successfully logged out from this session"},
            "message": "Logout successful",
        }
    ).data
    return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id="logout_all",
    summary="Logout all sessions",
    description="Invalidate all active sessions for the authenticated user. User must login again to access the API.",
    request={
        "type": "object",
        "properties": {},
        "description": "No request body required",
    },
    responses={
        200: LogoutAllResponseSerializer,
        **COMMON_RESPONSES,
    },
    tags=["Authentication"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_all(request):
    """
    Logout user from all sessions.

    Invalidates all active refresh tokens for the user, requiring re-authentication for all devices/clients.
    This is useful for security concerns or password changes.
    """
    user = request.user
    SessionService.invalidate_all_sessions(user)

    logger.info(f"User {user.id} logged out from all sessions.")

    response_data = LogoutAllResponseSerializer(
        {
            "data": {"message": "All sessions successfully logged out"},
        }
    ).data
    return Response(response_data, status=status.HTTP_200_OK)
