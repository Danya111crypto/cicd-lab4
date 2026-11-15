import re


def validate_user_email(email: str) -> bool:
    """Перевіряє коректність формату email-адреси користувача."""
    if not isinstance(email, str) or not email.strip():
        return False
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def validate_age(age: int) -> bool:
    """Перевіряє коректність віку користувача (від 0 до 150 включно)."""
    if isinstance(age, bool) or not isinstance(age, int):
        raise ValueError("Вік має бути цілим числом")
    if age < 0 or age > 150:
        raise ValueError("Вік має бути в діапазоні від 0 до 150")
    return True
