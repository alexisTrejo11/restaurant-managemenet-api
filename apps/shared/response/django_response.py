from .api_response import ApiResponse
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from dataclasses import asdict


# TODO: Remove Data form asdict
class ResponseWrapper:
    """
    Custom Django Response Wrapper that adds the following fields to HTTP responses:
        - data: Any (payload of the response)
        - timestamp: Date and time of the request
        - message: Informative message about the response
        - status_code: HTTP status code
    """

    @staticmethod
    def found(
        data=None, entity="Entity", param=None, value=None, metadata=None
    ) -> Response:
        """
        Creates a 200 OK response indicating that an entity was successfully retrieved.

        Args:
            data (Any, optional): The payload to include in the response. Defaults to None.
            entity (str, optional): The name of the entity being retrieved. Defaults to 'Entity'.
            param (str, optional): The parameter used to identify the entity. Defaults to None.
            value (Any, optional): The value of the parameter used to identify the entity. Defaults to None.

        Returns:
            Response: A DRF Response object with a 200 OK status code and a formatted message.
        """
        message = f"{entity} successfully Retrieved"
        if param and value:
            message = f"{entity} with {param} [{value}] successfully Retrieved"

        if isinstance(data, dict):
            data = dict(data)

        response_body = ApiResponse(
            data=None,
            timestamp=datetime.now().isoformat(),
            success=True,
            status_code=status.HTTP_200_OK,
            message=message,
            metadata=metadata if metadata else {},
        )

        response_dict = asdict(response_body)
        response_dict["data"] = data
        return Response(data=response_dict, status=status.HTTP_200_OK)

    @staticmethod
    def success(data=None, message=None, metadata=None) -> Response:
        """
        Creates a 200 OK response indicating that the request was successfully completed.

        Args:
            data (Any, optional): The payload to include in the response. Defaults to None.
            message (str, optional): A custom success message. Defaults to 'Request Successfully Completed'.

        Returns:
            Response: A DRF Response object with a 200 OK status code and a success message.
        """
        if not message:
            message = "Request Successfully Completed"

        if isinstance(data, dict):
            data = dict(data)

        response_body = ApiResponse(
            data=None,
            timestamp=datetime.now().isoformat(),
            success=True,
            status_code=status.HTTP_200_OK,
            message=message,
            metadata=metadata if metadata else {},
        )

        response_dict = asdict(response_body)
        response_dict["data"] = data
        return Response(data=response_dict, status=status.HTTP_200_OK)

    @staticmethod
    def created(data=None, entity=None, metadata=None) -> Response:
        """
        Creates a 201 Created response indicating that an entity was successfully created.

        Args:
            data (Any, optional): The payload to include in the response. Defaults to None.
            entity (str, optional): The name of the entity being created. Defaults to 'Entity'.

        Returns:
            Response: A DRF Response object with a 201 Created status code and a success message.
        """
        message = "Entity Successfully Created"
        if entity:
            message = f"{entity} Successfully Created"

        if isinstance(data, dict):
            data = dict(data)

        response_body = ApiResponse(
            data=None,
            timestamp=datetime.now().isoformat(),
            success=True,
            status_code=status.HTTP_201_CREATED,
            message=message,
            metadata=metadata if metadata else {},
        )

        response_dict = asdict(response_body)
        response_dict["data"] = data
        return Response(data=response_dict, status=status.HTTP_201_CREATED)

    @staticmethod
    def updated(data=None, entity=None, metadata=None) -> Response:
        """
        Creates a 200 OK response indicating that an entity was successfully updated.

        Args:
            data (Any, optional): The payload to include in the response. Defaults to None.
            entity (str, optional): The name of the entity being updated. Defaults to 'Entity'.

        Returns:
            Response: A DRF Response object with a 200 OK status code and a success message.
        """
        message = "Entity Successfully Updated"
        if entity:
            message = f"{entity} Successfully Updated"

        if isinstance(data, dict):
            data = dict(data)

        response_body = ApiResponse(
            data=None,
            timestamp=datetime.now().isoformat(),
            success=True,
            status_code=status.HTTP_200_OK,
            message=message,
            metadata=metadata if metadata else {},
        )

        response_dict = asdict(response_body)
        response_dict["data"] = data
        return Response(data=response_dict, status=status.HTTP_200_OK)

    @staticmethod
    def not_found(
        data=None, entity="Entity", param=None, value=None, metadata=None
    ) -> Response:
        """
        Creates a 404 Not Found response indicating that an entity was not found.

        Args:
            data (Any, optional): The payload to include in the response. Defaults to None.
            entity (str, optional): The name of the entity being searched for. Defaults to 'Entity'.
            param (str, optional): The parameter used to identify the entity. Defaults to None.
            value (Any, optional): The value of the parameter used to identify the entity. Defaults to None.

        Returns:
            Response: A DRF Response object with a 404 Not Found status code and a failure message.
        """
        message = f"{entity} not found"
        if param and value:
            message = f"{entity} with {param} [{value}] not found"

        if isinstance(data, dict):
            data = dict(data)

        response_body = ApiResponse(
            data=data,
            timestamp=datetime.now().isoformat(),
            success=False,
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            metadata=metadata if metadata else {},
        )

        return Response(data=asdict(response_body), status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def bad_request(data=None, message=None, metadata=None) -> Response:
        """
        Creates a 400 Bad Request response indicating that the request was invalid.

        Args:
            data (Any, optional): The payload to include in the response. Defaults to None.
            message (str, optional): A custom error message. Defaults to 'Bad Request'.

        Returns:
            Response: A DRF Response object with a 400 Bad Request status code and an error message.
        """
        if not message:
            message = "Bad Request"

        if isinstance(data, dict):
            data = dict(data)

        response_body = ApiResponse(
            data=data,
            timestamp=datetime.now().isoformat(),
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            metadata=metadata if metadata else {},
        )

        return Response(data=asdict(response_body), status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def conflict(message=None, metadata=None) -> Response:
        """
        Creates a 409 Conflict response indicating that the request conflicts with the current state of the resource.

        Args:
            message (str, optional): A custom error message. Defaults to 'Conflict'.

        Returns:
            Response: A DRF Response object with a 409 Conflict status code and an error message.
        """
        if not message:
            message = "Conflict"

        response_body = ApiResponse(
            data=None,
            timestamp=datetime.now().isoformat(),
            success=False,
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            metadata=metadata if metadata else {},
        )

        return Response(data=asdict(response_body), status=status.HTTP_409_CONFLICT)

    @staticmethod
    def deleted(entity=None, metadata=None) -> Response:
        """
        Creates a 204 No Content response indicating that the request was successful but there is no content to return.

        Args:
            message (str, optional): A custom message. Defaults to 'No Content'.

        Returns:
            Response: A DRF Response object with a 204 No Content status code and an optional message.
        """
        if not entity:
            message = "Entity Successfully Deleted"
        else:
            message = f"{entity} Successfully Deleted"

        response_body = ApiResponse(
            data=None,
            timestamp=datetime.now().isoformat(),
            success=False,
            status_code=status.HTTP_204_NO_CONTENT,
            message=message,
            metadata=metadata if metadata else {},
        )

        return Response(data=asdict(response_body), status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def no_content(message=None, metadata=None) -> Response:
        """
        Creates a 204 No Content response indicating that the request was successful but there is no content to return.

        Args:
            message (str, optional): A custom message. Defaults to 'No Content'.

        Returns:
            Response: A DRF Response object with a 204 No Content status code and an optional message.
        """
        if not message:
            message = "No Content"

        response_body = ApiResponse(
            data=None,
            timestamp=datetime.now().isoformat(),
            success=False,
            status_code=status.HTTP_204_NO_CONTENT,
            message=message,
            metadata=metadata if metadata else {},
        )

        return Response(data=asdict(response_body), status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def failure(data=None, message=None, status_code=None, metadata=None) -> Response:
        """
        Creates a generic failure response with a customizable status code and message.

        Args:
            data (Any, optional): The payload to include in the response. Defaults to None.
            message (str, optional): A custom failure message. Defaults to 'Request Has Failed'.
            status_code (int, optional): The HTTP status code to use. Defaults to 400 Bad Request.

        Returns:
            Response: A DRF Response object with the specified status code and failure message.
        """
        if not status_code:
            status_code = status.HTTP_400_BAD_REQUEST

        if isinstance(data, dict):
            data = dict(data)

        if not message:
            message = "Request Has Failed"

        response_body = ApiResponse(
            data=None,
            timestamp=datetime.now().isoformat(),
            success=False,
            status_code=status_code,
            message=message,
            metadata=metadata if metadata else {},
        )

        response_dict = asdict(response_body)
        response_dict["data"] = data
        return Response(data=asdict(response_body), status=status_code)

    @staticmethod
    def internal_server_error(data=None, message=None, metadata=None) -> Response:
        """
        Creates a 500 Internal Server Error response indicating that an unexpected server error occurred.

        Args:
            data (Any, optional): The payload to include in the response. Defaults to None.
            message (str, optional): A custom error message. Defaults to 'Internal Server Error'.

        Returns:
            Response: A DRF Response object with a 500 Internal Server Error status code and an error message.
        """
        if not message:
            message = "Internal Server Error"

        if isinstance(data, dict):
            data = dict(data)

        response_body = ApiResponse(
            data=data,
            timestamp=datetime.now().isoformat(),
            success=False,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            metadata=metadata if metadata else {},
        )

        return Response(
            data=asdict(response_body), status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
