import unicodedata
from typing import List, Dict, Any
from .base_validator import BaseValidator


class NameValidator:
    """
    Validates human names using Unicode letters, spaces, apostrophes and hyphens.
    """

    @staticmethod
    def _normalize_name(value: object) -> str:
        """Normalize apostrophe-like characters and composed accents before validation."""
        return (
            unicodedata.normalize("NFC", str(value))
            .strip()
            .replace("´", "'")
            .replace("’", "'")
            .replace("ʼ", "'")
            .replace("ʻ", "'")
            .replace("`", "'")
        )

    @staticmethod
    def _is_valid_name(value: str) -> bool:
        """Return True when the value only contains letters, marks, spaces, apostrophes or hyphens."""
        for char in value:
            if char in {"'", "-", " "}:
                continue
            category = unicodedata.category(char)
            if category.startswith("L") or category.startswith("M"):
                continue
            return False
        return True

    @staticmethod
    def validate(row: dict, index: int) -> List[Dict[str, Any]]:
        errors: List[Dict[str, Any]] = []

        # Si existe nombre_completo, solamente se valida ese campo.
        if not BaseValidator.is_empty(row.get("nombre_completo")):
            fields = ["nombre_completo"]
        else:
            fields = [
                "primer_apellido",
                "segundo_apellido",
                "nombres",
            ]

        for field in fields:
            value = row.get(field)

            if BaseValidator.is_empty(value):
                continue

            normalized_value = NameValidator._normalize_name(value)

            if not NameValidator._is_valid_name(normalized_value):
                errors.append(
                    {
                        "fila": index,
                        "columna": field,
                        "detalle": f"El nombre {normalized_value} no es permitido",
                        "valor": value,
                    }
                )

        return errors
