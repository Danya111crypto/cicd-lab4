import re
from hypothesis import given, settings, strategies as st

from common.utils import normalize_product_sku


ALLOWED_CHARS_PATTERN = re.compile(r"^[A-Z0-9-]*$")


@given(st.text())
@settings(max_examples=200)
def test_normalize_sku_idempotence(s: str) -> None:
    """Property 1: Re-applying normalize_product_sku does not change the result."""
    once = normalize_product_sku(s)
    twice = normalize_product_sku(once)
    assert twice == once


@given(st.text())
@settings(max_examples=200)
def test_normalize_sku_allowed_character_set(s: str) -> None:
    """Property 2: Result contains only uppercase Latin letters, digits, and hyphens."""
    result = normalize_product_sku(s)
    assert ALLOWED_CHARS_PATTERN.fullmatch(result) is not None


@given(st.text(min_size=0, max_size=500))
@settings(max_examples=200)
def test_normalize_sku_max_length(s: str) -> None:
    """Property 3: Generated SKU length never exceeds 20 characters."""
    result = normalize_product_sku(s)
    assert len(result) <= 20