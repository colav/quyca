import re
from typing import List, Dict, Any
from .base_validator import BaseValidator

CODE_RE = re.compile(r"^[0-9_]+$")
UNIT_RE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9, \-]+$")


class UnitValidator:
    """
    Validates unit/subunit codes and names (format + allowed characters).
    """

    @staticmethod
    def validate(row: dict, index: int) -> List[Dict[str, Any]]:
        errors: List[Dict[str, Any]] = []
        for field in ["código_unidad_académica", "código_subunidad_académica"]:
            value = row.get(field)
            if not BaseValidator.is_empty(value) and not CODE_RE.match(str(value).strip()):
                errors.append(
                    {
                        "fila": index,
                        "columna": field,
                        "detalle": f"No se permite {value}, solo números y _",
                        "valor": value,
                    }
                )

        for field in ["unidad_académica", "subunidad_académica"]:
            value = row.get(field)
            if not BaseValidator.is_empty(value) and not UNIT_RE.match(str(value).strip()):
                errors.append(
                    {
                        "fila": index,
                        "columna": field,
                        "detalle": f"Solo letras, números y espacios permitidos ya que {value} no es permitido",
                        "valor": value,
                    }
                )
        return errors
