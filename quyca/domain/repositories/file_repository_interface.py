from __future__ import annotations

from typing import Any, Dict, Protocol


class IFileRepository(Protocol):
    """Defines file persistence operations."""

    def save_file(self, file: Any, ror_id: str, institution: str, file_type: str) -> Dict[str, Any]:
        """Saves the file and returns the storage result payload."""
        ...
