from typing import Optional
import logging

logger = logging.getLogger(__name__)


def log_user_action(request, action: str, details: Optional[dict] = None):
    """Centralized logging helper."""
    user_id = getattr(request.user, "id", "Anonymous")
    log_message = f"User {user_id} {action}"
    if details:
        log_message += f" - Details: {details}"
    logger.info(log_message)
