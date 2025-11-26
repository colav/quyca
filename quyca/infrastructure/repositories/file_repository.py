import os
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import current_app
from infrastructure.repositories.google_drive_repository import GoogleDriveRepository


class FileRepository:
    def __init__(self, drive_repo: GoogleDriveRepository):
        self.drive_repo = drive_repo

    """
    Saves a file locally, uploads it to Drive in the proper folder, then deletes it from 
    the temporary server
    """

    def save_file(self, file, ror_id: str, institution: str, file_type: str):
        timestamp = datetime.now(ZoneInfo("America/Bogota")).strftime("%d_%m_%Y_%H:%M")
        filename = f"{file_type}_{ror_id}_{timestamp}.xlsx"

        temp_path = os.path.join("/tmp", filename)
        file.save(temp_path)

        try:
            root_folder = self.drive_repo.get_or_create_folder(file_type)
            user_folder_name = f"{ror_id}_{institution}"
            user_folder = self.drive_repo.get_or_create_folder(user_folder_name, parent_id=root_folder)

            self.drive_repo.upload_file(temp_path, filename, user_folder)

            os.remove(temp_path)
            return {"success": True, "msg": f"Archivo {filename} guardado correctamente."}

        except Exception:
            try:
                local_base = current_app.config.get("LOCAL_STORAGE_PATH")
                if not local_base:
                    raise ValueError("No se encontró la configuración LOCAL_STORAGE_PATH")

                type_folder = os.path.join(local_base, file_type)
                os.makedirs(type_folder, exist_ok=True)

                user_folder = os.path.join(type_folder, f"{ror_id}_{institution}")
                os.makedirs(user_folder, exist_ok=True)

                local_path = os.path.join(user_folder, filename)
                shutil.move(temp_path, local_path)

                return {
                    "success": True,
                    "msg": f"Archivo {filename} guardado correctamente en almacenamiento local.",
                    "path": local_path,
                }
            except Exception as fallback_err:
                return {
                    "success": False,
                    "msg": f"Error al guardar el archivo tanto en Drive como en local. Detalle: {fallback_err}",
                    "location": None,
                }
