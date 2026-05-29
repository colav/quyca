import unicodedata
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

REQUIRED_COLUMNS = [
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


def _normalize(s: str) -> str:
    """Strips accents and lowercases a string for flexible column matching."""
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("ascii").strip().lower()


def _relaxed_normalize(s: str) -> str:
    """Normalizes a header enough to compare spaces, hyphens and underscores."""
    normalized = _normalize(s)
    return normalized.replace(" ", "_").replace("-", "_")


_NORMALIZED_REQUIRED = {_normalize(c): c for c in REQUIRED_COLUMNS}
_NORMALIZED_EXTRA_ALLOWED = {_normalize(c) for c in EXTRA_ALLOWED}


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
        usecols: list[str] = []

        matched_required: set[str] = set()

        relaxed_required_map = {_relaxed_normalize(required): required for required in REQUIRED_COLUMNS}

        for idx, c in enumerate(raw_cols):
            col = c.strip()
            col_norm = _normalize(col)
            col_relaxed = _relaxed_normalize(col)

            if idx == 0 and (col_norm.startswith("unnamed") or col == "" or col_norm == "index"):
                continue
            if col_norm.startswith("unnamed") or col == "":
                if not df.iloc[:, idx].dropna(how="all").empty:
                    errors.append(f"Columna sin nombre en posición {idx+1}")
                continue

            if col_norm in _NORMALIZED_REQUIRED:
                canonical = _NORMALIZED_REQUIRED[col_norm]
                matched_required.add(canonical)
                usecols.append(canonical)
                continue

            if col_relaxed in relaxed_required_map:
                canonical = relaxed_required_map[col_relaxed]
                matched_required.add(canonical)
                usecols.append(canonical)
                continue

            # Ignore extra columns. They are allowed in the uploaded file,
            # but they are not part of the normalized schema used for ETL.
            continue

        missing = [c for c in REQUIRED_COLUMNS if c not in matched_required]

        if missing:
            errors.append(f"Columnas faltantes: {', '.join(missing)}")

        # Return usecols using canonical names from REQUIRED_COLUMNS where possible
        usecols = [
            _NORMALIZED_REQUIRED.get(_normalize(c), c)
            for c in usecols
            if _normalize(c) not in _NORMALIZED_EXTRA_ALLOWED
        ]

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
            date_value = row.get(field)
            if isinstance(date_value, str) and date_value.strip().lower() == "desconocido":
                warnings.append(
                    {
                        "fila": index,
                        "columna": field,
                        "detalle": f"{field} fuera de catálogo, se normalizó a desconocido",
                        "valor": date_value,
                    }
                )
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

        # Rename columns to canonical names so row validators always find the right keys
        rename_map = {
            col: _NORMALIZED_REQUIRED[_normalize(col)] for col in df.columns if _normalize(col) in _NORMALIZED_REQUIRED
        }
        df = df.rename(columns=rename_map)

        df = df.dropna(how="all").reset_index(drop=True)
        df = df[~df.apply(lambda row: row.astype(str).str.strip().eq("").all(), axis=1)]
        df = df.apply(lambda x: str(x).strip() if isinstance(x, str) else x)
        df = df.apply(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else x)

        for idx, row in df.iterrows():
            r = StaffValidator.validate_row(row.to_dict(), idx)
            errors.extend(r["errors"])
            warnings.extend(r["warnings"])

        dedupe_cols = [c for c in df.columns if c in REQUIRED_COLUMNS]

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
