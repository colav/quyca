from typing import List, Dict, Any


class ErrorGrouper:
    """
    Groups errors by column and detail, aggregating row numbers.
    """

    @staticmethod
    def group_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        grouped = {}
        for e in errors:
            key = (e["columna"], e["detalle"])
            if key not in grouped:
                grouped[key] = {"detalle": e["detalle"], "filas": []}
            grouped[key]["filas"].append(e["fila"])
        return [
            {
                "columna": col,
                "detalle": info["detalle"],
                "ejemplos": info["filas"][:3],
                "total_filas": len(info["filas"]),
            }
            for (col, _), info in grouped.items()
        ]

    """
    Groups warnings by column, detail, and value, aggregating row numbers.
    """

    @staticmethod
    def group_warnings(warnings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        grouped = {}
        for w in warnings:
            key = (w["columna"], w["detalle"], w.get("valor", ""))
            if key not in grouped:
                grouped[key] = {"detalle": w["detalle"], "valor": w.get("valor", ""), "filas": []}
            grouped[key]["filas"].append(w["fila"])
        return [
            {
                "columna": col,
                "detalle": info["detalle"],
                "valor": info["valor"],
                "ejemplos": info["filas"][:3],
                "total_filas": len(info["filas"]),
            }
            for (col, _, _), info in grouped.items()
        ]
