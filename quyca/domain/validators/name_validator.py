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
        for field in ["primer_apellido", "segundo_apellido", "nombres"]:
            value = row.get(field)
            normalized_value = NameValidator._normalize_name(value)
            if not BaseValidator.is_empty(value) and not NameValidator._is_valid_name(normalized_value):
                errors.append(
                    {
                        "fila": index,
                        "columna": field,
                        "detalle": f"El nombre {normalized_value} no es permitido",
                        "valor": value,
                    }
                )
        return errors
