from datetime import datetime, date
import pandas as pd
from typing import Dict, Any, Optional
from .base_validator import BaseValidator


class DateValidator:
    """Validates if a field contains a valid date in DD/MM/YYYY format."""

    @staticmethod
    def validate(value: Any, field: str, index: int) -> Optional[Dict[str, Any]]:
        if BaseValidator.is_empty(value):
            return None
        if isinstance(value, str) and value.strip().lower() == "desconocido":
            return None
        if isinstance(value, (pd.Timestamp, datetime, date)):
            return None

        try:
            datetime.strptime(str(value).strip(), "%d/%m/%Y")
            return None
        except Exception:
            return {
                "fila": index,
                "columna": field,
                "detalle": f"Formato inválido, debe ser DD/MM/YYYY y enviaste: {value}",
                "valor": value,
            }
