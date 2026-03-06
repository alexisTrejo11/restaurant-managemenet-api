import logging
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.shared.response.serializers import ApiResponseSerializer
from apps.shared.pagination import CustomPagination
from ..models import Dish
from ..serializers import (
    DishSerializer,
    ListDishResponseSerializer,
    PaginatedDishesResponseSerializer,
)
from ..services import DishService

logger = logging.getLogger(__name__)


class ListActiveDishesByStatus(generics.ListAPIView):
    """List active dishes filtered by category status."""

    serializer_class = DishSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category"]
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category = self.request.query_params.get("status", "ACTIVE").upper()
        logger.info(
            f"Listing menu items with category: {category}",
            extra={
                "requested_by": self.request.user.id,
                "query_params": self.request.query_params,
            },
        )
        DishService.validate_category(category)
        return Dish.objects.filter(category=category, status="ACTIVE").order_by("name")

    @extend_schema(
        operation_id="list_active_dishes_by_status",
        summary="List active dishes by category",
        description="Retrieve paginated list of active dishes filtered by category status",
        parameters=[
            OpenApiParameter(
                "status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by category status (DRINKS, ALCOHOL_DRINKS, BREAKFASTS, STARTERS, MEALS, DESSERTS, EXTRAS)",
                required=False,
            ),
            OpenApiParameter(
                "category",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by category",
                required=False,
            ),
        ],
        responses={
            200: PaginatedDishesResponseSerializer,
        },
        tags=["Menu"],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        response_data = ListDishResponseSerializer(
            {
                "data": serializer.data,
                "message": "Active dishes retrieved successfully",
            }
        ).data
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id="list_dish_categories",
    summary="List all dish categories",
    description="Retrieve all available dish category statuses (DRINKS, ALCOHOL_DRINKS, BREAKFASTS, STARTERS, MEALS, DESSERTS, EXTRAS)",
    responses={
        200: ApiResponseSerializer,
    },
    tags=["Menu"],
)
@api_view(["GET"])
def list_dish_categories(request):
    """API endpoint to list all available dish categories."""
    status_list = DishService.list_all_categories()

    response_data = {
        "data": status_list,
        "message": "Dish categories retrieved successfully",
    }
    return Response(response_data, status=status.HTTP_200_OK)
