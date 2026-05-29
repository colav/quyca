from typing import List, Dict, Any
from .base_validator import BaseValidator

REQUIRED_FIELDS = [
    "tipo_documento",
    "identificación",
    "primer_apellido",
    "nombres",
    "código_unidad_académica",
    "unidad_académica",
]


class RequiredFieldsValidator:
    """
    Ensures all mandatory Staff fields are present.
    """

    @staticmethod
    def validate(row: dict, index: int) -> List[Dict[str, Any]]:
        errors: List[Dict[str, Any]] = []
        for field in REQUIRED_FIELDS:
            value = row.get(field)
            if BaseValidator.is_empty(value):
                errors.append({"fila": index, "columna": field, "detalle": "Campo obligatorio vacío", "valor": "Vacío"})
        return errors
