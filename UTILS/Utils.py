import hashlib
import os
from functools import lru_cache
from PyQt6.QtGui import QFont
from CONFIG.Constants import Constants
from datetime import datetime
import re
from urllib.parse import urlsplit

class Utils:

    @staticmethod
    @lru_cache(maxsize=1)
    def get_sort_options():
        return {
                Constants.SORT_PRICE_UP: lambda x: float(x.current_price),
                Constants.SORT_PRICE_DOWN: lambda x: -float(x.current_price),
                Constants.SORT_TIME: lambda x: -int(x.insert_date),
        }

    @staticmethod
    def get_sort_options_keys():
        return list(Utils.get_sort_options().keys())

    @staticmethod
    @lru_cache(maxsize=None)
    def create_font(size, weight="normal", family="Arial"):
        font = QFont(family, size)
        if weight == "bold":
            font.setWeight(QFont.Weight.Bold)
        return font

    @staticmethod
    def truncate_text(text):
        if isinstance(text, str) and len(text) > Constants.CHAR_LIMIT:
            return f"{text[:Constants.CHAR_LIMIT]}..."
        return text

    @staticmethod
    def format_label_text(key, default_text, text=0):
        formatted = str(text)        
        if key in Constants.PRODUCT_INFO_PERCENTAGE_ITEMS:
            formatted = f"{text}%"
        elif key in Constants.PRODUCT_INFO_LABEL_CONTEXT_ITEMS:
            formatted = Utils.format_price(text)
            
        return f"{default_text}: {formatted}" if default_text else formatted

    @staticmethod
    def get_border_color(productdata):
        
        if productdata.current_price == 0:
            return Constants.PRODUCT_NOT_AVAILABLE_COLOR
        if productdata.both_changed_flag:
            return Constants.CHANGED_BOTH_BORDER_COLOR
        if productdata.price_changed_flag:
            return Constants.CHANGED_PRICE_BORDER_COLOR
        if productdata.stock_changed_flag:
            return Constants.CHANGED_STOCK_BORDER_COLOR
        if productdata.min_flag:
            return Constants.REACHED_MIN_BORDER_COLOR
        if productdata.max_flag:
            return Constants.REACHED_MAX_PRICE_COLOR
        return Constants.DEFAULT_BORDER_COLOR

    @staticmethod
    def matches_filters(product, min_price_filter, search_text, selected_category,only_updates):
        price_match = not min_price_filter or product.min_flag
        updates = not only_updates or (product.both_changed_flag or product.stock_changed_flag or product.price_changed_flag)
        
        category_match = selected_category in ["", product.category_name or ""]

        if search_text.isdigit():
            search_match = int(search_text) == product.product_id
        else:
            fields_to_search = [
                product.product_name,
                product.brand_name,
                product.category_name,
            ]
            search_match = any(
                search_text.lower() in str(field).lower()
                for field in fields_to_search
                if field
            )

        return price_match and category_match and search_match and updates

    @staticmethod
    def get_file_hash_path(image_url):
        return Utils._cached_hash_path(urlsplit(image_url).path)

    @staticmethod
    @lru_cache(maxsize=128)
    def _cached_hash_path(path: str) -> str:
        filename = hashlib.md5(path.encode()).hexdigest() + ".png"
        return os.path.join(Constants.CACHE_DIR_IMAGES, filename)

    @staticmethod
    def delete_image(image_url):
        try:
            cache_path = Utils.get_file_hash_path(image_url)
            if os.path.exists(cache_path):
                os.remove(cache_path)
                Constants.LOGGER.info(f"Bild gelöscht: {cache_path}")
            else:
                Constants.LOGGER.warning(f"Bild existiert nicht oder konnte nicht geladen werden: {image_url}")
        except Exception as e:
            Constants.LOGGER.error(f"Fehler beim Löschen des Bildes: {e}")



    @staticmethod
    def contains_error():
        log_file_path = os.path.join(Constants.LOG_PATH, Constants.LOG_FILE_NAME)
        today_str = datetime.today().strftime('%Y-%m-%d')

        try:
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return any(
                    line.startswith(today_str) and 'ERROR' in line
                    for line in file
                )
        except OSError:
            return False
    

    @staticmethod
    def float_or_default(value, default=1.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def calculate_preisverlust_percentage(current_price, max_price):
        if max_price == 0 or current_price == 0:
            return 0.0
        percentage = 100 - ((current_price / max_price) * 100)
        return round(percentage, 2)

    @staticmethod
    def format_price(value: float) -> str:
        return f"{float(value):.2f}"

    @staticmethod
    def extract_product_id_from_url(url: str) -> int | None:
        cleaned_url = re.sub(r"\?.*", "", url)
        match = re.search(r"(\d+)$", cleaned_url)
        return int(match.group(1)) if match else None
    

