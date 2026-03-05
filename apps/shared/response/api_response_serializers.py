from rest_framework import serializers
from apps.shared.response.api_response import ApiResponse

"""
Success Responses
"""


class ApiResponseSerializer(serializers.Serializer):
    """
    Serializer for the standardized ApiResponse structure.
    Compatible with drf-yasg for API documentation.
    """

    data = serializers.JSONField(
        help_text="The response data. Can be any valid JSON structure.",
        allow_null=True,
        required=False,
    )
    timestamp = serializers.CharField(
        help_text="ISO 8601 formatted timestamp of when the response was generated.",
        max_length=50,
    )
    success = serializers.BooleanField(
        help_text="Indicates whether the request was successful."
    )
    status_code = serializers.IntegerField(
        help_text="HTTP status code of the response.", min_value=100, max_value=599
    )
    message = serializers.CharField(
        help_text="Descriptive message about the response.", max_length=500
    )
    metadata = serializers.DictField(
        help_text="Additional metadata about the response.",
        required=False,
        allow_empty=True,
        child=serializers.CharField(allow_blank=True),
    )

    def to_representation(self, instance):
        """
        Handle both dataclass instances and dictionary representations.
        """
        if isinstance(instance, ApiResponse):
            return {
                "data": instance.data,
                "timestamp": instance.timestamp,
                "success": instance.success,
                "status_code": instance.status_code,
                "message": instance.message,
                "metadata": instance.metadata,
            }
        return super().to_representation(instance)


class ApiResponseWithListSerializer(ApiResponseSerializer):
    """
    ApiResponse serializer for list responses with pagination metadata.
    """

    data = serializers.ListField(
        help_text="List of items", child=serializers.DictField()
    )

    class PaginationMetadataSerializer(serializers.Serializer):
        page = serializers.IntegerField(help_text="Current page number")
        page_size = serializers.IntegerField(help_text="Number of items per page")
        total_count = serializers.IntegerField(help_text="Total number of items")
        total_pages = serializers.IntegerField(help_text="Total number of pages")
        has_next = serializers.BooleanField(help_text="Whether there is a next page")
        has_previous = serializers.BooleanField(
            help_text="Whether there is a previous page"
        )

    metadata = PaginationMetadataSerializer(help_text="Pagination information")


"""
 ERROR SERIAlIZERS
"""


class BaseErrorResponseSerializer(serializers.Serializer):
    """
    Base serializer for all error responses
    """

    success = serializers.BooleanField(
        default=False, help_text="Indicates if the request was successful."
    )
    message = serializers.CharField(help_text="Error message describing the issue.")
    data = serializers.JSONField(
        help_text="Error details (if any).", allow_null=True, required=False
    )
    timestamp = serializers.CharField(help_text="ISO timestamp of the response.")
    status_code = serializers.IntegerField(help_text="HTTP status code.")
    metadata = serializers.DictField(help_text="Additional metadata.", required=False)


class NotFoundErrorResponseSerializer(BaseErrorResponseSerializer):
    """
    Serializer for 404 Not Found responses
    """

    status_code = serializers.IntegerField(
        default=404, help_text="HTTP status code for not found requests."
    )
    message = serializers.CharField(
        default="The requested resource was not found.",
        help_text="Not found error message.",
    )


class UnauthorizedErrorResponseSerializer(BaseErrorResponseSerializer):
    """
    Serializer for 401 Unauthorized responses
    """

    status_code = serializers.IntegerField(
        default=401, help_text="HTTP status code for unauthorized requests."
    )
    message = serializers.CharField(
        default="Authentication credentials were not provided or are invalid.",
        help_text="Authentication error message.",
    )


class ForbiddenErrorResponseSerializer(BaseErrorResponseSerializer):
    """
    Serializer for 403 Forbidden responses
    """

    status_code = serializers.IntegerField(
        default=403, help_text="HTTP status code for forbidden requests."
    )
    message = serializers.CharField(
        default="You do not have permission to perform this action.",
        help_text="Permission error message.",
    )


class ValidationErrorResponseSerializer(BaseErrorResponseSerializer):
    """
    Serializer for 400 Bad Request responses with validation errors
    """

    status_code = serializers.IntegerField(
        default=400, help_text="HTTP status code for bad requests."
    )
    message = serializers.CharField(
        default="Validation Error", help_text="Validation error message."
    )
    data = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        help_text="Detailed validation errors by field.",
        required=False,
    )


class ServerErrorResponseSerializer(BaseErrorResponseSerializer):
    """
    Serializer for 500 Internal Server Error responses
    """

    status_code = serializers.IntegerField(
        default=500, help_text="HTTP status code for server errors."
    )
    message = serializers.CharField(
        default="An unexpected error occurred.", help_text="Server error message."
    )
