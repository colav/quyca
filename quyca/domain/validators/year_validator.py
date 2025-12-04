from datetime import datetime
from typing import Any, Dict, Optional


class YearValidator:
    """
    Validates that the provided year is numeric and not in the future.
    """

    @staticmethod
    def validate(value: Any, field: str, index: int) -> Optional[Dict[str, Any]]:
        if value is None or str(value).strip() == "":
            return None
        try:
            year = int(value)
            current_year = datetime.now().year
            if year > current_year:
                return {
                    "fila": index,
                    "columna": field,
                    "detalle": "Año no válido",
                    "valor": value,
                }
        except Exception:
            return {"fila": index, "columna": field, "detalle": f"Formato inválido, debe ser numérico", "valor": value}
        return None
