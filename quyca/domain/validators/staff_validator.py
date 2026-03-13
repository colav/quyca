from typing import List, Dict, Any, Tuple
from .required_fields_validator import RequiredFieldsValidator
from quyca.domain.models.staff_report_model import StaffReport
from .document_validator import DocumentValidator
from .academic_validator import AcademicValidator
from .name_validator import NameValidator
from .date_validator import DateValidator
from .unit_validator import UnitValidator
from .error_grouper import ErrorGrouper
import pandas as pd

REQUIARED_COLUMNS = [
    "tipo_documento",
    "identificación",
    "primer_apellido",
    "segundo_apellido",
    "nombres",
    "nivel_académico",
    "tipo_contrato",
    "jornada_laboral",
    "categoría_laboral",
    "sexo",
    "fecha_nacimiento",
    "fecha_inicial_vinculación",
    "fecha_final_vinculación",
    "código_unidad_académica",
    "unidad_académica",
    "código_subunidad_académica",
    "subunidad_académica",
]

EXTRA_ALLOWED = {"estado_de_validación", "observación"}


class StaffValidator:
    """Validates Staff dataframe schema and row-level data."""

    @staticmethod
    def excel_row_index(idx: int) -> int:
        """Converts dataframe index to Excel row number."""
        return idx + 2

    @staticmethod
    def validate_columns(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
        """Validates required and extra columns."""
        raw_cols = [str(c).strip() for c in df.columns]
        errors: List[str] = []
        usecols = []

        expected = list(REQUIARED_COLUMNS)

        for idx, c in enumerate(raw_cols):
            col = str(c).strip()

            if idx == 0 and (col.lower().startswith("unnamed") or col == "" or col.lower() == "index"):
                continue
            if col.lower().startswith("unnamed") or col == "":
                if not df.iloc[:, idx].dropna(how="all").empty:
                    errors.append(f"Columna sin nombre en posición {idx+1}")
                continue

            usecols.append(col)

        missing = [c for c in expected if c not in usecols]
        extra = [c for c in usecols if c not in expected and c not in EXTRA_ALLOWED]

        if missing:
            errors.append(f"Columnas faltantes: {', '.join(missing)}")
        if extra:
            errors.append(f"Columnas no permitidas: {', '.join(extra)}")

        usecols = [c for c in usecols if c not in EXTRA_ALLOWED]

        return (len(errors) == 0, errors, usecols)

    @staticmethod
    def validate_row(row: dict, index: int) -> dict:
        """Validates a single Staff row."""
        errors: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []

        errors.extend(RequiredFieldsValidator.validate(row, index))

        document_type: str = str(row.get("tipo_documento"))
        identification: str = str(row.get("identificación"))

        errors.extend(DocumentValidator.validate(document_type, identification, index))

        errors.extend(NameValidator.validate(row, index))

        for field in ["fecha_nacimiento", "fecha_inicial_vinculación", "fecha_final_vinculación"]:
            err = DateValidator.validate(row.get(field), field, index)
            if err:
                errors.append(err)

        e, w = AcademicValidator.validate(row, index)
        errors.extend(e)
        warnings.extend(w)

        errors.extend(UnitValidator.validate(row, index))

        return {"errors": errors, "warnings": warnings}

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> StaffReport:
        """Validates the full Staff dataframe and detects duplicates."""
        errors: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []

        df = df.dropna(how="all").reset_index(drop=True)
        df = df[~df.apply(lambda row: row.astype(str).str.strip().eq("").all(), axis=1)]
        df = df.apply(lambda x: str(x).strip() if isinstance(x, str) else x)
        df = df.apply(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else x)

        for idx, row in df.iterrows():
            r = StaffValidator.validate_row(row.to_dict(), idx)
            errors.extend(r["errors"])
            warnings.extend(r["warnings"])

        dedupe_cols = [c for c in df.columns if c in REQUIARED_COLUMNS]

        duplicate_info: List[Dict[str, Any]] = []
        total_dups = 0

        if dedupe_cols:
            dup_mask = df.duplicated(subset=dedupe_cols, keep=False)

            if dup_mask.any():
                total_dups = int(dup_mask.sum())
                for idx, row in df[dup_mask].iterrows():
                    duplicate_info.append(
                        {
                            "index": int(idx),
                            "index_excel": StaffValidator.excel_row_index(int(idx)),
                            "row": row.to_dict(),
                        }
                    )

        return StaffReport(
            total_errors=len(errors),
            total_duplicates=total_dups,
            errors=errors,
            grouped_errors=ErrorGrouper.group_errors(errors),
            warnings=warnings,
            grouped_warnings=ErrorGrouper.group_warnings(warnings),
            duplicates=duplicate_info,
        )
