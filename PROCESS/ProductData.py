from dataclasses import dataclass, asdict
from PROCESS.ProductDataCalculator import ProductDataCalculator

@dataclass
class ProductData:
    product_id: int
    product_name: str
    brand_name: str
    category_name: str
    current_price: float
    old_price: float
    stock_count: int
    old_stock: int
    min_price: float
    max_price: float
    min_price_erreicht: int
    max_price_erreicht: int
    preisverlust_percentage: int
    url: str
    image_url: str
    insert_date: int

    # Kontextfelder
    price_change: float = 0.0
    percentage_diff: int = 0
    old_price_percentage: str = ""
    price_changed_flag: bool = False
    stock_changed_flag: bool = False
    stock_count_change: str = ""
    both_changed_flag: bool = False
    min_flag: bool = False
    max_flag: bool = False

    def update_context_fields(self):
        # Die Berechnungen und die Logik sind nun in einer separaten Klasse
        product_data_calculator = ProductDataCalculator(self)
        product_data_calculator.calculate_price_and_stock_changes()
        product_data_calculator.evaluate_price_extremes()

    def to_dict(self) -> dict:
        return asdict(self)
