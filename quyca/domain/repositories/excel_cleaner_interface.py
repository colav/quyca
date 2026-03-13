from __future__ import annotations
from abc import ABC, abstractmethod


class IExcelCleaner(ABC):
    @abstractmethod
    def clean(self, filepath: str) -> None:
        """Cleans formatting or styles from the specified Excel file."""
        raise NotImplementedError
