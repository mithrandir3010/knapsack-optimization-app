import customtkinter as ctk
from tkinter import messagebox
import queue
import threading

from data import load_items
from algorithm import solve_bounded_knapsack


class KnapsackGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Market Alışveriş Optimizasyonu")
        self.root.geometry("1000x720")
        self.root.resizable(True, True)

        self.products = []
        self.product_rows = []
        self.product_state = {}
        self.log_buffer = []
        self.log_window = None
        self.log_text = None
        self.action_buttons = []
        self.worker_messages = queue.Queue()
        self.calculation_running = False

        self.colors = {
            "bg": "#090E1A",
            "surface": "#111827",
            "surface_alt": "#1A2235",
            "primary": "#22C55E",
            "primary_hover": "#16A34A",
            "warning": "#F59E0B",
            "warning_hover": "#D97706",
            "danger": "#EF4444",
            "danger_hover": "#DC2626",
            "text": "#F8FAFC",
            "muted": "#94A3B8",
            "entry_bg": "#0F172A",
        }

        self.create_widgets()
        self.load_products()
        self.reset_filter()

    def create_widgets(self):
        title = ctk.CTkLabel(
            self.root,
            text="Market Alışveriş Optimizasyonu",
            font=("Helvetica Neue", 30, "bold"),
            text_color=self.colors["text"],
        )
        title.pack(pady=(20, 12))

        top_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["surface"],
            corner_radius=16,
            border_width=1,
            border_color="#233046",
        )
        top_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            top_frame,
            text="Bütçe:",
            font=("Helvetica Neue", 16, "bold"),
            text_color=self.colors["text"],
        ).pack(side="left", padx=(16, 8), pady=14)

        self.budget_entry = ctk.CTkEntry(
            top_frame,
            font=("Helvetica Neue", 14),
            width=140,
            corner_radius=10,
            fg_color=self.colors["entry_bg"],
            border_color="#334155",
            text_color=self.colors["text"],
        )
        self.budget_entry.pack(side="left", padx=10)

        calculate_button = ctk.CTkButton(
            top_frame,
            text="Hesapla",
            command=self.calculate,
            fg_color=self.colors["warning"],
            hover_color=self.colors["warning_hover"],
            text_color="white",
            font=("Helvetica Neue", 13, "bold"),
            corner_radius=12,
            height=38,
        )
        calculate_button.pack(side="left", padx=10)
        self.action_buttons.append(calculate_button)

        clear_button = ctk.CTkButton(
            top_frame,
            text="Temizle",
            command=self.clear_all,
            fg_color=self.colors["danger"],
            hover_color=self.colors["danger_hover"],
            text_color="white",
            font=("Helvetica Neue", 13, "bold"),
            corner_radius=12,
            height=38,
        )
        clear_button.pack(side="left", padx=10, pady=14)
        self.action_buttons.append(clear_button)

        log_button = ctk.CTkButton(
            top_frame,
            text="Süreç Detayları",
            command=self.open_log_window,
            fg_color="#334155",
            hover_color="#1E293B",
            text_color="white",
            font=("Helvetica Neue", 13, "bold"),
            corner_radius=12,
            height=38,
        )
        log_button.pack(side="left", padx=10)
        self.action_buttons.append(log_button)

        table_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["surface"],
            corner_radius=16,
            border_width=1,
            border_color="#233046",
        )
        table_frame.pack(padx=20, pady=(10, 16), fill="both", expand=True)

        search_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=14, pady=(14, 2))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Ürün ara (örn: muz)",
            font=("Helvetica Neue", 13),
            width=280,
            fg_color=self.colors["entry_bg"],
            border_color="#334155",
            text_color=self.colors["text"],
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda _event: self.filter_products())

        search_button = ctk.CTkButton(
            search_frame,
            text="Ara",
            command=self.filter_products,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color="white",
            font=("Helvetica Neue", 13, "bold"),
            corner_radius=12,
            height=36,
            width=90,
        )
        search_button.pack(side="left", padx=(0, 8))
        self.action_buttons.append(search_button)

        reset_button = ctk.CTkButton(
            search_frame,
            text="Tümünü Göster",
            command=self.reset_filter,
            fg_color="#334155",
            hover_color="#1E293B",
            text_color="white",
            font=("Helvetica Neue", 13, "bold"),
            corner_radius=12,
            height=36,
        )
        reset_button.pack(side="left")
        self.action_buttons.append(reset_button)

        content_split = ctk.CTkFrame(table_frame, fg_color="transparent")
        content_split.pack(fill="both", expand=True, padx=14, pady=(8, 14))

        products_panel = ctk.CTkFrame(content_split, fg_color="transparent")
        products_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        cart_panel = ctk.CTkFrame(
            content_split,
            fg_color=self.colors["surface_alt"],
            corner_radius=12,
            border_width=1,
            border_color="#233046",
            width=260,
        )
        cart_panel.pack(side="right", fill="y")
        cart_panel.pack_propagate(False)

        header = ctk.CTkFrame(products_panel, fg_color=self.colors["surface_alt"], corner_radius=12)
        header.pack(fill="x", pady=(0, 10))

        self.column_widths = {
            "select": 70,
            "name": 280,
            "price": 120,
            "quantity": 200,
            "importance": 220,
        }

        headers = [
            ("Seç", "select"),
            ("Ürün Adı", "name"),
            ("Fiyat", "price"),
            ("Alınmak İstenen Adet", "quantity"),
            ("Önem Derecesi (1-10)", "importance")
        ]

        for index, (text, key) in enumerate(headers):
            anchor_type = "w" if key == "name" else "center"

            ctk.CTkLabel(
                header,
                text=text,
                width=self.column_widths[key] // 8,
                anchor=anchor_type,
                font=("Helvetica Neue", 13, "bold"),
                text_color=self.colors["text"],
            ).grid(row=0, column=index, padx=8, pady=10, sticky="ew")

        self.products_frame = ctk.CTkScrollableFrame(
            products_panel,
            fg_color=self.colors["surface"],
            corner_radius=12,
        )
        self.products_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            cart_panel,
            text="Sepetim",
            font=("Helvetica Neue", 16, "bold"),
            text_color=self.colors["text"],
        ).pack(anchor="w", padx=12, pady=(12, 8))

        self.cart_items_text = ctk.CTkTextbox(
            cart_panel,
            font=("Helvetica Neue", 12),
            fg_color=self.colors["entry_bg"],
            text_color=self.colors["text"],
            wrap="word",
            corner_radius=10,
            height=340,
        )
        self.cart_items_text.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.cart_items_text.configure(state="disabled")

        self.cart_total_label = ctk.CTkLabel(
            cart_panel,
            text="Sepet Tutarı: 0 TL",
            font=("Helvetica Neue", 14, "bold"),
            text_color=self.colors["primary"],
        )
        self.cart_total_label.pack(anchor="w", padx=12, pady=(0, 12))

        self.info_label = ctk.CTkLabel(
            self.root,
            text="Market ürünlerini seçip bütçe girerek en uygun sepeti hesaplayabilirsiniz.",
            font=("Helvetica Neue", 12),
            text_color=self.colors["muted"],
        )
        self.info_label.pack(pady=(0, 14))

    def load_products(self):
        self.set_busy_state(True)
        try:
            try:
                self.products = load_items("items.csv")
            except Exception as e:
                messagebox.showerror("Hata", f"Ürünler yüklenemedi:\n{e}")
                return

            self._initialize_product_state()
            self.reset_filter()
            self.info_label.configure(text=f"{len(self.products)} ürün hazır ve listelendi.")
        finally:
            self.set_busy_state(False)

    def _initialize_product_state(self):
        self.product_state = {}

        for product in self.products:
            self.product_state[product["name"]] = {
                "name": product["name"],
                "price": product["price"],
                "selected": 0,
                "quantity": 1,
                "importance": int(product.get("importance", 5)),
                "default_importance": int(product.get("importance", 5)),
            }

        self.refresh_cart_panel()

    def _sync_visible_rows_to_state(self):
        for row in self.product_rows:
            state = self.product_state.get(row["name"])
            if not state:
                continue

            state["selected"] = row["selected"].get()

            try:
                quantity = int(row["quantity_input"].get())
                if quantity > 0:
                    state["quantity"] = quantity
            except ValueError:
                pass

            try:
                importance = int(row["importance_input"].get())
                if 1 <= importance <= 10:
                    state["importance"] = importance
            except ValueError:
                pass

        self.refresh_cart_panel()

    def render_products(self, products_to_render):
        for widget in self.products_frame.winfo_children():
            widget.destroy()

        self.product_rows.clear()

        for product in products_to_render:
            state = self.product_state.get(product["name"], {})
            row = ctk.CTkFrame(
                self.products_frame,
                fg_color=self.colors["surface_alt"],
                corner_radius=10,
            )
            row.pack(fill="x", pady=5, padx=2)

            selected_var = ctk.IntVar(value=int(state.get("selected", 0)))

            check = ctk.CTkCheckBox(
                row,
                variable=selected_var,
                onvalue=1,
                offvalue=0,
                text="",
                width=28,
                fg_color=self.colors["primary"],
                hover_color=self.colors["primary_hover"],
                command=lambda item_name=product["name"], var=selected_var: self._update_selected_state(item_name, var),
            )
            check.grid(row=0, column=0, padx=(16, 10), pady=10)

            ctk.CTkLabel(
                row,
                text=product["name"],
                width=self.column_widths["name"] // 8,
                anchor="w",
                font=("Helvetica Neue", 13),
                text_color=self.colors["text"],
            ).grid(row=0, column=1, padx=6, sticky="w")

            ctk.CTkLabel(
                row,
                text=f"{product['price']} TL",
                width=self.column_widths["price"] // 8,
                anchor="center",
                font=("Helvetica Neue", 13),
                text_color=self.colors["text"],
            ).grid(row=0, column=2, padx=6)

            quantity_input = ctk.CTkEntry(
                row,
                width=80,
                font=("Helvetica Neue", 13),
                justify="center",
                fg_color=self.colors["entry_bg"],
                border_color="#334155",
                text_color=self.colors["text"],
            )
            quantity_input.insert(0, str(state.get("quantity", 1)))
            quantity_input.grid(row=0, column=3, padx=20)
            quantity_input.bind(
                "<FocusOut>",
                lambda _event, item_name=product["name"], widget=quantity_input: self._update_quantity_state(item_name, widget),
            )

            importance_entry = ctk.CTkEntry(
                row,
                width=80,
                font=("Helvetica Neue", 13),
                justify="center",
                fg_color=self.colors["entry_bg"],
                border_color="#334155",
                text_color=self.colors["text"],
            )
            importance_entry.insert(0, str(state.get("importance", product.get("importance", 5))))
            importance_entry.grid(row=0, column=4, padx=(20, 16))
            importance_entry.bind(
                "<FocusOut>",
                lambda _event, item_name=product["name"], widget=importance_entry: self._update_importance_state(item_name, widget),
            )

            self.product_rows.append({
                "selected": selected_var,
                "name": product["name"],
                "price": product["price"],
                "quantity_input": quantity_input,
                "importance_input": importance_entry
            })

        self.scroll_products_to_top()

    def scroll_products_to_top(self):
        try:
            # Keep filtered results visible from the first row.
            self.products_frame._parent_canvas.yview_moveto(0)
        except Exception:
            pass

    def _update_selected_state(self, item_name, selected_var):
        if item_name in self.product_state:
            self.product_state[item_name]["selected"] = selected_var.get()
            self.refresh_cart_panel()

    def _update_quantity_state(self, item_name, quantity_widget):
        if item_name not in self.product_state:
            return

        try:
            quantity = int(quantity_widget.get())
            if quantity > 0:
                self.product_state[item_name]["quantity"] = quantity
                self.refresh_cart_panel()
        except ValueError:
            pass

    def _update_importance_state(self, item_name, importance_widget):
        if item_name not in self.product_state:
            return

        try:
            importance = int(importance_widget.get())
            if 1 <= importance <= 10:
                self.product_state[item_name]["importance"] = importance
        except ValueError:
            pass

    def refresh_cart_panel(self):
        selected_items = [item for item in self.product_state.values() if item["selected"] == 1]

        self.cart_items_text.configure(state="normal")
        self.cart_items_text.delete("1.0", "end")

        if not selected_items:
            self.cart_items_text.insert("end", "Henüz ürün seçilmedi.")
            total_cost = 0
        else:
            for item in selected_items:
                self.cart_items_text.insert("end", f"• {item['name']}\n")
            total_cost = sum(item["price"] * item["quantity"] for item in selected_items)

        self.cart_items_text.configure(state="disabled")
        self.cart_total_label.configure(text=f"Sepet Tutarı: {total_cost} TL")

    def filter_products(self):
        self._sync_visible_rows_to_state()
        query = self.search_entry.get().strip().casefold()

        if not query:
            self.render_products(self.products)
            self.info_label.configure(text=f"{len(self.products)} ürün gösteriliyor.")
            return

        filtered = [item for item in self.products if query in item["name"].casefold()]
        self.render_products(filtered)

        if filtered:
            self.info_label.configure(text=f"Arama sonucu: {len(filtered)} ürün bulundu.")
        else:
            self.info_label.configure(text="Arama sonucu bulunamadı.")

    def reset_filter(self):
        self._sync_visible_rows_to_state()
        self.search_entry.delete(0, "end")
        self.render_products(self.products)
        self.info_label.configure(text=f"{len(self.products)} ürün gösteriliyor.")

    def calculate(self):
        if self.calculation_running:
            return

        try:
            budget = int(float(self.budget_entry.get()))
            if budget <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir bütçe giriniz.")
            return

        self._sync_visible_rows_to_state()
        selected_products = []

        for product in self.product_state.values():
            if product["selected"] == 1:
                quantity = product["quantity"]
                importance = product["importance"]

                if quantity <= 0 or importance < 1 or importance > 10:
                    messagebox.showerror(
                        "Hata",
                        "Adet geçerli olmalı, önem puanı 1-10 arasında olmalıdır."
                    )
                    return

                selected_products.append({
                    "name": product["name"],
                    "price": product["price"],
                    "quantity": quantity,
                    "importance": importance,
                })

        if not selected_products:
            messagebox.showerror("Hata", "En az bir ürün seçmelisiniz.")
            return

        self.clear_logs()
        self.log_message("Algoritma başlatıldı...")
        self.set_busy_state(True)
        self.calculation_running = True

        worker = threading.Thread(
            target=self._run_knapsack_worker,
            args=(selected_products, budget),
            daemon=True,
        )
        worker.start()
        self.root.after(20, self._poll_worker_messages)

    def _run_knapsack_worker(self, selected_products, budget):
        try:
            result = solve_bounded_knapsack(
                selected_products,
                budget,
                log_callback=lambda message: self.worker_messages.put(("log", message)),
                log_delay=0.0,
            )
            excluded_items = self.build_excluded_items(selected_products, result["selected_items"])
            self.worker_messages.put(("done", (result, budget, excluded_items)))
        except Exception as exc:
            self.worker_messages.put(("error", str(exc)))

    def _poll_worker_messages(self):
        done = False

        while True:
            try:
                message_type, payload = self.worker_messages.get_nowait()
            except queue.Empty:
                break

            if message_type == "log":
                self.log_message(payload)
            elif message_type == "done":
                result, budget, excluded_items = payload
                self.show_result_popup(result, budget, excluded_items)
                done = True
            elif message_type == "error":
                messagebox.showerror("Hata", f"Hesaplama sırasında hata oluştu:\n{payload}")
                done = True

        if done:
            self.calculation_running = False
            self.set_busy_state(False)
            return

        self.root.after(20, self._poll_worker_messages)

    def build_excluded_items(self, selected_products, optimized_items):
        selected_map = {item["name"]: item["quantity"] for item in selected_products}
        optimized_map = {item["name"]: item["quantity"] for item in optimized_items}

        excluded = []
        for item in selected_products:
            name = item["name"]
            excluded_quantity = selected_map.get(name, 0) - optimized_map.get(name, 0)

            if excluded_quantity > 0:
                excluded.append({
                    "name": name,
                    "quantity": excluded_quantity,
                })

        return excluded

    def show_result_popup(self, result, budget, excluded_items):
        popup = ctk.CTkToplevel(self.root)
        popup.title("En Uygun Market Sepeti")
        popup.geometry("860x620")
        popup.minsize(760, 520)
        popup.resizable(True, True)
        popup.transient(self.root)
        popup.grab_set()

        ctk.CTkLabel(
            popup,
            text="En Uygun Sepet Sonucu",
            font=("Helvetica Neue", 22, "bold"),
            text_color=self.colors["primary"],
        ).pack(pady=15)

        content_frame = ctk.CTkFrame(popup, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        text = ctk.CTkTextbox(
            content_frame,
            height=380,
            font=("Helvetica Neue", 12),
            fg_color=self.colors["entry_bg"],
            text_color=self.colors["text"],
            wrap="word",
            corner_radius=12,
        )
        text.pack(fill="both", expand=True)

        if not result["selected_items"]:
            text.insert("end", "Bütçeye uygun market ürünü bulunamadı.")
        else:
            text.insert("end", "EN UYGUN SEPET BULUNDU\n")
            text.insert("end", "=" * 50 + "\n\n")

            for item in result["selected_items"]:
                total = item["price"] * item["quantity"]
                text.insert(
                    "end",
                    f"{item['name']} | Adet: {item['quantity']} | "
                    f"Birim Fiyat: {item['price']} TL | "
                    f"Toplam: {total} TL | "
                    f"Önem: {item['importance']}\n"
                )

            text.insert("end", "\n" + "-" * 50 + "\n")
            text.insert("end", f"Bütçe: {budget} TL\n")
            text.insert("end", f"Toplam Maliyet: {result['total_cost']} TL\n")
            text.insert("end", f"Kalan Bütçe: {result['remaining_budget']} TL\n")
            text.insert("end", f"Toplam Önem Puanı: {result['total_importance']}\n")

            text.insert("end", "\n" + "-" * 50 + "\n")
            text.insert("end", "SEÇİM DIŞI KALAN ÜRÜNLER\n")

            if excluded_items:
                for item in excluded_items:
                    text.insert("end", f"- {item['name']} | Dışarıda Kalan Adet: {item['quantity']}\n")
            else:
                text.insert("end", "- Tüm seçili ürünler optimum çözümde kullanıldı.\n")

        text.configure(state="disabled")

        ctk.CTkButton(
            popup,
            text="Kapat",
            command=popup.destroy,
            fg_color="#334155",
            hover_color="#1E293B",
            text_color="white",
            font=("Helvetica Neue", 13, "bold"),
            corner_radius=12,
            height=36,
        ).pack(pady=(0, 14))

    def clear_all(self):
        self.budget_entry.delete(0, "end")
        self.search_entry.delete(0, "end")

        for item_name, state in self.product_state.items():
            state["selected"] = 0
            state["quantity"] = 1
            state["importance"] = state.get("default_importance", 5)

        self.render_products(self.products)
        self.refresh_cart_panel()
        self.info_label.config(text="Seçimler temizlendi.")
        self.clear_logs()

    def clear_logs(self):
        self.log_buffer.clear()

        if self.log_text is not None and self.log_text.winfo_exists():
            self.log_text.configure(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.configure(state="disabled")

    def log_message(self, message):
        self.log_buffer.append(message)

        if self.log_text is not None and self.log_text.winfo_exists():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", f"{message}\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")

        self.root.update_idletasks()

    def open_log_window(self):
        if self.log_window is not None and self.log_window.winfo_exists():
            self.log_window.lift()
            self.log_window.focus()
            return

        self.log_window = ctk.CTkToplevel(self.root)
        self.log_window.title("Algoritma Süreç Detayları")
        self.log_window.geometry("860x520")
        self.log_window.minsize(700, 420)

        ctk.CTkLabel(
            self.log_window,
            text="Algoritma Süreç Detayları",
            font=("Helvetica Neue", 20, "bold"),
            text_color=self.colors["primary"],
        ).pack(pady=(14, 10))

        self.log_text = ctk.CTkTextbox(
            self.log_window,
            font=("Helvetica Neue", 12),
            fg_color=self.colors["entry_bg"],
            text_color=self.colors["text"],
            wrap="word",
            corner_radius=12,
        )
        self.log_text.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.log_text.configure(state="normal")
        self.log_text.insert("end", "\n".join(self.log_buffer) + ("\n" if self.log_buffer else ""))
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def set_busy_state(self, is_busy):
        # Keep default cursor to avoid flashy system wait cursor.
        cursor_name = ""
        try:
            self.root.configure(cursor=cursor_name)
        except Exception:
            pass

        state_value = "disabled" if is_busy else "normal"
        for button in self.action_buttons:
            button.configure(state=state_value)

        self.root.update_idletasks()


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.configure(fg_color="#090E1A")
    app = KnapsackGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()