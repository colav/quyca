import re
from typing import List, Dict, Any
from .base_validator import BaseValidator
from quyca.domain.constants.staff_field_values import DOCUMENT_TYPES

PASSPORT_RE = re.compile(r"^[A-Za-z0-9]+$")

_NUMERIC_ID_TYPES = {"cédula de ciudadanía", "cédula de extranjería"}


class DocumentValidator:
    """
    Validates document type and identification fields.
    At this point in the flow, values are already normalized by StaffNormalizerService,
    so only canonical values are expected.
    """

    @staticmethod
    def validate(tipo_documento: str, identificacion: str, index: int) -> List[Dict[str, Any]]:
        errors: List[Dict[str, Any]] = []

        if not BaseValidator.is_empty(tipo_documento):
            tnorm = str(tipo_documento).strip().lower()

            if tnorm not in DOCUMENT_TYPES:
                errors.append(
                    {
                        "fila": index,
                        "columna": "tipo_documento",
                        "detalle": f"El tipo de documento '{tipo_documento}' no es válido",
                        "value": tipo_documento,
                    }
                )

            if not BaseValidator.is_empty(identificacion):
                id_str = str(identificacion).strip()

                if tnorm in _NUMERIC_ID_TYPES and not id_str.isdigit():
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
