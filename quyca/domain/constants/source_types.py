TYPE_DISPLAY_MAPPING = {
    "journal": "revista",
    "trade journal": "revista especializada",
    "book series": "serie de libros",
    "conference": "conferencia",
    "conference and proceedings": "conferencia y memorias de congreso",
    "ebook platform": "plataforma de libros electrónicos",
    "metadata": "metadatos",
    "other": "otro",
    "repository": "repositorio",
}

NORMALIZED_TYPE_MAPPING = {
    "E": "journal",
    "EL": "journal",
    "IE": "journal",
    "IM": "journal",
    "L": "journal",
    "P": "journal",
    "journal": "journal",
    "trade journal": "trade journal",
    "book series": "book series",
    "conference": "conference",
    "conference and proceedings": "conference and proceedings",
    "ebook platform": "ebook platform",
    "metadata": "metadata",
    "repository": "repository",
    "other": "other",
}

SOURCE_TITLES = {
    "openalex": "OpenAlex",
    "scimago": "Scimago",
    "scienti": "Scienti",
}

QUARTILE_MAPPING = {"Q1": "Q1", "Q2": "Q2", "Q3": "Q3", "Q4": "Q4", "-": "Sin cuartil"}
