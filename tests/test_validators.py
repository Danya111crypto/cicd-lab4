import pytest
from utils.validators import validate_user_email, validate_age


@pytest.mark.parametrize(
    "valid_email",
    [
        "test@example.com",
        "user.name@domain.co.uk",
        "student_2026+lab@opu.ua",
    ],
)
def test_validate_user_email_valid(valid_email):
    assert validate_user_email(valid_email) is True, (
        f"Коректний email '{valid_email}' має проходити валідацію"
    )


@pytest.mark.parametrize(
    "invalid_email",
    [
        "",
        "   ",
        None,
        "userexample.com",
        "user@",
        "@domain.com",
        "user@domain",
    ],
)
def test_validate_user_email_invalid(invalid_email):
    assert validate_user_email(invalid_email) is False, (
        f"Невалідний email '{invalid_email}' має відхилятися"
    )


@pytest.mark.parametrize("valid_age", [18, 99])
def test_validate_age_valid(valid_age):
    assert validate_age(valid_age) is True, (
        f"Вік {valid_age} має вважатися валідним"
    )


@pytest.mark.parametrize("boundary_age", [0, 150])
def test_validate_age_boundaries(boundary_age):
    assert validate_age(boundary_age) is True, (
        f"Граничне значення віку {boundary_age} має вважатися валідним"
    )


@pytest.mark.parametrize("invalid_age", ["25", None, -5, 151])
def test_validate_age_invalid_raises_value_error(invalid_age):
    with pytest.raises(ValueError) as exc_info:
        validate_age(invalid_age)
    assert exc_info.value is not None, (
        f"Для некоректного значення віку {invalid_age!r} має виникати ValueError"
    )
