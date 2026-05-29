import io
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IPDFRepository(ABC):
    """Defines PDF report generation operations."""

    @abstractmethod
    def generate_quality_report(
        self,
        errors: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]],
        duplicados: List[Dict[str, Any]] | None,
        institution: str,
        filename: str,
        upload_date: str,
        user: str,
        normalized_changes: List[Dict[str, Any]] | None = None,
    ) -> io.BytesIO:
        """Generates a Staff quality validation PDF report."""

    @abstractmethod
    def generate_quality_report_ciarp(
        self,
        errors: List[Dict[str, Any]],
        warnings: Dict[str, Any],
        duplicados: List[Dict[str, Any]] | None,
        institution: str,
        filename: str,
        upload_date: str,
        user: str,
    ) -> io.BytesIO:
        """Generates a CIARP quality validation PDF report."""
