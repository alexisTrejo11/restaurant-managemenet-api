from rest_framework import serializers


class ApiResponseSerializer(serializers.Serializer):
    """
    Base serializer for standardized API responses.

    Use this serializer in drf-spectacular's @extend_schema to document
    the structure of all API responses.

    Example:
        @extend_schema(
            responses={
                200: ApiResponseSerializer,
                404: NotFoundErrorResponseSerializer
            }
        )
    """

    data = serializers.JSONField(
        help_text="Response payload. Can be any valid JSON structure (object, array, string, number, boolean, or null).",
        allow_null=True,
        required=False,
        default=None,
    )

    timestamp = serializers.CharField(
        help_text="ISO 8601 formatted timestamp when the response was generated (e.g., '2024-01-01T12:00:00Z')",
        max_length=50,
    )
    success = serializers.BooleanField(
        help_text="Indicates whether the request was successful. True for 2xx responses, False for error responses.",
    )
    status_code = serializers.IntegerField(
        help_text="HTTP status code of the response (e.g., 200, 201, 400, 404, 500)",
        min_value=100,
        max_value=599,
    )
    message = serializers.CharField(
        help_text="Human-readable message describing the response outcome",
        max_length=500,
    )
    metadata = serializers.DictField(
        help_text="Additional metadata about the response (pagination info, warnings, etc.)",
        required=False,
        default=dict,
        child=serializers.JSONField(),
    )


class NoContentResponseSerializer(serializers.Serializer):
    """
    Serializer for 204 No Content responses.

    Note: 204 responses typically have no body. This serializer is for
    documentation purposes only.
    """

    class Meta:
        ref_name = "NoContentResponse"  # Avoid conflicts with other 204 serializers


class PaginatedResponseSerializer(ApiResponseSerializer):
    """
    Serializer for paginated list responses.

    Use this when returning paginated lists of resources.
    """

    data = serializers.ListField(
        help_text="List of items for the current page",
        child=serializers.DictField(),
    )

    class PaginationMetadataSerializer(serializers.Serializer):
        """Pagination metadata structure."""

        page = serializers.IntegerField(
            help_text="Current page number (1-indexed)", min_value=1
        )
        page_size = serializers.IntegerField(
            help_text="Number of items per page", min_value=1, max_value=100
        )
        total_count = serializers.IntegerField(
            help_text="Total number of items across all pages", min_value=0
        )
        total_pages = serializers.IntegerField(
            help_text="Total number of pages available", min_value=0
        )
        has_next = serializers.BooleanField(
            help_text="Whether there is a next page available"
        )
        has_previous = serializers.BooleanField(
            help_text="Whether there is a previous page available"
        )

    metadata = PaginationMetadataSerializer(
        help_text="Pagination information for the current response", required=True
    )


# Error Response Serializers


class BaseErrorResponseSerializer(ApiResponseSerializer):
    """Base serializer for all error responses (4xx and 5xx status codes)."""

    success = serializers.BooleanField(
        default=False, help_text="Always False for error responses"
    )
    data = serializers.JSONField(
        help_text="Additional error details (validation errors, etc.)",
        allow_null=True,
        required=False,
        default=None,
    )


class ValidationErrorResponseSerializer(BaseErrorResponseSerializer):
    """
    Serializer for 400 Bad Request responses with validation errors.

    Use this when request validation fails.
    """

    status_code = serializers.IntegerField(
        default=400, help_text="HTTP 400 Bad Request status code"
    )
    message = serializers.CharField(
        default="Validation Error",
        help_text="Validation error summary",
    )
    data = serializers.DictField(
        child=serializers.ListField(
            child=serializers.CharField(), help_text="List of error messages per field"
        ),
        help_text="Detailed validation errors by field",
        required=False,
    )


class NotFoundErrorResponseSerializer(BaseErrorResponseSerializer):
    """Serializer for 404 Not Found responses."""

    status_code = serializers.IntegerField(
        default=404, help_text="HTTP 404 Not Found status code"
    )
    message = serializers.CharField(
        default="The requested resource was not found",
        help_text="Resource not found message",
    )


class UnauthorizedErrorResponseSerializer(BaseErrorResponseSerializer):
    """Serializer for 401 Unauthorized responses."""

    status_code = serializers.IntegerField(
        default=401, help_text="HTTP 401 Unauthorized status code"
    )
    message = serializers.CharField(
        default="Authentication credentials were not provided or are invalid",
        help_text="Authentication error message",
    )


class ForbiddenErrorResponseSerializer(BaseErrorResponseSerializer):
    """Serializer for 403 Forbidden responses."""

    status_code = serializers.IntegerField(
        default=403, help_text="HTTP 403 Forbidden status code"
    )
    message = serializers.CharField(
        default="You do not have permission to perform this action",
        help_text="Permission error message",
    )


class ConflictErrorResponseSerializer(BaseErrorResponseSerializer):
    """Serializer for 409 Conflict responses."""

    status_code = serializers.IntegerField(
        default=409, help_text="HTTP 409 Conflict status code"
    )
    message = serializers.CharField(
        default="The request conflicts with the current state of the resource",
        help_text="Conflict error message",
    )


class ServerErrorResponseSerializer(BaseErrorResponseSerializer):
    """Serializer for 500 Internal Server Error responses."""

    status_code = serializers.IntegerField(
        default=500, help_text="HTTP 500 Internal Server Error status code"
    )
    message = serializers.CharField(
        default="An unexpected error occurred",
        help_text="Server error message",
    )
    data = serializers.JSONField(
        help_text="Error details (only shown in debug mode)",
        allow_null=True,
        required=False,
        default=None,
    )


class SuccessResponseSerializer(ApiResponseSerializer):
    """Serializer for successful responses (2xx status codes)."""

    success = serializers.BooleanField(
        default=True, help_text="Always True for successful responses"
    )


class CreatedResponseSerializer(SuccessResponseSerializer):
    """Serializer for 201 Created responses."""

    status_code = serializers.IntegerField(
        default=201, help_text="HTTP 201 Created status code"
    )
    message = serializers.CharField(
        help_text="Resource creation confirmation message",
    )
