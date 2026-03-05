from rest_framework import viewsets
from .models import Table
from .serializers import TableSerializer
from apps.shared.response import ResponseWrapper
from .services.table_service import TableService
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from .serializers import TableSerializer
from .documentation.table_documentation_data import (
    TableDocumentationData as TableDocData,
)

logger = logging.getLogger(__name__)


class TableViews(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    lookup_field = "number"
    lookup_url_kwarg = "number"

    @swagger_auto_schema(
        operation_id="list_tables",
        operation_summary=TableDocData.list_operation_summary,
        operation_description=TableDocData.list_operation_description,
        responses={
            status.HTTP_200_OK: TableDocData.list_response,
            status.HTTP_401_UNAUTHORIZED: TableDocData.unauthorized_response,
            status.HTTP_403_FORBIDDEN: TableDocData.forbidden_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: TableDocData.server_error_response,
        },
        tags=["Tables"],
    )
    def list(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting table list.")

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        logger.info(f"Returning {len(queryset)} tables.")
        return ResponseWrapper.found(
            data=serializer.data,
            entity="Table List",
        )

    @swagger_auto_schema(
        operation_id="retrieve_table",
        operation_summary=TableDocData.retrieve_operation_summary,
        operation_description=TableDocData.retrieve_operation_description,
        responses={
            status.HTTP_200_OK: TableDocData.success_response,
            status.HTTP_404_NOT_FOUND: TableDocData.not_found_response,
            status.HTTP_401_UNAUTHORIZED: TableDocData.unauthorized_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: TableDocData.server_error_response,
        },
        tags=["Tables"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(
            f"User {user_id} is requesting details for table ID: {instance.id}."
        )

        serializer = self.get_serializer(instance)

        logger.info(f"Returning details for table ID: {instance.id}.")
        return ResponseWrapper.found(
            data=serializer.data,
            entity=f"Table {instance.id}",
        )

    @swagger_auto_schema(
        operation_id="create_table",
        operation_summary=TableDocData.create_operation_summary,
        operation_description=TableDocData.create_operation_description,
        request_body=TableSerializer,
        responses={
            status.HTTP_201_CREATED: TableDocData.success_response,
            status.HTTP_400_BAD_REQUEST: TableDocData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: TableDocData.unauthorized_response,
            status.HTTP_403_FORBIDDEN: TableDocData.forbidden_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: TableDocData.server_error_response,
        },
        tags=["Tables"],
    )
    def create(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")

        logger.info(
            f"User {user_id} is attempting to create a new table with data: {request.data}."
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_table = TableService.create_table(serializer.validated_data)

        logger.info(
            f"Table ID: {created_table.id} created successfully by user {user_id}."
        )
        return ResponseWrapper.created(
            data=self.get_serializer(created_table).data,
            entity=f"Table {created_table.id}",
        )

    @swagger_auto_schema(
        operation_id="update_table",
        operation_summary=TableDocData.update_operation_summary,
        operation_description=TableDocData.update_operation_description,
        request_body=TableSerializer,
        responses={
            status.HTTP_201_CREATED: TableDocData.success_response,
            status.HTTP_404_NOT_FOUND: TableDocData.not_found_response,
            status.HTTP_400_BAD_REQUEST: TableDocData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: TableDocData.unauthorized_response,
            status.HTTP_403_FORBIDDEN: TableDocData.forbidden_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: TableDocData.server_error_response,
        },
        tags=["Tables"],
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(
            f"User {user_id} is attempting to update table ID: {instance.id} with data: {request.data}."
        )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        updated_table = TableService.update_table(instance, serializer.validated_data)

        logger.info(
            f"Table ID: {updated_table.id} updated successfully by user {user_id}."
        )
        return ResponseWrapper.updated(
            data=self.get_serializer(updated_table).data,
            entity=f"Table {updated_table.id}",
        )

    @swagger_auto_schema(
        operation_id="delete_table",
        operation_summary=TableDocData.destroy_operation_summary,
        operation_description=TableDocData.destroy_operation_description,
        responses={
            status.HTTP_200_OK: TableDocData.success_no_data_response,
            status.HTTP_401_UNAUTHORIZED: TableDocData.unauthorized_response,
            status.HTTP_403_FORBIDDEN: TableDocData.forbidden_response,
            status.HTTP_404_NOT_FOUND: TableDocData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: TableDocData.server_error_response,
        },
        tags=["Tables"],
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is attempting to delete table ID: {instance.id}.")

        table_id = instance.id
        TableService.delete_table(instance)

        logger.info(f"Table ID: {table_id} deleted successfully by user {user_id}.")
        return ResponseWrapper.deleted(
            entity=f"Table {table_id}",
        )
