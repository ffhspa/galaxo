from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from CONFIG.Constants import Constants
from UTILS.Utils import Utils

class ProductWidget(QFrame):
    def __init__(self, parent, product=None, border_color="white", toggle_selection_callback=None):
        super().__init__(parent)
        self.product = None
        self.toggle_selection_callback = toggle_selection_callback
        self.is_selected = False
        self.layout = QVBoxLayout(self)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)
        self.text_labels = []
        if product:
            self.update_product(product, border_color)
        self.setStyleSheet("background:white")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setLineWidth(2)

    def _set_border(self, color):
        self.setStyleSheet(f"background:white;border:2px solid {color}")

    def update_product(self, product, border_color):
        if not product or product == self.product:
            return
        self.product = product
        self._set_border(border_color)
        pixmap = QPixmap(Utils.get_file_hash_path(product.image_url))
        if pixmap and not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaled(*Constants.IMAGE_SIZE, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.image_label.setText("Kein Bild")
        for lbl in self.text_labels:
            self.layout.removeWidget(lbl)
            lbl.deleteLater()
        self.text_labels = []
        fields = [
            (product.brand_name, True),
            (product.product_name, False),
            (f"Preis: {product.current_price:.2f}", False),
            (f"Lager: {product.stock_count}", False),
        ]
        for text, bold in fields:
            label = QLabel(text)
            if bold:
                label.setStyleSheet("font-weight: bold")
            label.setWordWrap(True)
            self.layout.addWidget(label)
            self.text_labels.append(label)

