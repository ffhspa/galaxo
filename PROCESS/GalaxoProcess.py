from typing import List
from GALAXO.CONFIG.Constants import Constants
from GALAXO.PROCESS.ProductFactory import ProductFactory
from GALAXO.PROCESS.ProductStorage import ProductStorage
from GALAXO.PROCESS.ProductClient import ProductClient
from GALAXO.UTILS.Utils import Utils
from GALAXO.PROCESS.ProductData import ProductData
from concurrent.futures import ThreadPoolExecutor, as_completed


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
        if product_id is None or self.get_product(product_id):
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

    def process_update_prices(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(
                    self.product_client.get_full_product_details, pd.product_id
                ): pd
                for pd in self._cached_products
            }

            for future in as_completed(futures):
                pd = futures[future]
                try:
                    details = future.result()
                    if details:
                        ProductFactory.update_existing(pd, details)
                except Exception as e:
                    Constants.LOGGER.error(f"Fehler bei Produkt {pd.product_id}: {e}", exc_info=True)

        self._save_products()

    def _save_products(self) -> None:
        ProductStorage.save_products([p.to_dict() for p in self._cached_products])

    def close(self) -> None:
        self.product_client.shutdown()
