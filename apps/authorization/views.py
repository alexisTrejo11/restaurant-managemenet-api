from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    SignUpSerializer,
    LoginSerializer,
    TokenDataSerializer,
    LogoutRequestSerializer,
)
from .services import AuthService
from .services import SessionService
from apps.shared.response import ResponseWrapper
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .documentation.auth_doc_data import (
    SignupDocumentationData as SignupDocData,
    LoginDocumentationData as LogDocData,
    LogoutDocumentationData as LogoutDocData,
    LogoutAllDocumentationData as LogoutAllDocData,
)


@swagger_auto_schema(
    method=SignupDocData.signup_method,
    operation_id=SignupDocData.singup_operation_id,
    operation_summary=SignupDocData.singup_operation_summary,
    operation_description=SignupDocData.singup_operation_description,
    request_body=SignUpSerializer,
    responses=SignupDocData.signup_responses,
    tags=["Authentication"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    validation_result = AuthService.validate_signup_data(serializer.validated_data)
    if validation_result.is_failure():
        return ResponseWrapper.bad_request(message=validation_result.get_error_msg())

    user = serializer.save()
    user_session = SessionService.create_session(user)

    return ResponseWrapper.success(
        data=user_session, message="Signup Successfully Processed"
    )


@swagger_auto_schema(
    method=LogDocData.method,
    operation_id=LogDocData.operation_id,
    operation_summary=LogDocData.operation_summary,
    operation_description=LogDocData.operation_description,
    request_body=LoginSerializer,
    responses=LogDocData.responses,
    tags=["Authentication"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    auth_result = AuthService.authenticate_user(serializer.validated_data)
    if auth_result.is_failure():
        return ResponseWrapper.bad_request(message=auth_result.get_error_msg())

    user = auth_result.get_data()
    user_session = SessionService.create_session(user)

    serializer = TokenDataSerializer(user_session)
    return ResponseWrapper.success(
        data=serializer.data, message="Login Successfully Processed"
    )


@swagger_auto_schema(
    method=LogoutDocData.method,
    operation_id=LogoutDocData.operation_id,
    operation_summary=LogoutDocData.operation_summary,
    operation_description=LogoutDocData.operation_description,
    request_body=LogoutRequestSerializer,
    responses=LogoutDocData.logout_responses,
    tags=["Authentication"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    serializer = LogoutRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    refresh_token = serializer.validated_data.get("refresh_token")
    SessionService.invalidate_session(refresh_token)
    return ResponseWrapper.success(message="Logout successfully processed")


@swagger_auto_schema(
    method=LogoutAllDocData.method,
    operation_id=LogoutAllDocData.operation_id,
    operation_summary=LogoutAllDocData.operation_summary,
    operation_description=LogoutAllDocData.operation_description,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT, properties={}, description="No request body required"
    ),
    responses=LogoutAllDocData.logout_all_responses,
    tags=["Authentication"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_all(request):
    user = request.user
    SessionService.invalidate_all_sessions(user)
    return ResponseWrapper.success(message="All sessions logged out.")
