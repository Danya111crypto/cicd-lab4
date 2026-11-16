import re


def normalize_product_sku(sku: str) -> str:
    """Normalize an arbitrary product SKU string.

    - Converts ASCII letters to uppercase.
    - Replaces any sequence of non-alphanumeric ASCII characters with '-'.
    - Strips leading and trailing hyphens.
    - Truncates to at most 20 characters without leaving a trailing hyphen.
    """
    if not isinstance(sku, str):
        raise TypeError("SKU must be a string")

    cleaned = re.sub(r"[^A-Z0-9]+", "-", sku.upper()).strip("-")
    return cleaned[:20].rstrip("-")