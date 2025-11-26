import pandas as pd


class BaseValidator:
    """
    Lightweight utility to determine if a value is empty/blank.
    Returns True when value is None, NaN or empty string (trimmed).
    """

    @staticmethod
    def is_empty(value) -> bool:
        if value is None:
            return True
        if isinstance(value, float) and pd.isna(value):
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        return False
