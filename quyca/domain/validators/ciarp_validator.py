import unicodedata
from typing import List, Dict, Any, Tuple
import pandas as pd
from quyca.domain.models.staff_report_model import StaffReport
from quyca.domain.validators.required_fields_validator_ciarp import RequiredFieldsCiarpValidator
from quyca.domain.validators.document_validator import DocumentValidator
from quyca.domain.validators.base_validator import BaseValidator
from quyca.domain.validators.year_validator import YearValidator
from quyca.domain.validators.language_validator import LanguageValidator
from quyca.domain.validators.country_validator import CountryValidator
from quyca.domain.validators.unit_validator import UnitValidator
from quyca.domain.validators.error_grouper import ErrorGrouper

EXTRA_ALLOWED = {"estado_de_validación", "observación"}

WARNING_EMPTY_FIELDS = ["código_unidad_académica", "ranking"]

REQUIRED_COLUMNS = [
    "código_unidad_académica",
    "código_subunidad_académica",
    "tipo_documento",
    "identificación",
    "año",
    "título",
    "idioma",
    "revista",
    "editorial",
    "doi",
    "issn",
    "isbn",
    "volumen",
    "issue",
    "primera_página",
    "última_página",
    "pais_producto",
    "entidad_premiadora",
    "ranking",
]


def _normalize(s: str) -> str:
    """Strips accents and lowercases a string for flexible column matching."""
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("ascii").strip().lower()


_NORMALIZED_REQUIRED = {_normalize(c): c for c in REQUIRED_COLUMNS}
_NORMALIZED_EXTRA_ALLOWED = {_normalize(c) for c in EXTRA_ALLOWED}


class CiarpValidator:
    """Validates CIARP dataframe schema and row-level rules."""

    @staticmethod
    def excel_row_index(idx: int) -> int:
        """Converts dataframe index to Excel row number."""
        return idx + 2

    @staticmethod
    def validate_columns(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
        """Validates required/extra columns and returns validation details."""
        raw_cols = [str(c).strip() for c in df.columns]
        errors: List[str] = []
        usecols: List[str] = []

        for idx, c in enumerate(raw_cols):
            col = c.strip()
            col_norm = _normalize(col)

            if idx == 0 and (col == "" or col_norm == "index" or col_norm.startswith("unnamed")):
                continue

            if col == "" or col_norm.startswith("unnamed"):
                if not df.iloc[:, idx].dropna(how="all").empty:
                    errors.append(f"Columna sin nombre en posición {idx+1}")
                continue

            usecols.append(col)

        normalized_usecols = {_normalize(c): c for c in usecols}

        missing = [c for c in REQUIRED_COLUMNS if _normalize(c) not in normalized_usecols]
        extra = [
            original
            for norm, original in normalized_usecols.items()
            if norm not in _NORMALIZED_REQUIRED and norm not in _NORMALIZED_EXTRA_ALLOWED
        ]

        if missing:
            errors.append(f"Columnas faltantes: {', '.join(missing)}")
        if extra:
            errors.append(f"Columnas no permitidas: {', '.join(extra)}")

        # Return usecols using canonical names from REQUIRED_COLUMNS where possible
        usecols = [
            _NORMALIZED_REQUIRED.get(_normalize(c), c)
            for c in usecols
            if _normalize(c) not in _NORMALIZED_EXTRA_ALLOWED
        ]

        return (len(errors) == 0, errors, usecols)

    @staticmethod
    def validate_row(row: dict, index: int) -> Dict[str, List[Dict[str, Any]]]:
        """Validates a CIARP row and returns errors and warnings."""
        errors, warnings = [], []

        if all(BaseValidator.is_empty(v) for v in row.values()):
            return {"errors": [], "warnings": []}

        errors.extend(RequiredFieldsCiarpValidator.validate(row, index))
        tipo_documento = str(row.get("tipo_documento") or "").strip()
        identificacion = str(row.get("identificación") or "").strip()
        errors.extend(DocumentValidator.validate(tipo_documento, identificacion, index))

        year_err = YearValidator.validate(row.get("año"), "año", index)
        if year_err:
            errors.append(year_err)

        warnings.extend(LanguageValidator.validator(row, index))
        warnings.extend(CountryValidator.validator(row, index))

        errors.extend(UnitValidator.validate(row, index))

        for field in WARNING_EMPTY_FIELDS:
            value = row.get(field)
            if BaseValidator.is_empty(value):
                warnings.append(
                    {
                        "fila": index,
                        "columna": field,
                        "detalle": f"El campo '{field}' está vacío.",
                        "valor": "",
                    }
                )

        return {"errors": errors, "warnings": warnings}

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> StaffReport:
        """Validates the full dataframe and builds a StaffReport."""
        errors: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []

        df = df.dropna(how="all").reset_index(drop=True)
        df = df.map(lambda v: v.strip() if isinstance(v, str) else v)
        df = df.apply(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else x)

        for idx, row in df.iterrows():
            result = CiarpValidator.validate_row(row.to_dict(), idx)
            errors.extend(result["errors"])
            warnings.extend(result["warnings"])

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
                            "index_excel": CiarpValidator.excel_row_index(int(idx)),
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
