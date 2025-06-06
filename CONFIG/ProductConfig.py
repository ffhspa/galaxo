from UTILS.Utils import Utils
from CONFIG.Constants import Constants
from PROCESS.ProductFactory import ProductFactory

class ProductConfig:
    @staticmethod
    def get_config(product: dict):
        
        product_data = ProductFactory.from_source(product)

        # Modus bestimmen
        mode = (
            'both' if product_data.price_changed_flag and product_data.stock_changed_flag else
            'price_change' if product_data.price_changed_flag else
            'stock_change' if product_data.stock_changed_flag else
            'base'
        )
        # GUI-Feldkonfiguration zurückgeben
        return {
            key: (info_key, Utils.create_font(size, weight))
            for key, (info_key, size, weight) in Constants.PRODUCT_FIELD_CONFIG[mode].items()
        }
