import logging

from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from apps.shared.response import ResponseWrapper

from ..models import Dish
from ..serializers import DishSerializer
from ..services import DishService
from ..filters import DishFilter
from ..documentation.menu_documentation import DishDocumentationData as DishDocData

logger = logging.getLogger(__name__)


# TODO: Check Filters
class DishViewSet(viewsets.ModelViewSet):
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = DishFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "created_at"]
    ordering = ["name"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Dish.objects.filter()

    @swagger_auto_schema(
        operation_id="list_dishes",
        operation_summary=DishDocData.list_operation_summary,
        operation_description=DishDocData.list_operation_description,
        manual_parameters=[
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                description="Filter by category",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "price_min",
                openapi.IN_QUERY,
                description="Minimum price",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "price_max",
                openapi.IN_QUERY,
                description="Maximum price",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search term (name or description)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Which field to use when ordering the results",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            status.HTTP_200_OK: DishDocData.dish_list_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: DishDocData.server_error_reponse,
        },
        tags=["Menu"],
    )
    # @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        query_params_dict = dict(request.query_params)

        logger.info(
            f"Listed {len(queryset)} menu items", extra={"filters": query_params_dict}
        )

        return ResponseWrapper.found(
            data=serializer.data,
            entity="Dish List",
            metadata={
                "total_items": queryset.count(),
                "filters_applied": query_params_dict,
            },
        )

    @swagger_auto_schema(
        operation_id="retrieve_dish",
        operation_summary=DishDocData.retrieve_operation_summary,
        operation_description=DishDocData.retrieve_operation_description,
        responses={
            status.HTTP_200_OK: DishDocData.dish_response,
            status.HTTP_404_NOT_FOUND: DishDocData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: DishDocData.server_error_reponse,
        },
        tags=["Menu"],
    )
    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        logger.info(
            f"Retrieve request for menu item ID: {kwargs.get('id')}",
            extra={"user": request.user.id, "request_data": request.data},
        )

        instance = self.get_object()
        serializer = self.get_serializer(instance)

        logger.info(
            f"Successfully retrieved menu dish ID: {instance.id}",
            extra={"category": instance.category},
        )
        return ResponseWrapper.found(data=serializer.data, entity="Dish")

    @swagger_auto_schema(
        operation_id="create_dish",
        operation_summary=DishDocData.create_operation_summary,
        operation_description=DishDocData.create_operation_description,
        request_body=DishSerializer,
        responses={
            status.HTTP_201_CREATED: DishDocData.dish_response,
            status.HTTP_400_BAD_REQUEST: DishDocData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: DishDocData.unauthorized_reponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: DishDocData.server_error_reponse,
        },
        tags=["Menu"],
    )
    def create(self, request, *args, **kwargs):
        logger.info(
            "Create request for new menu item",
            extra={"user": request.user.id, "data": request.data},
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        menu_item = DishService.create_menu_item(**serializer.validated_data)
        logger.info(
            f"Successfully created menu item ID: {menu_item.id}",
            extra={"item_id": menu_item.id},
        )

        menu_serialized = self.get_serializer(menu_item)
        return ResponseWrapper.created(data=menu_serialized.data, entity="Dish")

    @swagger_auto_schema(
        operation_id="update_dish",
        operation_summary=DishDocData.update_operation_summary,
        operation_description=DishDocData.update_operation_description,
        request_body=DishSerializer,
        responses={
            status.HTTP_200_OK: DishDocData.dish_response,
            status.HTTP_400_BAD_REQUEST: DishDocData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: DishDocData.unauthorized_reponse,
            status.HTTP_404_NOT_FOUND: DishDocData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: DishDocData.server_error_reponse,
        },
        tags=["Menu"],
    )
    def update(self, request, *args, **kwargs):
        logger.info(
            f"Update request for menu item ID: {kwargs.get('id')}",
            extra={"user": request.user.id, "request_data": request.data},
        )
        instance = self.get_object()

        serializer = self.get_serializer(
            instance, data=request.data, partial=bool(kwargs.get("partial"))
        )
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        logger.info(
            f"Successfully updated menu dish ID: {instance.id}",
            extra={"updated_fields": list(request.data.keys())},
        )
        return ResponseWrapper.updated(data=serializer.data, entity="Menu dish")

    @swagger_auto_schema(
        operation_id="delete_dish",
        operation_summary=DishDocData.destroy_operation_summary,
        operation_description=DishDocData.destroy_operation_description,
        responses={
            status.HTTP_204_NO_CONTENT: DishDocData.success_no_data,
            status.HTTP_401_UNAUTHORIZED: DishDocData.unauthorized_reponse,
            status.HTTP_404_NOT_FOUND: DishDocData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: DishDocData.server_error_reponse,
        },
        tags=["Menu"],
    )
    def destroy(self, request, *args, **kwargs):
        logger.warning(
            f"Delete request for menu dish ID: {kwargs.get('id')}",
            extra={"user": request.user.id},
        )

        instance = self.get_object()
        self.perform_destroy(instance)

        logger.info(f"Successfully deleted menu item ID: {kwargs.get('id')}")

        return ResponseWrapper.deleted(entity="Dish")
