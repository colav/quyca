from typing import Union
import pandas as pd


class BaseValidator:
    """Checks if a given value is considered empty.
    Supports None, NaN, and empty strings."""

    @staticmethod
    def is_empty(value: Union[str, float, None]) -> bool:
        if value is None:
            return True
        if isinstance(value, float) and pd.isna(value):
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        return False
