from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status, serializers

# TODO: Use It in Response Wrapper?????
class StockResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField()
    metadata = serializers.DictField(required=False)

class StockListResponseSerializer(StockResponseSerializer):
    data = serializers.ListField(child=serializers.DictField())
    metadata = serializers.DictField(child=serializers.CharField())

class StockDetailResponseSerializer(StockResponseSerializer):
    data = serializers.DictField()

class StockErrorResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    errors = serializers.DictField()


class StockDocumentationData:
    """
    Documentation data for StockViews endpoints
    """
    # Common responses
    success_response = openapi.Response(
        description="Successful operation",
        schema=StockDetailResponseSerializer,
        examples={
            "application/json": {
                "success": True,
                "message": "Operation successful",
                "data": {
                    "id": 1,
                    "_id": 101,
                    "total_stock": 150,
                    "optimal_stock_quantity": 200,
                    "transactions": None
                }
            }
        }
    )
    
    list_response = openapi.Response(
        description="List of all stock",
        schema=StockListResponseSerializer,
        examples={
            "application/json": {
                "success": True,
                "message": "Found 5 stock",
                "data": [
                    {
                        "id": 1,
                        "_id": 101,
                        "total_stock": 150,
                        "optimal_stock_quantity": 200
                    }
                ],
                "metadata": {
                    "total": 5,
                    "note": "Add ?include_transactions=true to include transactions"
                }
            }
        }
    )
    
    not_found_response = openapi.Response(
        description="Stock  not found",
        schema=StockErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Stock not found",
                "errors": {
                    "detail": "Stock with ID 999 does not exist."
                }
            }
        }
    )
    
    validation_error_response = openapi.Response(
        description="Validation error",
        schema=StockErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Validation Error",
                "errors": {
                    "total_stock": ["Stock must be an integer."],
                    "id": ["The specified inventory  does not exist."]
                }
            }
        }
    )
    
    # Operation metadata
    list_operation_summary = 'List all stock'
    list_operation_description = """
    Returns a list of all stock in inventory.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in.
    
    **Query Parameters:**
    - `include_transactions=true`: Include transaction history for each stock 
    """
    
    retrieve_operation_summary = 'Retrieve a specific stock '
    retrieve_operation_description = """
    Returns details for a specific stock .
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in.
    
    **Query Parameters:**
    - `include_transactions=true`: Include transaction history
    """
    
    create_operation_summary = 'Create a new stock '
    create_operation_description = """
    Creates a new stock record in the system.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in.
    
    **Required Fields:**
    - `_id`: ID of the inventory 
    - `total_stock`: Current stock quantity
    - `optimal_stock_quantity`: Target stock level
    """
    
    update_operation_summary = 'Update a stock '
    update_operation_description = """
    Updates an existing stock record.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in.
    
    **Note:**
    - This is a full update (PUT), not a partial update
    """
    
    destroy_operation_summary = 'Delete a stock '
    destroy_operation_description = """
    Deletes a stock record from the system.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in.
    
    **Note:**
    - This action is irreversible
    - Does not delete the associated inventory 
    """
