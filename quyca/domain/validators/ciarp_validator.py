from typing import List, Dict, Any, Tuple
import pandas as pd
from domain.models.staff_report_model import StaffReport
from domain.validators.required_fields_validator_ciarp import RequiredFieldsCiarpValidator
from domain.validators.document_validator import DocumentValidator
from domain.validators.base_validator import BaseValidator
from domain.validators.year_validator import YearValidator
from domain.validators.language_validator import LanguageValidator
from domain.validators.country_validator import CountryValidator
from domain.validators.unit_validator import UnitValidator
from domain.validators.error_grouper import ErrorGrouper

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


class CiarpValidator:
    """
    Maps DataFrame index to Excel row number (header=1 → first row=2).
    """

    @staticmethod
    def excel_row_index(idx: int) -> int:
        return idx + 2

    """
    Verifies schema: required columns present, extra columns flagged, ignores unnamed/index columns.
    """

    @staticmethod
    def validate_columns(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
        raw_cols = [str(c).lower().strip() for c in df.columns]
        errors: List[str] = []
        usecols: List[str] = []

        expected = list(REQUIRED_COLUMNS)

        for idx, c in enumerate(raw_cols):
            col = str(c).strip()

            if idx == 0 and (col == "" or col.lower() == "index" or col.lower().startswith("unnamed")):
                continue

            if col == "" or col.lower().startswith("unnamed"):
                if not df.iloc[:, idx].dropna(how="all").empty:
                    errors.append(f"Columna sin nombre en posición {idx+1}")
                continue

            usecols.append(col)
        missing = [c for c in expected if c not in usecols]
        extra = [c for c in usecols if c not in expected and c not in EXTRA_ALLOWED]

        if missing:
            errors.append(f"Columna faltantes: {', '.join(missing)}")
        if extra:
            errors.append(f"Columnas no permitidas: {', '.join(extra)}")

        return (len(errors) == 0, errors, raw_cols)

    """
    Applies CIARP row validations: required, document, year, language, country, units + empties as warnings.
    """

    @staticmethod
    def validate_row(row: dict, index: int) -> Dict[str, List[Dict[str, Any]]]:
        errors, warnings = [], []

        if all(BaseValidator.is_empty(v) for v in row.values()):
            return {"errores": [], "advertencias": []}

        errors.extend(RequiredFieldsCiarpValidator.validate(row, index))
        errors.extend(DocumentValidator.validate(row.get("tipo_documento"), row.get("identificación"), index))

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

        return {"errores": errors, "advertencias": warnings}

    """
    Validates the whole DataFrame (clean blanks, normalize cells, detect duplicates).
    """

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> StaffReport:
        errors, warnings = [], []

        df = df.dropna(how="all").reset_index(drop=True)

        df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)

        df = df.applymap(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else x)

        for idx, row in df.iterrows():
            result = CiarpValidator.validate_row(row.to_dict(), idx)
            errors.extend(result["errores"])
            warnings.extend(result["advertencias"])

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
            total_errores=len(errors),
            total_duplicados=total_dups,
            errores=errors,
            errores_agrupados=ErrorGrouper.group_errors(errors),
            advertencias=warnings,
            advertencias_agrupadas=ErrorGrouper.group_warnings(warnings),
            duplicados=duplicate_info,
        )
