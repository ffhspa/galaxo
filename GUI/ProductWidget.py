import tkinter as tk
import webbrowser
from GUI.ImageLoader import ImageLoader
from CONFIG.Constants import Constants
from CONFIG.ProductConfig import ProductConfig
from UTILS.Utils import Utils


class ProductWidget(tk.Frame):
    def __init__(self, parent, product=None, border_color="white", toggle_selection_callback=None):
        super().__init__(parent, bg=Constants.BG_COLOR)
        self.product = None
        self.toggle_selection_callback = toggle_selection_callback
        self.is_selected = False
        self.single_click_id = None
        self.current_image_url = None
        self.product_frame = tk.Frame(self, bg="white")
        self.product_frame.pack(fill="both", expand=True, padx=3, pady=3)

        self.image_label = tk.Label(self.product_frame, bg="white")
        self.image_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.text_frame = tk.Frame(self.product_frame, bg="white")
        self.text_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5)

        for widget in [self.image_label, self.text_frame, self.product_frame]:
            Utils.bind_widget_events(widget, self._on_click, self._open_product_url)

        if product:
            self.update_product(product, border_color)

    def _on_click(self, event=None):
        if self.single_click_id is not None:
            try:
                self.after_cancel(self.single_click_id)
            except Exception:
                pass
        self.single_click_id = self.after(200, self._toggle_selection)

    def _toggle_selection(self):
        self.is_selected = not self.is_selected
        self._update_widget_bg_colors(Constants.SELECTED_COLOR if self.is_selected else "white")
        if self.toggle_selection_callback:
            self.toggle_selection_callback(self.product.product_id, self.is_selected)

    def _open_product_url(self, event=None):
        if self.single_click_id:
            try:
                self.after_cancel(self.single_click_id)
            except Exception:
                pass
        if self.product and self.product.url:
            webbrowser.open(self.product.url)

    def _update_widget_bg_colors(self, color):
        widgets = [self.product_frame, self.text_frame, self.image_label]
        for widget in widgets:
            if widget.cget("bg") != color:
                widget.config(bg=color)

        for label in self.text_frame.winfo_children():
            if label.cget("bg") != color:
                label.config(bg=color)

    def _update_image(self):
        if self.product and self.product.image_url:
            # Altes Bild durch Text ersetzen
            self.image_label.config(
                image=None,
                text="Lade Bild...",
                compound="center",  # Zentriert den Text
                fg="#888",
                font=("Arial", 15),
                bg="white"
            )
            self.image_label.image = None
            self.image_label.image_path = None

            # Neues Bild asynchron laden
            ImageLoader(self.image_label, self.product.image_url).load_image()

    def _update_labels(self):
        # Nur aktualisieren, wenn sich Text geändert hat
        new_config = ProductConfig.get_config(self.product)
        current_labels = self.text_frame.winfo_children()

        # Rebuild only if number or keys differ
        if len(current_labels) != len(new_config):
            for widget in current_labels:
                widget.destroy()
            self._create_labels(new_config)
            return

        for widget, (key, (default_text, font)) in zip(current_labels, new_config.items()):
            value = getattr(self.product, key, "")
            truncated = Utils.truncate_text(value)
            new_text = Utils.format_label_text(key, default_text, truncated)
            if widget.cget("text") != new_text:
                widget.config(text=new_text)

    def _create_labels(self, config):
        for key, (default_text, font) in config.items():
            value = getattr(self.product, key, "")
            truncated = Utils.truncate_text(value)
            text = Utils.format_label_text(key, default_text, truncated)

            label = tk.Label(
                self.text_frame,
                text=text,
                font=font,
                bg="white",
                anchor="w",
                justify="left",
                wraplength=Constants.WRAPLENGTH
            )
            label.pack(anchor="w", pady=2)
            Utils.bind_widget_events(label, self._on_click, self._open_product_url)

    def update_product(self, product, border_color):
        if not product or product == self.product:
            return
        self.product = product
        self.config(bg=border_color)
        self.is_selected = False
        self._update_image()
        self._update_widget_bg_colors("white")
        self._update_labels()
