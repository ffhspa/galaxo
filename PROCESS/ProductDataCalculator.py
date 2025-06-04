from GALAXO.UTILS.ProductDataUtils import ProductDataUtils
from GALAXO.CONFIG.Constants import Constants

class ProductDataCalculator:

    def __init__(self, product_data):
        self.product_data = product_data

    def calculate_price_and_stock_changes(self):
        stock_diff = self.product_data.stock_count - self.product_data.old_stock
        self.product_data.stock_changed_flag = stock_diff != 0
        self.product_data.stock_count_change = f"{self.product_data.stock_count} ({stock_diff:+d}){ProductDataUtils.get_symbol(stock_diff)}"

        self.product_data.price_change = self.product_data.current_price - self.product_data.old_price
        self.product_data.percentage_diff = (self.product_data.price_change / self.product_data.old_price * 100) if self.product_data.old_price else 0
        self.product_data.price_changed_flag = (
            self.product_data.current_price != self.product_data.old_price and abs(self.product_data.percentage_diff) > Constants.PRODUCT_PERCENTAGE_CHANGE
        )
        self.product_data.old_price_percentage = f"{int(round(self.product_data.percentage_diff))}%{ProductDataUtils.get_symbol(self.product_data.percentage_diff)}"

    def evaluate_price_extremes(self):
        self.product_data.min_flag, self.product_data.max_flag = ProductDataUtils.evaluate_price_extremes(
            self.product_data.current_price, self.product_data.min_price, self.product_data.max_price
        )
        self.product_data.both_changed_flag = self.product_data.price_changed_flag and self.product_data.stock_changed_flag
