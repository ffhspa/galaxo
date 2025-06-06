import tkinter as tk
from tkinter import ttk
from typing import Counter
from CONFIG.Constants import Constants
from CONFIG.Version import Version
from UTILS.Utils import Utils
from CONFIG.LogLevel import LogLevel

class FilterFrame(ttk.LabelFrame):
    def __init__(self, parent, apply_filters_callback, apply_sort_callback, delete_selected_products_callback, apply_filters_debounced, update_prices_callback, add_favorit_callback):
        super().__init__(parent, padding="5", text=Version)
        self.parent = parent
        self.columnconfigure(20, weight=1)  # Hauptlayout-Spalte
        self.columnconfigure(100, weight=1)  # Dynamische rechte Spalte
        self.apply_filters_callback = apply_filters_callback
        self.apply_sort_callback = apply_sort_callback
        self.apply_filters_debounced = apply_filters_debounced
        self.delete_selected_products_callback = delete_selected_products_callback
        self.update_prices_callback = update_prices_callback
        self.add_favorit_callback = add_favorit_callback
        self._create_widgets()
        self.sort_combobox.set(Constants.SORT_DEFAULT)
        self.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="nwe")

    def _create_widgets(self):
        # Sortierung Combobox in Spalte 0
        self.sort_combobox = self._create_combobox(0, "Sortierung")
        self.sort_combobox["values"] = Utils.get_sort_options_keys()
        self.sort_combobox.bind("<<ComboboxSelected>>", self.apply_sort_callback)

        # Kategorie Combobox in Spalte 1
        self.category_combobox = self._create_combobox(1, "Kategorien")
        self.category_combobox.bind("<<ComboboxSelected>>", self.apply_filters_callback)

        # Nur Min-Preis Checkbox in Spalte 2
        self.min_price_var = tk.BooleanVar(value=False)
        self._create_checkbox("Min-Preis", self.min_price_var, self.apply_filters_callback, 0, 2)
        
        # Nur Aktuelle Checkbox in Spalte 3
        self.only_updates = tk.BooleanVar(value=False)
        self.only_updates_checkbox = self._create_checkbox("Aktuelle", self.only_updates, self.apply_filters_callback, 0, 3)

        # Produktanzahl und ausgewählte Produkte in Spalten 3 und 4
        self.product_count_label = self._create_label("Produkte: 0", 0, 4, bold=True)
        self.selected_product_count_label = self._create_label("Markiert: 0", 0, 5, bold=True)

        # Löschen-Button in Spalte 5
        self.delete_button = ttk.Button(self, text="Löschen", command=self.delete_selected_products_callback)
        self.delete_button.grid(row=0, column=6, padx=5, pady=5, sticky="w")
                
        self.update_button = ttk.Button(self, text="Preise aktualisieren", command=self.update_prices_callback)
        self.update_button.grid(row=0, column=7, padx=5, pady=5, sticky="w")
        
        self.status_update_label = self._create_label("", 0, 8, colspan=1, sticky="w",font=Constants.FONT_SIZE_VERY_SMALL)
        
        # Suchfeld-Frame mit Suchlabel zusammenfügen
        search_frame = ttk.Frame(self)
        search_frame.grid(row=0, column=100, padx=5, pady=5, sticky="e")

        self.search_label = ttk.Label(search_frame, text="🔍⩔➕", font=Utils.create_font(Constants.FONT_SIZE_MEDIUM))
        self.search_label.pack(side="left", padx=(0, 5))

        self.search_entry = tk.Entry(search_frame, width=30, font=Utils.create_font(Constants.FONT_SIZE_SMALL), insertontime=0, insertofftime=0)
        self.search_entry.pack(side="left", fill="x")
        self.search_entry.bind("<KeyRelease>", self.apply_filters_debounced)
        
        
                # Loglevel-Dropdown ganz rechts neben dem Suchfeld
        self.loglevel_combobox = ttk.Combobox(search_frame, width=10, state='readonly', font=Utils.create_font(Constants.FONT_SIZE_SMALL))
        self.loglevel_combobox['values'] = LogLevel.get_level_names()
        self.loglevel_combobox.set('WARNING')
        self.loglevel_combobox.pack(side="left", padx=(10, 0))
        self.loglevel_combobox.bind("<<ComboboxSelected>>", self._on_loglevel_changed)


    def _on_loglevel_changed(self, event):
        from CONFIG.LogLevel import LogLevel

        selected_level = self.loglevel_combobox.get().upper()
        level = getattr(LogLevel, selected_level, LogLevel.WARNING)
        Constants.set_log_level(level)
        #self.focus_set()
        #self.search_entry.focus_set()
            # Fokus komplett entfernen
        self.parent.focus_set()
        self.loglevel_combobox.selection_clear()
        Constants.LOGGER.info(f"Loglevel:{selected_level}")
        self.update_status_label(f"Loglevel:{selected_level}", severity="info")




    def update_status_label(self, text, severity="info"):
        Constants.LOGGER.info(f"update_status_label {severity}: {text}")
        self.status_update_label.config(text=text, foreground={'info': 'green', 'warning': 'orange', 'error': 'red'}.get(severity, 'green'))
        self.status_update_label.after(5000, lambda: self.status_update_label.config(text=""))

    def has_updates(self, all_products):
        return any(
            product.stock_changed_flag or product.price_changed_flag
            for product in all_products
        )        

    def _get_category_counts(self, all_products):
        category_counts = Counter(product.category_name for product in all_products)
        display_list = [f"{cat} ({count})" for cat, count in category_counts.items()]
        value_list = list(category_counts.keys())
        return display_list, value_list
        
    def update_category_counts(self, all_products):
        display_list, value_list = self._get_category_counts(all_products)
        
        self.category_combobox['values'] = [Constants.CATEGORY_DEFAULT] + display_list
        self.category_mapping = dict(zip(display_list, value_list))
        self.category_combobox.set(Constants.CATEGORY_DEFAULT)

        if self.has_updates(all_products):
            self.only_updates_checkbox.grid()
        else:
            self.only_updates_checkbox.grid_remove()        

    def _create_label(self, text, row, col, bold=False, colspan=1, sticky="w", font=Constants.FONT_SIZE_MEDIUM):
        font = Utils.create_font(font, "bold" if bold else "normal")
        label = ttk.Label(self, text=text, anchor="w", font=font)
        label.grid(row=row, column=col, padx=5, pady=5, sticky=sticky, columnspan=colspan)
        return label

    def _create_combobox(self, column, placeholder):
        combobox = ttk.Combobox(self, font=Utils.create_font(Constants.FONT_SIZE_MEDIUM), width=15, state='readonly')
        combobox.grid(row=0, column=column, padx=5, pady=5, sticky="we")
        combobox.insert(0, placeholder)
        return combobox

    def _create_checkbox(self, text, variable, command, row, col):
        style = ttk.Style()
        style.configure("Custom.TCheckbutton", font=Utils.create_font(Constants.FONT_SIZE_MEDIUM))
        
        checkbox = ttk.Checkbutton(self, text=text, variable=variable, command=command, style="Custom.TCheckbutton")
        checkbox.grid(row=row, column=col, padx=5, pady=5, sticky="w")
        return checkbox
