import os
import sys
import atexit
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton
)
from pyvirtualdisplay import Display
from PROCESS.GalaxoProcess import GalaxoProcess
from PROCESS.ProductFactory import ProductFactory
from CONFIG.Constants import Constants

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

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Brand", "Preis", "Lager"
        ])
        self.refresh_button = QPushButton("Laden")
        self.refresh_button.clicked.connect(self.load_products)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.table)
        layout.addWidget(self.refresh_button)
        self.setCentralWidget(central)

        self.load_products()

    def load_products(self):
        raw_products = self.process._fetch_all_products()
        products = [ProductFactory.from_source(p) for p in raw_products]
        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(p.product_id)))
            self.table.setItem(row, 1, QTableWidgetItem(p.product_name))
            self.table.setItem(row, 2, QTableWidgetItem(p.brand_name))
            self.table.setItem(row, 3, QTableWidgetItem(f"{p.current_price:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(p.stock_count)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductListWindow()
    window.show()
    sys.exit(app.exec())
