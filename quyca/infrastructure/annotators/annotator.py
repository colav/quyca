import pandas as pd
from domain.models.staff_report_model import StaffReport


class Annotator:
    """
    Adds validation state/notes to the DataFrame for Excel export.
    """

    @staticmethod
    def annotate(df: pd.DataFrame, staff_report: StaffReport) -> pd.DataFrame:
        df_copy = df.copy()
        df_copy["estado_de_validación"] = ""
        df_copy["observación"] = ""

        for err in staff_report.errores:
            row = err.get("fila")
            detail = err.get("detalle", "")
            column = err.get("columna", "")
            if row in df_copy.index:
                df_copy.at[row, "estado_de_validación"] += "Error | "
                df_copy.at[row, "observación"] += f"{detail} {column} | "

        for warn in staff_report.advertencias:
            row = warn.get("fila")
            detail = warn.get("detalle", "")
            if row in df_copy.index:
                df_copy.at[row, "estado_de_validación"] += "Advertencia | "
                df_copy.at[row, "observación"] += f"{detail} | "

        for dup in staff_report.duplicados:
            row = dup.get("index")
            if row in df_copy.index:
                df_copy.at[row, "estado_de_validación"] += "Duplicado | "
                df_copy.at[row, "observación"] += "Registro duplicado | "

        df_copy["observación"] = df_copy["observación"].str.rstrip(" |")

        def clean_state(value: str) -> str:
            states = [s.strip() for s in value.split("|") if s.strip()]
            priority = ["Error", "Advertencia", "Duplicado"]
            return " | ".join([p for p in priority if p in states])

        df_copy["estado_de_validación"] = df_copy["estado_de_validación"].apply(clean_state)

        if "Unnamed: 0" in df_copy.columns:
            df_copy = df_copy.drop(columns=["Unnamed: 0"])

        if "index" in df_copy.columns:
            df_copy = df_copy.drop(columns=["index"])

        return df_copy
