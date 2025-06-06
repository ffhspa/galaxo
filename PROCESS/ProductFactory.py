from typing import Union
from datetime import datetime
from PROCESS.ProductClient import ProductDetails
from PROCESS.ProductData import ProductData
from PROCESS.ProductDataCalculator import ProductDataCalculator
from UTILS.ProductDataUtils import ProductDataUtils

class ProductFactory:

    @staticmethod
    def from_source(source: Union[dict, ProductDetails]) -> ProductData:
        get = lambda k, d=None: ProductFactory._get(source, k, d)

        current_price = float(get("current_price", 0))
        stock_count = int(get("stock_count", 0))
        min_price = float(get("min_price", 0))
        max_price = float(get("max_price", 0))
        preisverlust = ProductDataUtils.calculate_preisverlust_percentage(current_price, max_price)

        product = ProductData(
            product_id=int(get("product_id", 0)),
            product_name=str(get("product_name", "")),
            brand_name=str(get("brand_name", "")),
            category_name=str(get("category_name", "")),
            current_price=current_price,
            old_price=float(get("old_price", current_price)),
            stock_count=stock_count,
            old_stock=int(get("old_stock", stock_count)),
            min_price=min_price,
            max_price=max_price,
            min_price_erreicht=int(current_price <= min_price),
            max_price_erreicht=int(current_price >= max_price),
            preisverlust_percentage=preisverlust,
            url=str(get("url", "")),
            image_url=str(get("image_url", "")),
            insert_date=int(get("insert_date", datetime.now().timestamp())),
        )

        # Kontextfelder werden in einer separaten Klasse berechnet
        calculator = ProductDataCalculator(product)
        calculator.calculate_price_and_stock_changes()
        calculator.evaluate_price_extremes()

        return product

    @staticmethod
    def update_existing(existing: ProductData, source: Union[dict, ProductDetails]) -> ProductData:
        get = lambda k, d=None: ProductFactory._get(source, k, d)

        # Backup alte Werte
        existing.old_price = existing.current_price
        existing.old_stock = existing.stock_count

        # Neue Rohdaten auslesen
        new_price = float(get("current_price", existing.current_price))
        new_stock = int(get("stock_count", existing.stock_count))

        # Felder aktualisieren
        existing.product_name = str(get("product_name", existing.product_name))
        existing.brand_name = str(get("brand_name", existing.brand_name))
        existing.category_name = str(get("category_name", existing.category_name))
        existing.url = str(get("url", existing.url))
        existing.image_url = str(get("image_url", existing.image_url))
        existing.insert_date = int(get("insert_date", existing.insert_date))

        # Nur echte Extremwerte aktualisieren!
        existing.min_price = min(existing.min_price, new_price)
        existing.max_price = max(existing.max_price, new_price)

        # Preis & Lagerstand übernehmen
        existing.current_price = new_price
        existing.stock_count = new_stock

        # Kontextberechnungen
        calculator = ProductDataCalculator(existing)
        calculator.calculate_price_and_stock_changes()
        calculator.evaluate_price_extremes()

        return existing

    @staticmethod
    def _get(source: Union[dict, ProductDetails], key: str, fallback=None):
        if isinstance(source, dict):
            return source.get(key, fallback)
        return getattr(source, key, fallback)
