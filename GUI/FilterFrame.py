from PyQt6.QtWidgets import (
    QGroupBox, QGridLayout, QComboBox, QCheckBox, QLabel,
    QPushButton, QLineEdit, QWidget, QHBoxLayout
)
from CONFIG.Constants import Constants
from CONFIG.Version import Version
from UTILS.Utils import Utils
from CONFIG.LogLevel import LogLevel

class FilterFrame(QGroupBox):
    def __init__(self, parent, apply_filters_callback,
                 apply_sort_callback, delete_selected_products_callback,
                 apply_filters_debounced, update_prices_callback,
                 add_favorit_callback):
        super().__init__(Version, parent)
        self.apply_filters_callback = apply_filters_callback
        self.apply_sort_callback = apply_sort_callback
        self.delete_selected_products_callback = delete_selected_products_callback
        self.apply_filters_debounced = apply_filters_debounced
        self.update_prices_callback = update_prices_callback
        self.add_favorit_callback = add_favorit_callback
        self._create_widgets()
        self.sort_combobox.setCurrentText(Constants.SORT_DEFAULT)

    def _create_widgets(self):
        layout = QGridLayout(self)

        self.sort_combobox = QComboBox()
        self.sort_combobox.addItems(Utils.get_sort_options_keys())
        self.sort_combobox.currentIndexChanged.connect(self.apply_sort_callback)
        layout.addWidget(self.sort_combobox, 0, 0)

        self.category_combobox = QComboBox()
        self.category_combobox.currentIndexChanged.connect(self.apply_filters_callback)
        layout.addWidget(self.category_combobox, 0, 1)

        self.min_price_var = QCheckBox("Min-Preis")
        self.min_price_var.stateChanged.connect(self.apply_filters_callback)
        layout.addWidget(self.min_price_var, 0, 2)

        self.only_updates = QCheckBox("Nur Änderungen")
        self.only_updates.stateChanged.connect(self.apply_filters_callback)
        self.only_updates_checkbox = self.only_updates
        layout.addWidget(self.only_updates_checkbox, 0, 3)

        self.product_count_label = QLabel("Produkte: 0")
        layout.addWidget(self.product_count_label, 0, 4)

        self.selected_product_count_label = QLabel("Markiert: 0")
        layout.addWidget(self.selected_product_count_label, 0, 5)

        self.delete_button = QPushButton("Löschen")
        self.delete_button.clicked.connect(self.delete_selected_products_callback)
        layout.addWidget(self.delete_button, 0, 6)

        self.update_button = QPushButton("Preise aktualisieren")
        self.update_button.clicked.connect(self.update_prices_callback)
        layout.addWidget(self.update_button, 0, 7)

        search_frame = QWidget()
        search_layout = QHBoxLayout(search_frame)
        self.search_label = QLabel("🔍⩔➕")
        search_layout.addWidget(self.search_label)
        self.search_entry = QLineEdit()
        self.search_entry.textChanged.connect(self.apply_filters_debounced)
        search_layout.addWidget(self.search_entry)
        self.loglevel_combobox = QComboBox()
        self.loglevel_combobox.addItems(LogLevel.get_level_names())
        self.loglevel_combobox.setCurrentText('WARNING')
        self.loglevel_combobox.currentIndexChanged.connect(self._on_loglevel_changed)
        search_layout.addWidget(self.loglevel_combobox)
        layout.addWidget(search_frame, 0, 8)

        self.status_update_label = QLabel()
        layout.addWidget(self.status_update_label, 1, 0, 1, 9)

    def _on_loglevel_changed(self, event):
        selected_level = self.loglevel_combobox.currentText().upper()
        level = getattr(LogLevel, selected_level, LogLevel.WARNING)
        Constants.set_log_level(level)
        self.update_status_label(f"Loglevel:{selected_level}", "info")

    def update_status_label(self, text, severity="info"):
        color = {"info": "green", "warning": "orange", "error": "red"}.get(severity, "green")
        self.status_update_label.setText(text)
        self.status_update_label.setStyleSheet(f"color:{color}")

    def has_updates(self, all_products):
        return any(p.stock_changed_flag or p.price_changed_flag for p in all_products)

    def _get_category_counts(self, all_products):
        from collections import Counter
        category_counts = Counter(p.category_name for p in all_products)
        display_list = [f"{cat} ({count})" for cat, count in category_counts.items()]
        value_list = list(category_counts.keys())
        return display_list, value_list

    def update_category_counts(self, all_products):
        display_list, value_list = self._get_category_counts(all_products)
        self.category_combobox.clear()
        self.category_combobox.addItem(Constants.CATEGORY_DEFAULT)
        self.category_combobox.addItems(display_list)
        self.category_mapping = dict(zip(display_list, value_list))
        self.category_combobox.setCurrentText(Constants.CATEGORY_DEFAULT)
        if self.has_updates(all_products):
            self.only_updates_checkbox.show()
        else:
            self.only_updates_checkbox.hide()

