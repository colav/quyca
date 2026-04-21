from __future__ import annotations

from typing import Protocol

import pandas as pd

from quyca.domain.models.staff_report_model import StaffReport


class IDataFrameAnnotator(Protocol):
    """Defines dataframe annotation operations based on validation reports."""

    def annotate(self, df: pd.DataFrame, report: StaffReport) -> pd.DataFrame:
        """Annotates the dataframe using the provided validation report."""
        ...
