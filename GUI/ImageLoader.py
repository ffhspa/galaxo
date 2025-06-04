import os
import time
import threading
from io import BytesIO
from PIL import Image, ImageTk
import requests
from requests.adapters import HTTPAdapter
from GALAXO.UTILS.Utils import Utils
from GALAXO.CONFIG.Constants import Constants

class ImageLoader:
    _session = requests.Session()
    _session.mount('https://', HTTPAdapter(pool_connections=100, pool_maxsize=100))
    _session.mount('http://', HTTPAdapter(pool_connections=100, pool_maxsize=100))

    def __init__(self, image_label=None, image_url=None):
        self.image_label = image_label
        self.image_url = image_url
        self.image_size = Constants.IMAGE_SIZE
        self.cache_dir = Constants.CACHE_DIR_IMAGES
        self.max_retries = 3
        self.initial_delay = 1
        self.timeout = 4
        self.photo_image = None

        os.makedirs(self.cache_dir, exist_ok=True)

    def load_image(self):
        threading.Thread(target=self._load_image_thread, daemon=True).start()

    def _load_image_thread(self):
        try:
            cache_path = self._fetch_image(self.image_url)
            self.image_label.after(0, lambda: self._prepare_display(cache_path))
        except Exception as e:
            Constants.LOGGER.exception("Bildladefehler im Thread")

    def _fetch_image(self, url):

        cache_path = Utils.get_file_hash_path(url)
        if os.path.exists(cache_path):
            return cache_path

        delay = self.initial_delay
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self._session.get(url, timeout=self.timeout)
                response.raise_for_status()
                with Image.open(BytesIO(response.content)) as img:
                    img.thumbnail(self.image_size, Image.LANCZOS)
                    img.save(cache_path, format='PNG')
                Constants.LOGGER.info(f"Bild erfolgreich geladen und gecached: {cache_path}")
                return cache_path
            except Exception as e:
                Constants.LOGGER.warning(f"Versuch {attempt} fehlgeschlagen für {url}: {e}")
                if attempt < self.max_retries:
                    time.sleep(delay)
                    delay *= 2
        Constants.LOGGER.error(f"Alle Download-Versuche fehlgeschlagen für: {url}")
        return None

    def _prepare_display(self, path):
        try:
            with Image.open(path) as img:
                img.thumbnail(self.image_size, Image.LANCZOS)
                image_copy = img.copy()
            self.image_label.after(0, lambda: self._display_image(image_copy, path))
        except Exception as e:
            Constants.LOGGER.exception("Fehler beim Öffnen/Croppen des Bildes")

    def _display_image(self, pil_image, path):
        try:
            self.photo_image = ImageTk.PhotoImage(pil_image)
            self.image_label.config(image=self.photo_image, text="", bg="#FFFFFF")
            self.image_label.image = self.photo_image
            self.image_label.image_path = path
        except Exception as e:
            Constants.LOGGER.exception("Fehler bei ImageTk.PhotoImage")
