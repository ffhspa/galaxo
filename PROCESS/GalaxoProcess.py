from typing import List
from CONFIG.Constants import Constants
from PROCESS.ProductFactory import ProductFactory
from PROCESS.ProductStorage import ProductStorage
from PROCESS.ProductClient import ProductClient
from UTILS.Utils import Utils
from PROCESS.ProductData import ProductData

class GalaxoProcess:

    def __init__(self):
        self.product_client = ProductClient()
        raw_products = ProductStorage.load_products()
        self._cached_products: List[ProductData] = [
            ProductFactory.from_source(p) for p in raw_products
        ]

    def _fetch_all_products(self) -> List[ProductData]:
        return self._cached_products

    def insert_favorite_by_url(self, url: str):
        product_id = Utils.extract_product_id_from_url(url)
        if product_id is None or self.get_product(product_id) or product_id == '0' or product_id == 0:
            return

        details = self.product_client.get_full_product_details(product_id)
        pd = ProductFactory.from_source(details)
        self._cached_products.append(pd)
        self._save_products()

    def get_product(self, product_id: int) -> ProductData | None:
        return next((p for p in self._cached_products if p.product_id == product_id), None)

    def delete_product(self, product_id: int):
        self._cached_products = [
            p for p in self._cached_products if p.product_id != product_id
        ]
        self._save_products()

    def _update_product_price(self, pd: ProductData):
        try:
            details = self.product_client.get_full_product_details(
                pd.product_id, include_price_history=False
            )
            if details:
                ProductFactory.update_existing(pd, details)
        except Exception as e:
            Constants.LOGGER.error(
                f"Fehler bei Produkt {pd.product_id}: {e}", exc_info=True
            )

    def process_update_prices(self):
        """Update prices for all cached products sequentially."""
        for pd in self._cached_products:
            self._update_product_price(pd)

        self._save_products()

    def _save_products(self) -> None:
        ProductStorage.save_products([p.to_dict() for p in self._cached_products])

    def close(self) -> None:
        self.product_client.shutdown()
