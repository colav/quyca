from dataclasses import dataclass
from typing import List, Dict, Any

"""
Domain entity that represents the validation result of a staff Excel file.
Contains errors, warnings, and duplicates detected during validation.
"""


@dataclass
class StaffReport:
    """Represents the validation result a Excel file."""

    total_errors: int
    total_duplicates: int
    errors: List[Dict[str, Any]]
    grouped_errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    grouped_warnings: List[Dict[str, Any]]
    duplicates: List[Dict[str, Any]]
