import threading
import tkinter as tk
from tkinter import ttk
import os
import sys
from pyvirtualdisplay import Display
import atexit
from GALAXO.PROCESS.GalaxoProcess import GalaxoProcess
from GALAXO.CONFIG.Constants import Constants
from GALAXO.GUI.FilterFrame import FilterFrame
from GALAXO.GUI.ProductWidget import ProductWidget
from GALAXO.UTILS.Utils import Utils
from GALAXO.PROCESS.ProductFactory import ProductFactory

# Start a virtual X display if none is available
display = None
if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
    display = Display(visible=False, size=(1024, 768))
    display.start()
    atexit.register(display.stop)

class ProductListApp:
    def __init__(self, root):
        self.root = root
        style = ttk.Style()
        style.theme_use(Constants.THEME)
        self.root.title(Constants.TITLE)
        try:
            self.root.state('zoomed')
        except tk.TclError:
            self.root.state('normal')
        self.root.configure(bg=Constants.BG_COLOR)
        self.galaxo_process = GalaxoProcess()

        self.all_products = []
        self.filtered_products = []
        self.sort_options = Utils.get_sort_options()
        self.selected_products = set()
        self.product_widgets = []
        self.category_counts = {}
        
        self._create_widgets()
        # Load products and check logs after the main loop has started
        self.root.after_idle(self._load_products)
        self.root.after_idle(self._check_log)

    # --- GUI Setup ---

    def _create_widgets(self):
        self.filter_frame = FilterFrame(
            self.root, self.apply_filters, self._apply_sort,
            self.delete_selected_products, self._apply_filters_debounced,
            self._update_prices, self._add_favorit
        )
        self._create_canvas_frame()

    def _create_canvas_frame(self):
        self.canvas_frame = ttk.Frame(self.root, padding="1")
        self.canvas_frame.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="nsew")

        self.canvas = tk.Canvas(self.canvas_frame, bg=Constants.BG_COLOR)
        self.scroll_y = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.frame = tk.Frame(self.canvas, bg=Constants.BG_COLOR)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _on_mouse_wheel(self, event):
        if self.canvas.yview() == (0.0, 1.0): return
        delta = -1 * int(event.delta / 120) * 2 if os.name == 'nt' else -1 * int(event.delta)
        self.canvas.yview_scroll(delta, "units")

    def _run_in_thread(self, func):
        threading.Thread(target=func, daemon=True).start()

    def _update_selected_count_label(self):
        self.filter_frame.selected_product_count_label.config(
            text=f"Markiert: {len(self.selected_products)}")

    def _check_log(self):
        if Utils.contains_error():
            self.filter_frame.update_status_label("Fehlerlog einträge vorhanden!", "error")

    # --- Produktanzeige ---

    def _place_products(self):
        num_products = len(self.filtered_products)

        while len(self.product_widgets) < num_products:
            self.product_widgets.append(ProductWidget(self.frame, None, None, self._select_product))

        for widget in self.product_widgets[num_products:]:
            widget.place_forget()

        self.filter_frame.product_count_label.config(text=f"Produkte: {num_products}")

        width, height = Constants.ITEM_WIDTH, Constants.ITEM_HEIGHT
        item_w = width + Constants.PADDING_X
        item_h = height + Constants.PADDING_Y
        num_columns = Constants.NUM_COLUMNS

        frame_width = num_columns * item_w - Constants.PADDING_X
        frame_height = ((num_products + num_columns - 1) // num_columns) * item_h - Constants.PADDING_Y
        self.frame.config(width=frame_width, height=frame_height)

        for idx, product in enumerate(self.filtered_products):
            widget = self.product_widgets[idx]
            widget.update_product(product, Utils.get_border_color(product))

            col, row = idx % num_columns, idx // num_columns
            x, y = col * item_w, row * item_h
            widget.place(x=x, y=y, width=width, height=height)

        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.filter_frame.search_entry.focus_set()

    # --- Produktlogik ---

    def _select_product(self, product_id, is_selected):
        if is_selected:
            self.selected_products.add(product_id)
        else:
            self.selected_products.discard(product_id)
        self._update_selected_count_label()

    def delete_selected_products(self):
        count = len(self.selected_products)

        for product_id in self.selected_products:
            self.galaxo_process.delete_product(product_id)
            product = next((p for p in self.all_products if p.product_id == product_id), None)
            Utils.delete_image(product.image_url)

        if(len(self.filtered_products) == len(self.selected_products) and self.filter_frame.only_updates):
            self.filter_frame.only_updates.set(False)

        self.selected_products.clear()
        self._load_products()
        self.filter_frame.update_status_label(f"{count} Product gelöscht!")

    def _update_prices(self):
        self._run_in_thread(self._update_prices_thread)

    def _update_prices_thread(self):
        try:
            self.galaxo_process.process_update_prices()
            self.filter_frame.update_status_label("Update abgeschlossen")

            if(self.filter_frame.only_updates):
                self.filter_frame.only_updates.set(False)

            self._load_products()
        except Exception as e:
            self.filter_frame.update_status_label(f"Fehler beim Aktualisieren der Preise: {e}", "error")
            Constants.LOGGER.error(f"Fehler beim Aktualisieren der Preise: {e}")

    def _add_favorit(self):
        self._run_in_thread(self._add_favorit_thread)

    def _add_favorit_thread(self):
        url = self.filter_frame.search_entry.get().strip()
        self.filter_frame.search_entry.delete(0, tk.END)
        try:
            product_id = Utils.extract_product_id_from_url(url)
            if self.galaxo_process.get_product(product_id):
                self.filter_frame.update_status_label(f"Product {product_id} existiert bereits!", "warning")
            else:
                self.galaxo_process.insert_favorite_by_url(url)
                self._load_products()
                self.filter_frame.update_status_label(f"Product {int(product_id)} hinzugefügt!")
        except Exception as e:
            self.filter_frame.update_status_label(f"Fehler beim Hinzufügen des Produkts: {e}", "error")
            Constants.LOGGER.error(f"Fehler beim Hinzufügen des Produkts: {e}")
            self._check_log()

    # --- Filter & Sortierung ---

    def _apply_filters_debounced(self, event=None):
        if event.keysym in ["Left", "Right", "Up", "Down"]:
            return
        current_text = self.filter_frame.search_entry.get().strip().lower()
        if 'galaxus' in current_text or 'digitec' in current_text:
            self._add_favorit()
            return
        if hasattr(self, '_filter_debounce_id'):
            self.root.after_cancel(self._filter_debounce_id)
        self._filter_debounce_id = self.root.after_idle(self.apply_filters)

    def _apply_sort(self, event=None):
        self.filtered_products = self._apply_sort_to_list(self.filtered_products)
        self.filter_frame.sort_combobox.selection_clear()
        self.selected_products.clear()
        self._update_selected_count_label()
        self._place_products()

    def apply_filters(self, event=None):
        self.filtered_products = self._get_filtered_products()
        self.filtered_products = self._apply_sort_to_list(self.filtered_products)
        self.filter_frame.category_combobox.selection_clear()
        self.selected_products.clear()
        self._update_selected_count_label()
        self._place_products()

    def _get_filtered_products(self) -> list:
        search_text = self.filter_frame.search_entry.get().strip().lower()
        selected_category_display = self.filter_frame.category_combobox.get()
        min_price = self.filter_frame.min_price_var.get()
        only_updates = self.filter_frame.only_updates.get()
        selected_category = "" if selected_category_display == Constants.CATEGORY_DEFAULT else self.filter_frame.category_mapping.get(selected_category_display, "")
        return [
            p for p in self.all_products
            if Utils.matches_filters(p, min_price, search_text, selected_category, only_updates)
        ]

    def _apply_sort_to_list(self, products: list) -> list:
        sort_option = self.filter_frame.sort_combobox.get()
        sort_key = self.sort_options.get(sort_option)
        return sorted(products, key=sort_key) if sort_key else products

    # --- Datenladen ---

    def _load_products(self):
        try:
            raw_products = self.galaxo_process._fetch_all_products()
            self.all_products = [ProductFactory.from_source(p) for p in raw_products]
            self._on_products_loaded()
            self._check_log()
        except Exception as e:
            Constants.LOGGER.error(f"Fehler beim Laden der Produkte: {e}")

    def _on_products_loaded(self):
        self.filter_frame.update_category_counts(self.all_products)
        self.apply_filters()
        self._update_selected_count_label()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductListApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.galaxo_process.close(), root.destroy()))
    root.mainloop()
