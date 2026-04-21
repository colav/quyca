from typing import Union
import pandas as pd


class BaseValidator:
    """Provides basic validation utilities."""

    @staticmethod
    def is_empty(value: Union[str, float, None]) -> bool:
        """Checks whether a value is None, NaN or an empty string."""
        if value is None:
            return True
        if isinstance(value, float) and pd.isna(value):
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        return False
