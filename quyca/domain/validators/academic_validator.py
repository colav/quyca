from .base_validator import BaseValidator
from typing import List, Dict, Any, Tuple

ALLOWED_ACADEMIC_LEVELS = {"técnico", "pregrado", "maestria", "doctorado", "especialización", "especialización médica"}
ALLOWED_CONTRACT_TYPES = {"vinculado", "ocasional", "cátedra", "prestación de servicios", "postdoc"}
ALLOWED_WORK_SCHEDULES = {"medio tiempo", "tiempo completo", "tiempo parcial"}
ALLOWED_JOB_CATEGORIES = {"auxiliar", "asociado", "titular"}
ALLOWED_GENDERS = {"hombre", "mujer", "intersexual", ""}


class AcademicValidator:
    """Validates academic and employment attributes in staff records."""

    @staticmethod
    def validate(row: dict, index: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Checks allowed values and returns detected errors and warnings."""
        errors: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []

        nivel = row.get("nivel_académico")
        if not BaseValidator.is_empty(nivel) and str(nivel).strip().lower() not in ALLOWED_ACADEMIC_LEVELS:
            errors.append(
                {
                    "fila": index,
                    "columna": "nivel_académico",
                    "detalle": f"El nivel académico {nivel} no existe en el listado",
                    "valor": nivel,
                }
            )

        tc = row.get("tipo_contrato")
        if not BaseValidator.is_empty(tc) and str(tc).strip().lower() not in ALLOWED_CONTRACT_TYPES:
            warnings.append(
                {
                    "fila": index,
                    "columna": "tipo_contrato",
                    "detalle": f"El tipo de contrato {tc} no está en el listado",
                    "valor": tc,
                }
            )

        jr = row.get("jornada_laboral")
        if not BaseValidator.is_empty(jr) and str(jr).strip().lower() not in ALLOWED_WORK_SCHEDULES:
            errors.append(
                {
                    "fila": index,
                    "columna": "jornada_laboral",
                    "detalle": f"La jornada laboral {jr} no se encontró en el listado",
                    "valor": jr,
                }
            )

        cat = row.get("categoría_laboral")
        if not BaseValidator.is_empty(cat) and str(cat).strip().lower() not in ALLOWED_JOB_CATEGORIES:
            warnings.append(
                {
                    "fila": index,
                    "columna": "categoría_laboral",
                    "detalle": f"{cat} no está en el listado de categoría laboral",
                    "valor": cat,
                }
            )

        sexo = row.get("sexo")
        if not BaseValidator.is_empty(sexo) and str(sexo).strip().lower() not in ALLOWED_GENDERS:
            errors.append(
                {
                    "fila": index,
                    "columna": "sexo",
                    "detalle": f"{sexo} no válido solo se permite (hombre, mujer, intersexual o ninguno)",
                    "valor": sexo,
                }
            )

        return errors, warnings
