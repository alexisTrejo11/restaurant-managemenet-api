import logging
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, permissions, status

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from apps.shared.response import ResponseWrapper

from .models import User
from .serializers import UserCreateUpdateSerializer, UserResponseSerializer
from .documentation.user_documentation_data import UserDocumentationData
from .services import UserService


logger = logging.getLogger(__name__)


class UserModelViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserResponseSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = PageNumberPagination

    @swagger_auto_schema(
        operation_id="list_users",
        operation_summary=UserDocumentationData.list_operation_summary,
        operation_description=UserDocumentationData.list_operation_description,
        manual_parameters=[
            openapi.Parameter(
                "role",
                openapi.IN_QUERY,
                description="Filter by user role",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "is_active",
                openapi.IN_QUERY,
                description="Filter by active status",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Number of results per page",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            status.HTTP_200_OK: UserDocumentationData.user_list_response,
            status.HTTP_401_UNAUTHORIZED: UserDocumentationData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: UserDocumentationData.forbidden_reponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: UserDocumentationData.server_error_reponse,
        },
        tags=["User Management"],
    )
    def list(self, request, *args, **kwargs):
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
        return ResponseWrapper.found(data=serializer_data, entity="User List")

    @swagger_auto_schema(
        operation_id="retrieve_user",
        operation_summary=UserDocumentationData.retrieve_operation_summary,
        operation_description=UserDocumentationData.retrieve_operation_description,
        responses={
            status.HTTP_200_OK: UserDocumentationData.user_response,
            status.HTTP_401_UNAUTHORIZED: UserDocumentationData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: UserDocumentationData.forbidden_reponse,
            status.HTTP_404_NOT_FOUND: UserDocumentationData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: UserDocumentationData.server_error_reponse,
        },
        tags=["User Management"],
    )
    def retrieve(self, request, *args, **kwargs):
        admin = request.user
        user = self.get_object()

        logger.info(
            f"Admin {admin.id} retrieved user {user.id}",
            extra={"admin_id": admin.id, "user_id": user.id},
        )

        serializer = self.get_serializer(user)
        return ResponseWrapper.found(data=serializer.data, entity="User")

    @swagger_auto_schema(
        operation_id="create_user",
        operation_summary=UserDocumentationData.create_operation_summary,
        operation_description=UserDocumentationData.create_operation_description,
        request_body=UserCreateUpdateSerializer,
        responses={
            status.HTTP_201_CREATED: UserDocumentationData.user_response,
            status.HTTP_400_BAD_REQUEST: UserDocumentationData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: UserDocumentationData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: UserDocumentationData.forbidden_reponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: UserDocumentationData.server_error_reponse,
        },
        tags=["User Management"],
    )
    def create(self, request, *args, **kwargs):
        admin = request.user
        logger.info(f"Admin {admin.id} init creation of user.")

        serializer = UserCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        UserService.validate_user_creation(serializer.validated_data)
        user = serializer.save()

        logger.info(
            f"Admin {admin.id} succesfully create new User {user.id}",
            extra={"user_id": user.id, "admin_id": admin.id},
        )

        response_data = UserResponseSerializer(user).data
        return ResponseWrapper.created(data=response_data, entity="User")

    @swagger_auto_schema(
        operation_id="update_user",
        operation_summary=UserDocumentationData.update_operation_summary,
        operation_description=UserDocumentationData.update_operation_description,
        request_body=UserCreateUpdateSerializer,
        responses={
            status.HTTP_200_OK: UserDocumentationData.user_response,
            status.HTTP_400_BAD_REQUEST: UserDocumentationData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: UserDocumentationData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: UserDocumentationData.forbidden_reponse,
            status.HTTP_404_NOT_FOUND: UserDocumentationData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: UserDocumentationData.server_error_reponse,
        },
        tags=["User Management"],
    )
    def update(self, request, *args, **kwargs):
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

        return ResponseWrapper.updated(
            data=UserResponseSerializer(updated_user).data,
            entity="User",
        )

    @swagger_auto_schema(
        operation_id="delete_user",
        operation_summary=UserDocumentationData.destroy_operation_summary,
        operation_description=UserDocumentationData.destroy_operation_description,
        responses={
            status.HTTP_204_NO_CONTENT: UserDocumentationData.success_no_data_response,
            status.HTTP_401_UNAUTHORIZED: UserDocumentationData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: UserDocumentationData.forbidden_reponse,
            status.HTTP_404_NOT_FOUND: UserDocumentationData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: UserDocumentationData.server_error_reponse,
        },
        tags=["User Management"],
    )
    def destroy(self, request, *args, **kwargs):
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

        return ResponseWrapper.deleted("User")
