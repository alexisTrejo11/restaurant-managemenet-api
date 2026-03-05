from decimal import Decimal
from django.db import IntegrityError, transaction
from .models import Dish
from django.core.cache import cache
import logging
from .exceptions import (
    InvalidDishCategory,
    InvalidDishPrice,
    DuplicateDishName,
    InvalidDishStatus,
    DishException,
)

logger = logging.getLogger(__name__)


class DishService:
    @staticmethod
    def validate_category(category: str) -> str:
        """Validates that the category exists in the choices."""
        valid_categories = dict(Dish.CATEGORY_CHOICES).keys()
        if category not in valid_categories:
            logger.warning(
                f"Invalid menu item category provided: '{category}'. Valid options: {', '.join(valid_categories)}"
            )
            raise InvalidDishCategory(
                f"Invalid category. Valid options: {', '.join(valid_categories)}"
            )
        return category

    @staticmethod
    def validate_price(price: Decimal) -> Decimal:
        """Validates business rules for prices."""
        if price <= Decimal("0.00"):
            logger.warning(f"Invalid menu item price: {price}. Price must be positive.")
            raise InvalidDishPrice("Price must be positive.")
        if price.as_tuple().exponent < -2:
            logger.warning(
                f"Invalid menu item price: {price}. Maximum 2 decimal places allowed."
            )
            raise InvalidDishPrice("Maximum 2 decimal places allowed.")
        if price > Decimal("10000.00"):
            logger.warning(
                f"Invalid menu item price: {price}. Price cannot exceed 10000.00."
            )
            raise InvalidDishPrice("Price cannot exceed 10000.00.")
        return price

    @staticmethod
    def create_menu_item(**kwargs) -> Dish:
        """Creates a new menu item record."""
        try:
            DishService.validate_category(kwargs.get("category"))
            DishService.validate_price(kwargs.get("price"))
            DishService.validate_status(kwargs.get("status", "ACTIVE"))

            kwargs["name"] = kwargs["name"].strip().title()
            kwargs.setdefault("status", "ACTIVE")

            with transaction.atomic():
                menu_item = Dish.objects.create(**kwargs)
                logger.info(
                    f"Menu item '{menu_item.name}' created successfully with ID: {menu_item.id}."
                )
                return menu_item
        except IntegrityError as e:
            logger.error(
                f"Integrity error creating menu item with data {kwargs}: {e}",
                exc_info=True,
            )
            if (
                "unique constraint" in str(e).lower() and "name" in str(e).lower()
            ):  # Generic check, refine if needed
                raise DuplicateDishName(
                    f"A menu item with the name '{kwargs.get('name')}' already exists."
                )
            raise DishException(
                "Failed to create menu item due to a database integrity error."
            )  # Generic fallback
        except (InvalidDishCategory, InvalidDishPrice, InvalidDishStatus) as e:
            raise

    @staticmethod
    def update_menu_item(instance: Dish, **kwargs) -> Dish:
        """Updates an existing menu item with business validation."""
        with transaction.atomic():
            if "name" in kwargs:
                new_name = kwargs["name"].strip().title()
                if (
                    Dish.objects.filter(name__iexact=new_name)
                    .exclude(id=instance.id)
                    .exists()
                ):
                    logger.warning(
                        f"Attempted to update menu item {instance.id} to duplicate name '{new_name}'."
                    )
                    raise DuplicateDishName(
                        f"Another menu item with the name '{new_name}' already exists."
                    )
                kwargs["name"] = new_name

            if "description" in kwargs:
                kwargs["description"] = kwargs["description"].strip()

            if "category" in kwargs:
                DishService.validate_category(kwargs["category"])

            if "price" in kwargs:
                DishService.validate_price(kwargs["price"])

            if "status" in kwargs:
                DishService.validate_status(kwargs["status"])

            for attr, value in kwargs.items():
                setattr(instance, attr, value)

            instance.save()
            logger.info(
                f"Menu item '{instance.name}' (ID: {instance.id}) updated successfully."
            )
            return instance

    @staticmethod
    def validate_status(status_value: str) -> str:
        """Validates that the status exists in the choices."""
        valid_statuses = [choice[0] for choice in Dish.STATUS_CHOICES]
        if status_value not in valid_statuses:
            logger.warning(
                f"Invalid menu item status provided: '{status_value}'. Valid choices: {', '.join(valid_statuses)}"
            )
            raise InvalidDishStatus(
                f"Invalid status parameter. Valid choices: {', '.join(valid_statuses)}"
            )
        return status_value

    @staticmethod
    def list_all_categories():
        """Lists all available menu item categories, using cache."""
        cached = cache.get("menu_categories")
        if not cached:
            cached = [
                {"id": idx + 1, "category": v}
                for idx, (v, l) in enumerate(Dish.CATEGORY_CHOICES)
            ]
            cache.set("menu_categories", cached, timeout=86400)
            logger.info("Menu categories cached.")
        else:
            logger.debug("Menu categories retrieved from cache.")
        return cached
