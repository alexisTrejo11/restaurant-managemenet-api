import logging
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import User
from .serializers import (
    UserCreateUpdateSerializer,
    UserResponseSerializer,
    CreateUserResponseSerializer,
    UpdateUserResponseSerializer,
    RetrieveUserResponseSerializer,
    ListUserResponseSerializer,
    PaginatedUsersResponseSerializer,
)
from .services import UserService
from apps.shared.response import (
    NoContentResponseSerializer,
    ValidationErrorResponseSerializer,
    NotFoundErrorResponseSerializer,
    UnauthorizedErrorResponseSerializer,
    ForbiddenErrorResponseSerializer,
    ServerErrorResponseSerializer,
)


logger = logging.getLogger(__name__)

COMMON_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: UnauthorizedErrorResponseSerializer,
    status.HTTP_403_FORBIDDEN: ForbiddenErrorResponseSerializer,
    status.HTTP_500_INTERNAL_SERVER_ERROR: ServerErrorResponseSerializer,
}


@extend_schema(tags=["Users"])
class UserModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing system users.

    Provides CRUD operations with comprehensive logging and response formatting.
    All endpoints require admin authentication.
    """

    queryset = User.objects.all()
    serializer_class = UserResponseSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = PageNumberPagination

    @extend_schema(
        operation_id="list_users",
        summary="List all users",
        description="Retrieves a list of all users with pagination support.",
        parameters=[
            OpenApiParameter(
                name="role",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by user role",
                required=False,
            ),
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by active status",
                required=False,
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of results per page",
                required=False,
            ),
        ],
        responses={
            200: PaginatedUsersResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def list(self, request, *args, **kwargs):
        """List all users with optional filtering."""
        admin = request.user
        logger.info(
            f"Admin {admin.id} listing users. Query params: {request.query_params}",
            extra={"admin_id": admin.id},
        )
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer_data = self.get_serializer(queryset, many=True).data
        response_data = PaginatedUsersResponseSerializer(serializer_data).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="retrieve_user",
        summary="Get user details",
        description="Retrieves detailed information for a specific user.",
        responses={
            200: RetrieveUserResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific user."""
        admin = request.user
        user = self.get_object()

        logger.info(
            f"Admin {admin.id} retrieved user {user.id}",
            extra={"admin_id": admin.id, "user_id": user.id},
        )

        serializer = self.get_serializer(user)
        response_data = RetrieveUserResponseSerializer(serializer.data).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="create_user",
        summary="Create new user",
        description="Creates a new user account with the provided information.",
        request=UserCreateUpdateSerializer,
        responses={
            201: CreateUserResponseSerializer,
            400: ValidationErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def create(self, request, *args, **kwargs):
        """Create a new user."""
        admin = request.user
        logger.info(f"Admin {admin.id} init creation of user.")

        serializer = UserCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        UserService.validate_user_creation(serializer.validated_data)
        user = serializer.save()

        logger.info(
            f"Admin {admin.id} successfully create new User {user.id}",
            extra={"user_id": user.id, "admin_id": admin.id},
        )

        response_data = CreateUserResponseSerializer(
            UserResponseSerializer(user).data
        ).data
        return Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="update_user",
        summary="Update user",
        description="Updates an existing user's information. Supports partial updates.",
        request=UserCreateUpdateSerializer,
        responses={
            200: UpdateUserResponseSerializer,
            400: ValidationErrorResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def update(self, request, *args, **kwargs):
        """Update an existing user (full or partial)."""
        admin = request.user
        user = self.get_object()

        logger.info(
            f"Admin {admin.id} updating user {user.id}. Data: {request.data}",
            extra={"admin_id": admin.id, "user_id": user.id},
        )

        serializer = UserCreateUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        UserService.validate_user_update(
            user_data=serializer.validated_data, current_user=user
        )
        updated_user = serializer.save()

        logger.info(
            f"Admin {admin.id} successfully updated user {user.id}",
            extra={"admin_id": admin.id, "user_id": user.id},
        )

        response_data = UpdateUserResponseSerializer(
            UserResponseSerializer(updated_user).data
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="delete_user",
        summary="Delete user",
        description="Deactivates a user account (soft delete).",
        responses={
            204: NoContentResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a user (soft delete by setting is_active to False)."""
        admin = request.user
        user = self.get_object()

        logger.warning(
            f"Admin {admin.id} initiating deletion of user {user.id}",
            extra={"admin_id": admin.id, "user_id": user.id},
        )

        user.is_active = False
        user.save()

        logger.info(
            f"Admin {admin.id} successfully deleted user {user.id}",
            extra={"admin_id": admin.id, "user_id": user.id},
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
