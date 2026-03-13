from __future__ import annotations

from typing import List, Protocol, Tuple
import pandas as pd


class ICiarpValidator(Protocol):
    """Defines CIARP column validation operations."""

    def validate_columns(self, df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
        """Validates dataframe columns and returns validation results."""
        ...
