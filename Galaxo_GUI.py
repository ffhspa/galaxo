import os
import sys
import atexit
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QScrollArea,
    QGridLayout
)
from pyvirtualdisplay import Display
from PROCESS.GalaxoProcess import GalaxoProcess
from PROCESS.ProductFactory import ProductFactory
from CONFIG.Constants import Constants
from GUI.FilterFrame import FilterFrame
from GUI.ProductWidget import ProductWidget
from UTILS.Utils import Utils

# Start a virtual display if none is available (headless environments)
display = None
if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
    display = Display(visible=False, size=(1024, 768))
    display.start()
    atexit.register(display.stop)

class ProductListWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(Constants.TITLE)
        self.resize(1000, 700)
        self.process = GalaxoProcess()

        self.filter_frame = FilterFrame(
            self,
            self.apply_filters,
            self.apply_sort,
            self.delete_selected_products,
            self.apply_filters_debounced,
            self.update_prices,
            self.add_favorite,
        )

        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.grid = QGridLayout(self.scroll_area_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.filter_frame)
        layout.addWidget(self.scroll_area)
        self.setCentralWidget(central)

        self.all_products = []
        self.filtered_products = []
        self.product_widgets = []
        self.sort_options = Utils.get_sort_options()
        self.num_columns = Constants.NUM_COLUMNS
        self.load_products()

    def load_products(self):
        raw_products = self.process._fetch_all_products()
        self.all_products = [ProductFactory.from_source(p) for p in raw_products]
        self.on_products_loaded()

    def on_products_loaded(self):
        self.filter_frame.update_category_counts(self.all_products)
        self.apply_filters()

    def apply_filters_debounced(self):
        text = self.filter_frame.search_entry.text().strip()
        if "galaxus" in text or "digitec" in text:
            self.add_favorite()
            return
        QApplication.instance().processEvents()
        self.apply_filters()

    def apply_sort(self):
        sort_option = self.filter_frame.sort_combobox.currentText()
        sort_key = self.sort_options.get(sort_option)
        if sort_key:
            self.filtered_products = sorted(self.filtered_products, key=sort_key)
        self.place_products()

    def apply_filters(self):
        search_text = self.filter_frame.search_entry.text().strip().lower()
        selected_category_display = self.filter_frame.category_combobox.currentText()
        min_price = self.filter_frame.min_price_var.isChecked()
        only_updates = self.filter_frame.only_updates.isChecked()
        selected_category = "" if selected_category_display == Constants.CATEGORY_DEFAULT else self.filter_frame.category_mapping.get(selected_category_display, "")
        self.filtered_products = [
            p for p in self.all_products
            if Utils.matches_filters(p, min_price, search_text, selected_category, only_updates)
        ]
        self.apply_sort()

    def place_products(self):
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.product_widgets = []
        num_products = len(self.filtered_products)
        self.filter_frame.product_count_label.setText(f"Produkte: {num_products}")
        item_w = Constants.ITEM_WIDTH
        item_h = Constants.ITEM_HEIGHT
        for idx, product in enumerate(self.filtered_products):
            widget = ProductWidget(self.scroll_area_widget, product, Utils.get_border_color(product))
            row = idx // self.num_columns
            col = idx % self.num_columns
            self.grid.addWidget(widget, row, col)
            self.product_widgets.append(widget)

    def delete_selected_products(self):
        pass

    def update_prices(self):
        pass

    def add_favorite(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductListWindow()
    window.show()
    sys.exit(app.exec())
