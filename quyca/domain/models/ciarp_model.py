from dataclasses import dataclass

"""
Domain entity for CIARP records (research products metadata).
"""


@dataclass
class CIARP:
    codigo_unidad_academica: str
    codigo_subunidad_academica: str | None = None
    tipo_documento: str
    identificacion: str
    año: int
    titulo: str
    idioma: str | None = None
    revista: str | None = None
    editorial: str | None = None
    doi: str | None = None
    issn: str | None = None
    isbn: str | None = None
    volumen: str | None = None
    issue: str | None = None
    primera_pagina: str | None = None
    ultima_pagina: str | None = None
    pais_producto: str
    entidad_premiadora: str | None = None
    ranking: str | None = None
