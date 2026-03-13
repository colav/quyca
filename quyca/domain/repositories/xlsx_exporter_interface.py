from __future__ import annotations

import io
from typing import Protocol

import pandas as pd


class IXlsxExporter(Protocol):
    """Defines in-memory Excel export operations."""

    def to_excel_bytes(self, df: pd.DataFrame) -> io.BytesIO:
        """Exports the dataframe to Excel and returns it as bytes."""
        ...
