from typing import Any
from dataclasses import dataclass


@dataclass
class ApiResponse:
    """
    Dataclass to represent the standardized API response structure.
    """

    data: Any
    timestamp: str
    success: bool
    status_code: int
    message: str
    metadata: dict
