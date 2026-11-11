from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r"^\+7\d{10}$",
    message="Телефон в формате +7XXXXXXXXXX (11 цифр, без пробелов и скобок).",
)
