from typing import Optional

from API.ProductDetailsClient_PDP import ProductDetailsClient_PDP
from CONFIG.Constants import Constants
from API.OfferAvailabilityClient import OfferAvailabilityClient
from API.PriceHistoryClient import PriceHistoryClient


class ProductDetails:
    def __init__(self, current_price, image_url, product_name, brand_name,
                 url, category_name, product_id, stock_count, min_price, max_price):
        self.current_price = current_price
        self.image_url = image_url
        self.product_name = product_name
        self.brand_name = brand_name
        self.url = url
        self.category_name = category_name
        self.product_id = product_id
        self.stock_count = stock_count
        self.min_price = min_price
        self.max_price = max_price

    def to_dict(self):
        return self.__dict__


class ProductClient:
    def __init__(
        self,
        details_client: Optional[ProductDetailsClient_PDP] = None,
        availability_client: Optional[OfferAvailabilityClient] = None,
        price_history_client: Optional[PriceHistoryClient] = None
    ):
        self.details_client = details_client or ProductDetailsClient_PDP()
        self.availability_client = availability_client or OfferAvailabilityClient()
        self.price_history_client = price_history_client or PriceHistoryClient()
        self.logger = Constants.LOGGER

    def get_full_product_details(self, product_id: str) -> Optional[ProductDetails]:
        self.logger.info(f"Fetching full product details for: {product_id}")
        try:
            pdp_data = self.details_client.get_product_details_pdp(product_id)

            try:
                price_history = self.price_history_client.get_pdp_price_history(product_id)
            except Exception as e:
                self.logger.warning(
                    f"Price history unavailable for {product_id}: {e}", exc_info=True
                )
                price_history = {}

            try:
                stock_count = self.availability_client.get_offer_availability(
                    product_id, pdp_data.offer_id, pdp_data.offer_type
                )
            except Exception as e:
                self.logger.warning(
                    f"Stock count unavailable for {product_id}: {e}", exc_info=True
                )
                stock_count = 0

            current_price = pdp_data.price
            min_price = (price_history or {}).get("min_price") or current_price
            max_price = (price_history or {}).get("max_price") or current_price
            min_price = min(min_price, current_price)

            return ProductDetails(
                current_price=current_price,
                image_url=pdp_data.image_url,
                product_name=pdp_data.name,
                brand_name=pdp_data.brand,
                url=pdp_data.product_url,
                category_name=pdp_data.category,
                product_id=product_id,
                stock_count=stock_count,
                min_price=min_price,
                max_price=max_price
            )

        except Exception as e:
            self.logger.error(f"Unhandled error for {product_id}: {e}", exc_info=True)
            return None

    def shutdown(self):
        if hasattr(self.details_client, "close"):
            self.details_client.close()
        if hasattr(self.availability_client, "close"):
            self.availability_client.close()
        if hasattr(self.price_history_client, "close"):
            self.price_history_client.close()
