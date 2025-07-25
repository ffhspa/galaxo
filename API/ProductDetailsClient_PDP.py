from CONFIG.Constants import Constants
from API.RequestGraphQLClient import RequestGraphQLClient

class ProductDetails:
    def __init__(self, name, brand, product_id, price, image_url, product_url, category, offer_id, shop_offer_id,offer_type):
        self.name = name
        self.brand = brand
        self.product_id = product_id
        self.price = price
        self.image_url = image_url
        self.product_url = product_url
        self.category = category
        self.offer_id = offer_id
        self.shop_offer_id = shop_offer_id
        self.offer_type = offer_type
        
class ProductDetailsClient_PDP(RequestGraphQLClient):
    
    def get_product_details_pdp(self, product_id):
        
        query = [{
            "operationName": "PDP_GET_PRODUCT_DETAILS",
            "variables": {"productId": product_id},
            "query": """query PDP_GET_PRODUCT_DETAILS($productId: Int!) { 
                productDetails: productDetailsV3(productId: $productId) { 
                    product { id productId name productTypeName brandName images { url } }
                    offers { id productId offerId shopOfferId type price { amountInclusive } supplier { name } }
                    productDetails { canonicalUrl }
                } 
            }"""
        }]
     
        try:
            response = self.send_request(query)
            product_info = response[0]["data"]["productDetails"]
            product_data = product_info["product"]
            
            offers = product_info.get("offers", [])
            product_url = product_info.get("productDetails", {}).get("canonicalUrl", "")            
            image_url = product_data['images'][0]['url']
                        
            valid_offers = [
                offer for offer in offers
                if offer.get("supplier") and offer["supplier"].get("name")
            ]
                        
            price = 0
            cheapest_offer_id = None
            cheapest_shop_offer_id = None
            cheapest_offer_type = ''
            
            if valid_offers:
                cheapest_offer = min(valid_offers, key=lambda x: x["price"]["amountInclusive"])
                price = cheapest_offer["price"]["amountInclusive"]
                cheapest_offer_id = cheapest_offer["offerId"]
                cheapest_shop_offer_id = cheapest_offer["shopOfferId"]
                cheapest_offer_type = cheapest_offer["type"]
            
                    
            return ProductDetails(
                name=product_data.get("name", ""),
                brand=product_data.get("brandName", ""),
                product_id=product_id,
                price=price,
                image_url=image_url,
                product_url=product_url,
                category=product_data.get("productTypeName", ""),
                offer_id=cheapest_offer_id,
                shop_offer_id=cheapest_shop_offer_id,
                offer_type=cheapest_offer_type
            )

        except Exception as e:
            Constants.LOGGER.error(f"Fehler in get_product_details_pdp für Produkt {product_id}: {e}", exc_info=True)
            return None
