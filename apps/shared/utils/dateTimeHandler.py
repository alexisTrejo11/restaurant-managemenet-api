from django.forms import ValidationError
from datetime import datetime
from django.utils.dateparse import parse_datetime

class DateTimeHandler:
    @staticmethod
    def parse_date_to_ISO_8601(string_date: str):
        try:
            start_date = parse_datetime(string_date)
            
            if len(string_date) == 10:  #YYYY-MM-DD
                start_date = datetime.combine(start_date.date(), datetime.min.time())
        except (ValueError, TypeError) as e:
            raise ValidationError({
                "error": "Invalid date format",
                "detail": str(e),
                "expected_format": "ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
                "examples": [
                    "2023-05-01",
                    "2023-05-01T14:30:00"
                ]
            })