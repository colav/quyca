import re
from typing import List, Dict, Any
from .base_validator import BaseValidator

NAME_RE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' \-]+$")


class NameValidator:
    """
    Validates human names (letters, spaces, accents, apostrophes, hyphens).
    """

    @staticmethod
    def validate(row: dict, index: int) -> List[Dict[str, Any]]:
        errors: List[Dict[str, Any]] = []
        for field in ["primer_apellido", "segundo_apellido", "nombres"]:
            value = row.get(field)
            if not BaseValidator.is_empty(value) and not NAME_RE.match(str(value).strip()):
                errors.append(
                    {"fila": index, "columna": field, "detalle": f"El nombre {value} no es permitido", "valor": value}
                )
        return errors
