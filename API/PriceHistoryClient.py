from datetime import datetime
from dataclasses import dataclass
from GALAXO.CONFIG.Constants import Constants
from GALAXO.API.GraphQLClient import GraphQLClient
import base64


@dataclass
class PriceHistoryPoint:
    amount_incl: float
    valid_from: str

class PriceHistoryClient(GraphQLClient):
        
    def __init__(self):
        super().__init__()
        self.BASE_URL = Constants.BASE_URL_HISTORY

    def encode_product_id(self, product_id):                
        full_string = "Product\nd" + str(product_id) + ":1:406802"
        return base64.b64encode(full_string.encode()).decode()

    def fetch_price_chart(self, product_id):
        timestamp = datetime.now().isoformat() + "Z"

        encoded_id =  self.encode_product_id(product_id)

        payload = {
            "variables": {
                "id": encoded_id,
                "olderThan3MonthTimestamp": timestamp,
                "historyFrom": None
            }
        }
        try:           
            response = self.send_request(payload)
            return response
        except Exception as e:
            Constants.LOGGER.error(f"Fehler beim Abrufen der Preishistorie für Produkt-ID {product_id}: {e} {payload} {self.BASE_URL}  evtl. hat sich die URL geändert!!!!!")
            return {"error": str(e)}

    def get_pdp_price_history(self, product_id: str) -> dict:
        try:
            response = self.fetch_price_chart(product_id)
            points = response.get("data", {}).get("productById", {}).get("priceHistory", {}).get("points", [])

            price_history = [
                PriceHistoryPoint(
                    amount_incl=point["price"]["amountInclusive"],
                    valid_from=point["validFrom"][:10]
                )
                for point in points
                if point.get("price") and "amountInclusive" in point["price"] and "validFrom" in point
            ]

            # Prüfen, ob es Preispunkte gibt
            if not price_history:
                return {"min_price": None, "max_price": None}

            # Sortiere die Liste nach dem Datum (optional, aber falls du eine chronologische Reihenfolge benötigst)
            price_history.sort(key=lambda x: datetime.fromisoformat(x.valid_from), reverse=True)

            # Berechne den minimalen und maximalen Preis
            min_price = min(price_history, key=lambda x: x.amount_incl).amount_incl
            max_price = max(price_history, key=lambda x: x.amount_incl).amount_incl

            return {"min_price": min_price, "max_price": max_price}

        except Exception as e:
            Constants.LOGGER.error(f"Error in get_pdp_price_history for product {product_id}: {e}")
        return {"min_price": None, "max_price": None}
