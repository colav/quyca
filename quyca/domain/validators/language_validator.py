import re
from typing import List, Dict, Any
from domain.validators.base_validator import BaseValidator

LANG_RE = re.compile(r"^[a-z]{2}$")


class LanguageValidator:
    """
    Warns when language code is not ISO 639-1 (two lowercase letters).
    """

    @staticmethod
    def validator(row: dict, index: int) -> List[Dict[str, Any]]:
        warnings = []

        language = row.get("idioma")
        if not BaseValidator.is_empty(language) and not LANG_RE.match(str(language).lower().strip()):
            warnings.append(
                {
                    "fila": index,
                    "columna": "idioma",
                    "detalle": "Formato de idioma inválido (debe ser ISO 639-1, ej: 'es', 'en')",
                    "valor": language,
                }
            )

        return warnings
