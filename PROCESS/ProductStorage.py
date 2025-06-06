import datetime
import json
import os
import shutil
import glob
from datetime import datetime
import hashlib

from CONFIG.Constants import Constants

class ProductStorage:

    @staticmethod
    def load_products() -> list[dict]:
        if os.path.exists(Constants.JSON_PATH):
            with open(Constants.JSON_PATH, "r", encoding="utf-8") as f:
                products = json.load(f)
            Constants.LOGGER.info(f"Produkte erfolgreich geladen von: {Constants.JSON_PATH}")
            ProductStorage.backup_products_file()
            return products
        Constants.LOGGER.error("Keine Produktdatei gefunden Rückgabe einer leeren Liste.")
        return []
    
    @staticmethod
    def save_products(products: list[dict]):
        with open(Constants.JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
            Constants.LOGGER.info(f"Produkte erfolgreich gespeichert unter: {Constants.JSON_PATH}")

    @staticmethod
    def backup_products_file():
        file_path = Constants.JSON_PATH
        backup_dir = Constants.JSON_BACKUP_PATH

        if not os.path.exists(file_path):
            return

        os.makedirs(backup_dir, exist_ok=True)

        def calculate_md5(file_path):
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()

        latest_backup = None
        backup_files = sorted(
            glob.glob(os.path.join(backup_dir, f"{Constants.JSON_BACKUP_FILE_NAMES}*.json")),
            key=os.path.getmtime,
            reverse=True,
        )

        if backup_files:
            latest_backup = backup_files[0]

        if latest_backup:
            current_md5 = calculate_md5(file_path)
            backup_md5 = calculate_md5(latest_backup)
            if current_md5 == backup_md5:
                Constants.LOGGER.info("Kein Backup erforderlich: Dateiinhalt unverändert (MD5 identisch).")
                return

        # Backup erstellen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{Constants.JSON_BACKUP_FILE_NAMES}{timestamp}.json"
        backup_path = os.path.join(backup_dir, filename)

        shutil.copy(file_path, backup_path)
        Constants.LOGGER.info(f"Backup gespeichert unter {backup_path}")

        # Alte Backups aufräumen (nur die 5 neuesten behalten)
        backup_files = sorted(
            glob.glob(os.path.join(backup_dir, f"{Constants.JSON_BACKUP_FILE_NAMES}*.json")),
            key=os.path.getmtime,
            reverse=True,
        )

        for old_file in backup_files[5:]:
            try:
                os.remove(old_file)
                Constants.LOGGER.info(f"Altes Backup gelöscht: {old_file}")
            except Exception as e:
                Constants.LOGGER.warning(f"Konnte Backup nicht löschen: {old_file}  {e}")
