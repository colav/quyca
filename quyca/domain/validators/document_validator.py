import re
from typing import List, Dict, Any
from .base_validator import BaseValidator

PASSPORT_RE = re.compile(r"^[A-Za-z0-9]+$")
ALLOWED_DOCUMENT_TYPES = {"cédula de ciudadanía", "cédula de extranjería", "pasaporte"}


class DocumentValidator:
    """
    Validator for document type and identification fields.
    Ensures that the provided document type is allowed and
    that the identification value matches the expected format
    (numeric for IDs, alphanumeric for passports).
    """

    @staticmethod
    def validate(tipo_documento: str, identificacion: str, index: int) -> List[Dict[str, Any]]:
        errors: List[Dict[str, Any]] = []

        if not BaseValidator.is_empty(tipo_documento):
            tnorm = str(tipo_documento).strip().lower()
            if tnorm not in ALLOWED_DOCUMENT_TYPES:
                errors.append(
                    {
                        "fila": index,
                        "columna": "tipo_documento",
                        "detalle": f"El tipo de documento {tnorm} no es válido",
                        "value": tipo_documento,
                    }
                )

            if not BaseValidator.is_empty(identificacion) and not BaseValidator.is_empty(tipo_documento):
                id_str = str(identificacion).strip()
                tnorm = str(tipo_documento).strip().lower()

                if tnorm in {"cédula de ciudadanía", "cédula de extranjería"} and not id_str.isdigit():
                    errors.append(
                        {
                            "fila": index,
                            "columna": "identificación",
                            "detalle": f"La {tnorm} debe ser numérica",
                            "valor": identificacion,
                        }
                    )
                elif tnorm == "pasaporte" and not PASSPORT_RE.match(id_str):
                    errors.append(
                        {
                            "fila": index,
                            "columna": "identificación",
                            "detalle": "Formato inválido para pasaporte",
                            "valor": identificacion,
                        }
                    )

        return errors
