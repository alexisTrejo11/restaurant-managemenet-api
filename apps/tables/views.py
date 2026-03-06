import logging

from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from apps.shared.utils.log_user_actions import log_user_action
from apps.shared.response import (
    NoContentResponseSerializer,
    ValidationErrorResponseSerializer,
    NotFoundErrorResponseSerializer,
    UnauthorizedErrorResponseSerializer,
    ForbiddenErrorResponseSerializer,
    ServerErrorResponseSerializer,
)

from .models import Table
from .services.table_service import TableService
from .serializers import (
    TableSerializer,
    CreateTableResponseSerializer,
    UpdateTableResponseSerializer,
    FoundTableResponseSerializer,
    FoundTableListResponseSerializer,
    PaginatedTablesResponseSerializer,
)

logger = logging.getLogger(__name__)

COMMON_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: UnauthorizedErrorResponseSerializer,
    status.HTTP_403_FORBIDDEN: ForbiddenErrorResponseSerializer,
    status.HTTP_500_INTERNAL_SERVER_ERROR: ServerErrorResponseSerializer,
}


@extend_schema(tags=["Tables"])
class TableViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing restaurant tables.

    Provides CRUD operations with comprehensive logging and response formatting.
    All endpoints require authentication and appropriate permissions.
    """

    queryset = Table.objects.all()
    serializer_class = TableSerializer
    lookup_field = "number"
    lookup_url_kwarg = "number"

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    @extend_schema(
        operation_id="list_tables",
        summary="List all tables",
        description="Retrieves a list of all tables with their current status.",
        parameters=[
            OpenApiParameter(
                name="is_available",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by availability",
                required=False,
            ),
            OpenApiParameter(
                name="min_capacity",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Minimum table capacity",
                required=False,
            ),
        ],
        responses={
            200: PaginatedTablesResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def list(self, request, *args, **kwargs):
        """List all tables with optional filtering."""
        log_user_action(request, "requested table list")

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        response_data = PaginatedTablesResponseSerializer(serializer.data).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="retrieve_table",
        summary="Get table details",
        description="Retrieves detailed information for a specific table by number.",
        responses={
            200: FoundTableResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific table by number."""
        instance = self.get_object()
        log_user_action(request, f"requested table {instance.id}")

        serializer = self.get_serializer(instance)
        response_data = FoundTableResponseSerializer(serializer.data).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="create_table",
        summary="Create new table",
        description="Creates a new table with the provided information.",
        request=TableSerializer,
        responses={
            201: CreateTableResponseSerializer,
            400: ValidationErrorResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def create(self, request, *args, **kwargs):
        """Create a new table."""
        log_user_action(request, "attempted table creation", request.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        table = TableService.create_table(serializer.validated_data)
        log_user_action(request, f"created table {table.id}")

        created_table = self.get_serializer(table).data
        response_data = CreateTableResponseSerializer(created_table).data
        return Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="update_table",
        summary="Update table",
        description="Updates an existing table's information. Supports partial updates.",
        request=TableSerializer,
        responses={
            200: UpdateTableResponseSerializer,
            400: ValidationErrorResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def update(self, request, *args, **kwargs):
        """Update an existing table (full or partial)."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        log_user_action(request, f"attempted table {instance.id} update", request.data)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        table = TableService.update_table(instance, serializer.validated_data)
        log_user_action(request, f"updated table {table.id}")

        updated_table = self.get_serializer(table).data
        response_data = UpdateTableResponseSerializer(updated_table).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="delete_table",
        summary="Delete table",
        description="Permanently removes a table from the system.",
        responses={
            204: NoContentResponseSerializer,
            400: UnauthorizedErrorResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a table."""
        instance = self.get_object()
        table_id = instance.id

        log_user_action(request, f"attempted table {table_id} deletion")
        TableService.delete_table(instance)
        log_user_action(request, f"deleted table {table_id}")

        return Response(status=status.HTTP_204_NO_CONTENT)
