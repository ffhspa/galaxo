from GALAXO.CONFIG.Constants import Constants
class ProductDataUtils:
    
    @staticmethod
    def calculate_preisverlust_percentage(current_price, max_price):
        if max_price == 0 or current_price == 0:
            return 0.0
        percentage = 100 - ((current_price / max_price) * 100)
        return int(round(percentage))

    @staticmethod
    def evaluate_price_extremes(current_price, min_price, max_price):
        min_perc_diff = ((current_price - min_price) / min_price) * 100 if min_price else 0
        max_perc_diff = ((current_price - max_price) / max_price) * 100 if max_price else 0
        min_price_reached = current_price == min_price or abs(min_perc_diff) < Constants.PRODUCT_PERCENTAGE_CHANGE
        max_price_reached = current_price == max_price or  abs(max_perc_diff) < Constants.PRODUCT_PERCENTAGE_CHANGE
        return min_price_reached, max_price_reached

    @staticmethod
    def get_symbol(zahl):
        return "▲" if zahl > 0 else "▼"
