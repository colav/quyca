import io
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IPDFRepository(ABC):
    """
    Abstraction to generate PDF reports for Staff/CIARP validation results.
    """

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
    ) -> io.BytesIO:
        pass

    @abstractmethod
    def generate_quality_report_ciarp(
        self,
        errors: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]],
        duplicados: List[Dict[str, Any]] | None,
        institution: str,
        filename: str,
        upload_date: str,
        user: str,
    ) -> io.BytesIO:
        pass
