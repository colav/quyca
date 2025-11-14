from datetime import datetime


class YearValidator:
    """
    Validates that the provided year is numeric and not in the future.
    """

    @staticmethod
    def validate(value, field: str, index: int):
        if value is None or str(value).strip() == "":
            return None
        try:
            year = int(value)
            current_year = datetime.now().year
            if year > current_year:
                return {
                    "fila": index,
                    "columna": field,
                    "detalle": "Año no valido",
                    "valor": value,
                }
        except Exception:
            return {"fila": index, "columna": field, "detalle": f"Formato inválido, debe ser númerico", "valor": value}
        return None
