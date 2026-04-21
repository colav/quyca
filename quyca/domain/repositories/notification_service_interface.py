from __future__ import annotations

from typing import Any, Protocol
from quyca.domain.models.staff_report_model import StaffReport


class INotificationService(Protocol):
    """Defines notification sending operations for processing results."""

    def send_report(
        self,
        staff_report: StaffReport,
        institution: str,
        filename: str,
        upload_date: str,
        user: str,
        email: str,
        file_type: str,
        attachments: list[dict],
        ror_id: str,
    ) -> dict[str, Any]:
        """Sends a processing report notification and returns the result."""
        ...
