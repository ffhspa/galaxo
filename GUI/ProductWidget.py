from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
from CONFIG.Constants import Constants
from CONFIG.ProductConfig import ProductConfig
from UTILS.Utils import Utils
import webbrowser
import os
import requests

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
        self.single_click_timer = QTimer(self)
        self.single_click_timer.setSingleShot(True)
        self.single_click_timer.timeout.connect(self._toggle_selection)
        if product:
            self.update_product(product, border_color)
        self.setStyleSheet("background:white")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setLineWidth(2)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.single_click_timer.start(200)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.single_click_timer.isActive():
                self.single_click_timer.stop()
            self._open_product_url()
        super().mouseDoubleClickEvent(event)

    def _set_border(self, color):
        self.setStyleSheet(f"background:white;border:2px solid {color}")

    def _update_image(self):
        if not self.product or not self.product.image_url:
            self.image_label.setText("Kein Bild")
            return
        cache_path = Utils.get_file_hash_path(self.product.image_url)
        if not os.path.exists(cache_path):
            try:
                resp = requests.get(self.product.image_url, timeout=4)
                resp.raise_for_status()
                with open(cache_path, "wb") as f:
                    f.write(resp.content)
            except Exception:
                cache_path = None
        if cache_path and os.path.exists(cache_path):
            pixmap = QPixmap(cache_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    *Constants.IMAGE_SIZE,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.image_label.setPixmap(pixmap)
                return
        self.image_label.setText("Kein Bild")

    def _create_labels(self, config):
        for key, (default_text, font) in config.items():
            value = getattr(self.product, key, "")
            truncated = Utils.truncate_text(value)
            text = Utils.format_label_text(key, default_text, truncated)
            label = QLabel(text)
            label.setFont(font)
            label.setWordWrap(True)
            self.layout.addWidget(label)
            self.text_labels.append(label)

    def _update_labels(self):
        config = ProductConfig.get_config(self.product)
        for lbl in self.text_labels:
            self.layout.removeWidget(lbl)
            lbl.deleteLater()
        self.text_labels = []
        self._create_labels(config)

    def _toggle_selection(self):
        self.is_selected = not self.is_selected
        bg = Constants.SELECTED_COLOR if self.is_selected else "white"
        border = Utils.get_border_color(self.product)
        self.setStyleSheet(f"background:{bg};border:2px solid {border}")
        if self.toggle_selection_callback and self.product:
            self.toggle_selection_callback(self.product.product_id, self.is_selected)

    def _open_product_url(self):
        if self.product and self.product.url:
            webbrowser.open(self.product.url)

    def update_product(self, product, border_color):
        if not product or product == self.product:
            return
        self.product = product
        self.is_selected = False
        self._set_border(border_color)
        self.setStyleSheet(f"background:white;border:2px solid {border_color}")
        self._update_image()
        self._update_labels()

