from dataclasses import dataclass

"""Domain entity representing a staff member with identity and HR attributes."""


@dataclass
class Staff:
    tipo_documento: str
    identificacion: str
    primer_apellido: str
    segundo_apellido: str | None = None
    nombres: str = ""
    nivel_academico: str | None = None
    tipo_contrato: str | None = None
    jornada_laboral: str | None = None
    categoria_laboral: str | None = None
    sexo: str | None = None
    fecha_nacimiento: str | None = None
    fecha_inicial_vinculacion: str | None = None
    fecha_final_vinculacion: str | None = None
    codigo_unidad_academica: str | None = None
    unidad_academica: str | None = None
    codigo_subunidad_academica: str | None = None
    subunidad_academica: str | None = None
