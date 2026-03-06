import logging
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from ..models import Dish
from ..serializers import (
    DishSerializer,
    CreateDishResponseSerializer,
    UpdateDishResponseSerializer,
    RetrieveDishResponseSerializer,
    ListDishResponseSerializer,
    PaginatedDishesResponseSerializer,
)
from ..services import DishService
from ..filters import DishFilter
from apps.shared.response.serializers import (
    ApiResponseSerializer,
    NoContentResponseSerializer,
)

logger = logging.getLogger(__name__)

# Global error response mapping to reduce verbosity
COMMON_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: ApiResponseSerializer,
    status.HTTP_500_INTERNAL_SERVER_ERROR: ApiResponseSerializer,
}


@extend_schema(tags=["Menu"])
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

    @extend_schema(
        operation_id="list_dishes",
        summary="List all dishes",
        description="Retrieve a paginated list of dishes with optional filtering by category, price range, and search term",
        parameters=[
            OpenApiParameter(
                "category",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by category (DRINKS, ALCOHOL_DRINKS, BREAKFASTS, STARTERS, MEALS, DESSERTS, EXTRAS)",
                required=False,
            ),
            OpenApiParameter(
                "price_min",
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description="Minimum price filter",
                required=False,
            ),
            OpenApiParameter(
                "price_max",
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description="Maximum price filter",
                required=False,
            ),
            OpenApiParameter(
                "search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search term (searches in name and description)",
                required=False,
            ),
            OpenApiParameter(
                "ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Field to order results by (name, price, created_at)",
                required=False,
            ),
        ],
        responses={
            200: PaginatedDishesResponseSerializer,
            **COMMON_RESPONSES,
        },
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

        response_data = ListDishResponseSerializer(
            {
                "data": serializer.data,
                "message": "Dishes retrieved successfully",
            }
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="retrieve_dish",
        summary="Retrieve a single dish",
        description="Get detailed information about a specific dish by ID",
        responses={
            200: RetrieveDishResponseSerializer,
            404: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        logger.info(
            f"Retrieve request for menu item ID: {kwargs.get('id')}",
            extra={"user": request.user.id},
        )

        instance = self.get_object()
        serializer = self.get_serializer(instance)

        logger.info(
            f"Successfully retrieved menu dish ID: {instance.id}",
            extra={"category": instance.category},
        )
        response_data = RetrieveDishResponseSerializer(
            {
                "data": serializer.data,
                "message": "Dish retrieved successfully",
            }
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="create_dish",
        summary="Create a new dish",
        description="Create a new menu dish with category, price, and description",
        request=DishSerializer,
        responses={
            201: CreateDishResponseSerializer,
            400: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
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
        response_data = CreateDishResponseSerializer(
            {
                "data": menu_serialized.data,
                "message": f"Dish {menu_item.name} successfully created",
            }
        ).data
        return Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="update_dish",
        summary="Update a dish",
        description="Update dish information (name, price, category, status, etc.)",
        request=DishSerializer,
        responses={
            200: UpdateDishResponseSerializer,
            400: ApiResponseSerializer,
            404: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
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
        response_data = UpdateDishResponseSerializer(
            {
                "data": serializer.data,
                "message": f"Dish {instance.name} successfully updated",
            }
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="delete_dish",
        summary="Delete a dish",
        description="Remove a dish from the menu",
        responses={
            204: NoContentResponseSerializer,
            404: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def destroy(self, request, *args, **kwargs):
        logger.warning(
            f"Delete request for menu dish ID: {kwargs.get('id')}",
            extra={"user": request.user.id},
        )

        instance = self.get_object()
        self.perform_destroy(instance)

        logger.info(f"Successfully deleted menu item ID: {kwargs.get('id')}")

        return Response(status=status.HTTP_204_NO_CONTENT)
