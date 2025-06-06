from API.GraphQLClient import GraphQLClient

class OfferAvailabilityClient(GraphQLClient):
    
    def get_offer_availability(self, product_id, sales_offer_id, offer_type):
        query = [{
            "operationName": "GET_OFFER_AVAILABILITY_V2",
            "variables": {
                "productId": product_id,
                "salesOfferId": sales_offer_id,
                "salesOfferType": offer_type,
                "refurbishedId": None,
                "resaleId": None
            },
            "query": """
                query GET_OFFER_AVAILABILITY_V2($productId: Int!, $salesOfferId: Int!, $salesOfferType: ShopOfferType!, $refurbishedId: Int, $resaleId: Int) {
                    offerAvailabilityV2(
                        productId: $productId,
                        salesOfferId: $salesOfferId,
                        offerType: $salesOfferType,
                        refurbishedId: $refurbishedId,
                        resaleId: $resaleId
                    ) {
                        id
                        mail {
                            stockDetails {
                                stockCount
                            }
                        }
                    }
                }
            """
        }]
        
        try:
            response = self.send_request(query)
            return response[0]["data"].get("offerAvailabilityV2", {}).get("mail", {}).get("stockDetails", {}).get("stockCount", 0)        
        except Exception as e:
            return 0
