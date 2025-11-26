import io
import pandas as pd


class XlsxWriteExporter:
    """
    Exports annotated DataFrame to XLSX, with row coloring and autofilter.
    """

    @staticmethod
    def to_excel_bytes(df: pd.DataFrame) -> io.BytesIO:
        output = io.BytesIO()

        def sort_identification(val):
            try:
                return (0, int(val))
            except:
                return (1, str(val))

        with pd.ExcelWriter(output, engine="xlsxwriter") as write:
            df_sorted = df.sort_values(by="identificación", key=lambda col: col.map(sort_identification))
            df_sorted.to_excel(write, index=False, sheet_name="Validación")

            workbook = write.book
            worksheet = write.sheets["Validación"]

            fmt_error = workbook.add_format({"bg_color": "#ffbaa6"})
            fmt_warn = workbook.add_format({"bg_color": "#ffecac"})
            fmt_dup = workbook.add_format({"bg_color": "#a6d4e2"})

            for row_num, value in enumerate(df_sorted["estado_de_validación"], start=1):
                if "Error" in value:
                    fmt = fmt_error
                elif "Advertencia" in value:
                    fmt = fmt_warn
                elif "Duplicado" in value:
                    fmt = fmt_dup
                else:
                    fmt = None

                if fmt:
                    for col_num, cell_value in enumerate(df_sorted.iloc[row_num - 1]):
                        if pd.isna(cell_value) or cell_value in [float("inf"), float("-inf")]:
                            worksheet.write(row_num, col_num, "", fmt)
                        else:
                            worksheet.write(row_num, col_num, cell_value, fmt)

            for i, col in enumerate(df_sorted.columns):
                max_len = max(df_sorted[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_len)

            worksheet.autofilter(0, 0, len(df_sorted), len(df_sorted.columns) - 1)

        output.seek(0)
        return output
