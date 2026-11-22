from django.core.exceptions import ValidationError


def validate_note(value):
    if any(ord(char) < 32 and char not in "\n\r\t" for char in value):
        raise ValidationError("Примечание содержит недопустимые управляющие символы.")
