import json
from pymongo import MongoClient
from os import environ, path
from sys import exit
import warnings
import argparse

warnings.filterwarnings("ignore", message="Pydantic serializer warnings:")
warnings.filterwarnings("ignore")
import time

if "QUYCA_CONFIG_FILE" in environ:
    print("Using configuration file:", environ["QUYCA_CONFIG_FILE"])
else:
    print("No configuration file set, please export QUYCA_CONFIG_FILE with th e path to your config file.")
    exit(1)

from quyca.domain.services.api_expert_service import search_works
from quyca.models.base_model import QueryParams

qp = QueryParams()
qp.page = 1
qp.limit = 250
qp.sort = None


def main() -> None:
    parser = argparse.ArgumentParser(description="Exportar works de MongoDB a un archivo JSON.")
    parser.add_argument("output_file", help="Nombre del archivo de salida (ej. impactu.json)")
    parser.add_argument("database_name", help="Nombre de la base de datos MongoDB (ej. kahi_dev)")
    args = parser.parse_args()

    MongoClient()[args.database_name]["works"].count_documents({})

    start_total = time.time()
    if path.exists(args.output_file):
        confirm = (
            input(f"The file '{args.output_file}' already exists. Do you want to overwrite it? [y/N]: ").strip().lower()
        )
        if confirm != "y":
            print("Operation canceled.")
            exit(0)
    with open(args.output_file, "w", encoding="utf-8") as f:
        f.truncate(0)  # Borra el contenido del archivo
        f.seek(0)
        f.write("[\n")
        first = True
        qp.page = 1
        works = search_works(qp)
        while works["data"]:
            start_iter = time.time()
            for item in works["data"]:
                if not first:
                    f.write(",\n")
                json.dump(item, f, ensure_ascii=False)
                first = False
            qp.page += 1
            works = search_works(qp)
            end_iter = time.time()
            elapsed_iter = end_iter - start_iter
            elapsed_total = end_iter - start_total
            print(f"Time for page {qp.page-1}: {elapsed_iter:.2f}s — Total time: {elapsed_total:.2f}s")

        f.write("\n]")


if __name__ == "__main__":
    main()
