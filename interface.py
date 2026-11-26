import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import operations as db


# Theme Colors
BG_CREAM = "#F5F0E8"
BG_PANEL = "#EFE7DA"
HEADER_GREEN = "#ACE2B0"
DARK_GREEN = "#1B4332"
BROWN_PRIMARY = "#4B3025"
BROWN_ACCENT = "#8B5E3C"
NAV_BG = "#2D3A3A"
NAV_ACTIVE = "#4B3025"
MAX_CONTENT_WIDTH = 1120


class SafeLabel(ttk.Label):

    def __init__(self, parent, text="", bg=BG_PANEL, fg="black", font=("Arial", 10), justify="left", **kwargs):
        anchor_map = {"left": "w", "center": "center", "right": "e"}
        anchor = kwargs.pop("anchor", anchor_map.get(justify, "w"))
        super().__init__(
            parent,
            text=str(text),
            background=bg,
            foreground=fg,
            font=font,
            justify=justify,
            anchor=anchor,
            **kwargs,
        )

    def set_text(self, text):
        super().configure(text=str(text))

    def config(self, cnf=None, **kw):
        if "bg" in kw:
            kw["background"] = kw.pop("bg")
        if "fg" in kw:
            kw["foreground"] = kw.pop("fg")
        if "justify" in kw and "anchor" not in kw:
            anchor_map = {"left": "w", "center": "center", "right": "e"}
            kw["anchor"] = anchor_map.get(kw["justify"], "w")
        if cnf is not None:
            return super().configure(cnf, **kw)
        return super().configure(**kw)

    configure = config


class BookstoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Girard's Bookstore Management System")
        self.root.geometry("1120x740")
        self.root.minsize(1000, 660)
        self.root.configure(bg=BG_CREAM)

        # Session state
        self.current_buyer = None   # dict when logged in as Buyer
        self.current_store = None   # dict when logged in as Store Partner
        self.active_page_key = None
        self._last_extra_x = None

        self._configure_styles()
        self._build_header_and_nav()

        # Container holding stacked page frames
        self.content_container = tk.Frame(self.root, bg=BG_CREAM)
        self.content_container.pack(fill="both", expand=True, padx=16, pady=12)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Keep full-screen layout centered at the small window's proportions
        self.root.bind("<Configure>", self._on_root_resize)

        self.pages = {}
        self._build_login_page()
        self._build_search_page()
        self._build_cart_page()
        self._build_checkout_page()
        self._build_admin_reports_page()

        # Start on Page 1: Login
        self.show_page("login")

    def _on_root_resize(self, event):
        if event.widget is not self.root:
            return
        extra_x = max(0, (event.width - MAX_CONTENT_WIDTH) // 2)
        if extra_x == self._last_extra_x:
            return
        self._last_extra_x = extra_x
        self.header_inner.pack_configure(padx=extra_x)
        self.nav_inner.pack_configure(padx=extra_x)
        self.content_container.pack_configure(padx=extra_x + 16)

    def _make_checkbox(self, parent, text, variable, bg=BG_PANEL, fg="black", font=("Arial", 10), command=None):
        """Build a Checkbutton paired with a SafeLabel"""
        holder = tk.Frame(parent, bg=bg)
        cb = ttk.Checkbutton(
            holder,
            variable=variable,
            style="Panel.TCheckbutton" if bg == BG_PANEL else "Cream.TCheckbutton",
            command=command,
        )
        cb.pack(side="left")
        lbl = SafeLabel(holder, text=text, bg=bg, fg=fg, font=font, cursor="hand2")
        lbl.pack(side="left")

        def toggle(_event):
            variable.set(not variable.get())
            if command:
                command()

        lbl.bind("<Button-1>", toggle)
        return holder

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # LabelFrames
        style.configure("Panel.TLabelframe", background=BG_PANEL, bordercolor="#C8BFA8", relief="groove")
        style.configure("Panel.TLabelframe.Label", background=BG_PANEL, foreground=BROWN_PRIMARY, font=("Arial", 11, "bold"))

        style.configure("PanelGreen.TLabelframe", background=BG_PANEL, bordercolor="#C8BFA8", relief="groove")
        style.configure("PanelGreen.TLabelframe.Label", background=BG_PANEL, foreground=DARK_GREEN, font=("Arial", 11, "bold"))

        style.configure("PanelAccent.TLabelframe", background=BG_PANEL, bordercolor="#C8BFA8", relief="groove")
        style.configure("PanelAccent.TLabelframe.Label", background=BG_PANEL, foreground=BROWN_ACCENT, font=("Arial", 11, "bold"))

        style.configure("PanelBlack.TLabelframe", background=BG_PANEL, bordercolor="#C8BFA8", relief="groove")
        style.configure("PanelBlack.TLabelframe.Label", background=BG_PANEL, foreground="black", font=("Arial", 10, "bold"))

        style.configure("Cream.TLabelframe", background=BG_CREAM, bordercolor="#C8BFA8", relief="groove")
        style.configure("Cream.TLabelframe.Label", background=BG_CREAM, foreground="black", font=("Arial", 10, "bold"))

        # Checkbuttons
        style.configure("Panel.TCheckbutton", background=BG_PANEL, foreground="black")
        style.map("Panel.TCheckbutton", background=[("active", BG_PANEL)])

        style.configure("Cream.TCheckbutton", background=BG_CREAM, foreground="black")
        style.map("Cream.TCheckbutton", background=[("active", BG_CREAM)])

        # Entry, Treeview & Combobox
        style.configure(
            "TEntry",
            fieldbackground="white",
            foreground="black",
            insertcolor="black",
            padding=(4, 3),
        )
        style.configure(
            "Treeview",
            rowheight=26,
            font=("Arial", 10),
            background="white",
            fieldbackground="white",
            foreground="black",
        )
        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold"),
            background="#D8CFC0",
            foreground="black",
        )
        style.configure(
            "TCombobox",
            fieldbackground="white",
            background="#D8CFC0",
            foreground="black",
        )

    def _build_header_and_nav(self):
        # Top Brand Banner
        header = tk.Frame(self.root, bg=HEADER_GREEN)
        header.pack(fill="x")

        self.header_inner = tk.Frame(header, bg=HEADER_GREEN)
        self.header_inner.pack(fill="x")

        SafeLabel(
            self.header_inner,
            text="GIRARD'S BOOKSTORE",
            font=("Georgia", 22, "bold"),
            fg=DARK_GREEN,
            bg=HEADER_GREEN,
        ).pack(side="left", padx=20, pady=12)

        right_status = tk.Frame(self.header_inner, bg=HEADER_GREEN)
        right_status.pack(side="right", padx=20, pady=10)

        connected, status_msg = db.test_connection()
        SafeLabel(
            right_status,
            text=status_msg,
            font=("Arial", 9, "bold"),
            fg=DARK_GREEN if connected else "#9B1C1C",
            bg=HEADER_GREEN,
            justify="right",
        ).pack(anchor="e")

        self.session_label = SafeLabel(
            right_status,
            text="Not logged in (Guest)",
            font=("Arial", 10, "bold"),
            fg="#1F2937",
            bg=HEADER_GREEN,
            justify="right",
        )
        self.session_label.pack(anchor="e", pady=(2, 0))

        # Navigation Bar
        nav_bar = tk.Frame(self.root, bg=NAV_BG)
        nav_bar.pack(fill="x")

        self.nav_inner = tk.Frame(nav_bar, bg=NAV_BG)
        self.nav_inner.pack(fill="x")

        self.nav_buttons = {}
        nav_items = [
            ("login", "1. Login"),
            ("search", "2. Search & Books"),
            ("cart", "3. Cart"),
            ("checkout", "4. Checkout"),
            ("admin", "5. Orders, Store Admin & Reports"),
        ]

        for key, label in nav_items:
            btn = tk.Button(
                self.nav_inner,
                text=label,
                command=lambda k=key: self.show_page(k),
                bg=NAV_BG,
                fg="white",
                activebackground=NAV_ACTIVE,
                activeforeground="white",
                relief="flat",
                font=("Arial", 10, "bold"),
                padx=16,
                pady=8,
                cursor="hand2",
            )
            btn.pack(side="left")
            self.nav_buttons[key] = btn

        tk.Button(
            self.nav_inner,
            text="Quit",
            command=self.root.destroy,
            bg="#7F1D1D",
            fg="white",
            activebackground="#991B1B",
            activeforeground="white",
            relief="flat",
            font=("Arial", 10, "bold"),
            padx=14,
            pady=8,
            cursor="hand2",
        ).pack(side="right")

    def update_session_banner(self):
        if self.current_buyer:
            self.session_label.config(
                text=f"Logged in: {self.current_buyer['BuyerName']} (Buyer #{self.current_buyer['BuyerID']})"
            )
        elif self.current_store:
            self.session_label.config(
                text=f"Logged in: {self.current_store['StoreName']} (Store #{self.current_store['StoreID']})"
            )
        else:
            self.session_label.config(text="Not logged in (Guest)")

    def show_page(self, key):
        self.active_page_key = key
        for k, btn in self.nav_buttons.items():
            btn.config(bg=NAV_ACTIVE if k == key else NAV_BG)

        # Refresh data for the target page before displaying
        if key == "login":
            self.refresh_sample_accounts()
        elif key == "search":
            self.refresh_filter_dropdowns()
            self.run_book_search()
        elif key == "cart":
            self.refresh_cart_page()
        elif key == "checkout":
            self.refresh_checkout_page()
        elif key == "admin":
            self.refresh_admin_reports_page()

        self.pages[key].tkraise()

    # ========================================================================
    # PAGE 1: LOGIN & NEW BUYER REGISTRATION
    # ========================================================================
    def _build_login_page(self):
        page = tk.Frame(self.content_container, bg=BG_CREAM)
        page.grid(row=0, column=0, sticky="nsew")
        self.pages["login"] = page

        SafeLabel(
            page,
            text="Account Login & Buyer Registration",
            font=("Georgia", 16, "bold"),
            bg=BG_CREAM,
            fg=DARK_GREEN,
        ).pack(anchor="w", pady=(0, 10))

        cards_frame = tk.Frame(page, bg=BG_CREAM)
        cards_frame.pack(fill="x", pady=(0, 14))
        cards_frame.grid_columnconfigure(0, weight=1, uniform="login_cards")
        cards_frame.grid_columnconfigure(1, weight=1, uniform="login_cards")
        cards_frame.grid_columnconfigure(2, weight=1, uniform="login_cards")

        # Card 1: Buyer Account Login
        buyer_card = ttk.LabelFrame(
            cards_frame,
            text=" Buyer Account Login ",
            style="Panel.TLabelframe",
            padding=(14, 10),
        )
        buyer_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        SafeLabel(buyer_card, text="Buyer Name or ID:", bg=BG_PANEL).pack(anchor="w")
        self.buyer_login_id = ttk.Entry(buyer_card, font=("Arial", 10))
        self.buyer_login_id.insert(0, "Alice Johnson")
        self.buyer_login_id.pack(fill="x", pady=(2, 8))

        SafeLabel(buyer_card, text="Phone Number:", bg=BG_PANEL).pack(anchor="w")
        self.buyer_login_phone = ttk.Entry(buyer_card, font=("Arial", 10))
        self.buyer_login_phone.insert(0, "415-555-0211")
        self.buyer_login_phone.pack(fill="x", pady=(2, 12))

        tk.Button(
            buyer_card,
            text="Login as Buyer",
            command=self.handle_buyer_login,
            bg=BROWN_PRIMARY,
            fg="white",
            font=("Arial", 10, "bold"),
            pady=6,
        ).pack(fill="x")

        # Card 2: Create New Buyer Account (CRUD: Create)
        reg_card = ttk.LabelFrame(
            cards_frame,
            text=" Create New Buyer Account ",
            style="PanelGreen.TLabelframe",
            padding=(14, 10),
        )
        reg_card.grid(row=0, column=1, sticky="nsew", padx=8)

        SafeLabel(reg_card, text="Full Name:", bg=BG_PANEL).pack(anchor="w")
        self.reg_name = ttk.Entry(reg_card, font=("Arial", 10))
        self.reg_name.pack(fill="x", pady=(1, 4))

        SafeLabel(reg_card, text="Phone Number:", bg=BG_PANEL).pack(anchor="w")
        self.reg_phone = ttk.Entry(reg_card, font=("Arial", 10))
        self.reg_phone.pack(fill="x", pady=(1, 4))

        SafeLabel(reg_card, text="Shipping Address:", bg=BG_PANEL).pack(anchor="w")
        self.reg_address = ttk.Entry(reg_card, font=("Arial", 10))
        self.reg_address.pack(fill="x", pady=(1, 4))

        SafeLabel(reg_card, text="Payment Method:", bg=BG_PANEL).pack(anchor="w")
        self.reg_payment = ttk.Combobox(
            reg_card,
            values=["Credit", "Debit", "PayPal", "Apple Pay", "Cash"],
            state="readonly",
        )
        self.reg_payment.set("Credit")
        self.reg_payment.pack(fill="x", pady=(1, 8))

        tk.Button(
            reg_card,
            text="Register & Sign In",
            command=self.handle_buyer_register,
            bg=DARK_GREEN,
            fg="white",
            font=("Arial", 10, "bold"),
            pady=6,
        ).pack(fill="x")

        # Card 3: Store Partner Login
        store_card = ttk.LabelFrame(
            cards_frame,
            text=" Store Partner Login ",
            style="PanelAccent.TLabelframe",
            padding=(14, 10),
        )
        store_card.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        SafeLabel(store_card, text="Store Name or ID:", bg=BG_PANEL).pack(anchor="w")
        self.store_login_id = ttk.Entry(store_card, font=("Arial", 10))
        self.store_login_id.insert(0, "City Lights Books")
        self.store_login_id.pack(fill="x", pady=(2, 8))

        SafeLabel(store_card, text="Store Phone Number:", bg=BG_PANEL).pack(anchor="w")
        self.store_login_phone = ttk.Entry(store_card, font=("Arial", 10))
        self.store_login_phone.insert(0, "415-555-0101")
        self.store_login_phone.pack(fill="x", pady=(2, 12))

        tk.Button(
            store_card,
            text="Login as Store Partner",
            command=self.handle_store_login,
            bg=BROWN_ACCENT,
            fg="white",
            font=("Arial", 10, "bold"),
            pady=6,
        ).pack(fill="x")

        # Sample Accounts Reference Table
        sample_frame = ttk.LabelFrame(
            page,
            text=" Sample Accounts in Database (Double-click a row to auto-fill login) ",
            style="Cream.TLabelframe",
            padding=(10, 8),
        )
        sample_frame.pack(fill="both", expand=True)

        cols = ("AccountType", "ID", "Name", "PhoneNumber", "Details")
        self.sample_tree = ttk.Treeview(sample_frame, columns=cols, show="headings", height=8)
        for col, heading, width in [
            ("AccountType", "Account Type", 110),
            ("ID", "ID", 60),
            ("Name", "Name", 200),
            ("PhoneNumber", "Phone Number", 130),
            ("Details", "Details", 420),
        ]:
            self.sample_tree.heading(col, text=heading)
            self.sample_tree.column(col, width=width)
        self.sample_tree.pack(fill="both", expand=True)
        self.sample_tree.bind("<Double-1>", self._autofill_from_sample)

    def refresh_sample_accounts(self):
        try:
            rows = db.get_sample_accounts()
            for item in self.sample_tree.get_children():
                self.sample_tree.delete(item)
            for r in rows:
                self.sample_tree.insert("", "end", values=r)
        except Exception as err:
            messagebox.showerror("Database Error", str(err))

    def _autofill_from_sample(self, _event):
        selected = self.sample_tree.selection()
        if not selected:
            return
        acct_type, _id, name, phone, _details = self.sample_tree.item(selected[0], "values")
        if acct_type == "Buyer":
            self.buyer_login_id.delete(0, tk.END)
            self.buyer_login_id.insert(0, name)
            self.buyer_login_phone.delete(0, tk.END)
            self.buyer_login_phone.insert(0, phone)
        else:
            self.store_login_id.delete(0, tk.END)
            self.store_login_id.insert(0, name)
            self.store_login_phone.delete(0, tk.END)
            self.store_login_phone.insert(0, phone)

    def handle_buyer_login(self):
        try:
            buyer = db.login_buyer(self.buyer_login_id.get(), self.buyer_login_phone.get())
            if not buyer:
                messagebox.showerror("Login Failed", "No matching Buyer found with that Name/ID and Phone Number.")
                return
            self.current_buyer = buyer
            self.current_store = None
            self.update_session_banner()
            messagebox.showinfo("Welcome", f"Logged in as {buyer['BuyerName']}!")
            self.show_page("search")
        except Exception as err:
            messagebox.showerror("Database Error", str(err))

    def handle_buyer_register(self):
        name = self.reg_name.get().strip()
        phone = self.reg_phone.get().strip()
        address = self.reg_address.get().strip()
        payment = self.reg_payment.get().strip()

        if not (name and phone and address):
            messagebox.showwarning("Missing Fields", "Please fill in Full Name, Phone Number, and Shipping Address.")
            return

        ok, msg, buyer = db.register_buyer(name, phone, address, payment)
        if ok and buyer:
            self.current_buyer = buyer
            self.current_store = None
            self.update_session_banner()
            self.reg_name.delete(0, tk.END)
            self.reg_phone.delete(0, tk.END)
            self.reg_address.delete(0, tk.END)
            messagebox.showinfo("Registration Complete", msg)
            self.show_page("search")
        else:
            messagebox.showerror("Registration Error", msg)

    def handle_store_login(self):
        try:
            store = db.login_store(self.store_login_id.get(), self.store_login_phone.get())
            if not store:
                messagebox.showerror("Login Failed", "No matching Store found with that Name/ID and Phone Number.")
                return
            self.current_store = store
            self.current_buyer = None
            self.update_session_banner()
            messagebox.showinfo("Store Partner Portal", f"Logged in as {store['StoreName']}!")
            self.show_page("admin")
        except Exception as err:
            messagebox.showerror("Database Error", str(err))

    # ========================================================================
    # PAGE 2: SEARCH & BOOKS 
    # ========================================================================
    def _build_search_page(self):
        page = tk.Frame(self.content_container, bg=BG_CREAM)
        page.grid(row=0, column=0, sticky="nsew")
        self.pages["search"] = page

        filter_box = ttk.LabelFrame(
            page,
            text=" Search Books & Filter by Category ",
            style="PanelGreen.TLabelframe",
            padding=(12, 8),
        )
        filter_box.pack(fill="x", pady=(0, 10))

        # Row 1: Keyword + Genre (Subquery) + Author
        row1 = tk.Frame(filter_box, bg=BG_PANEL)
        row1.pack(fill="x", pady=3)

        SafeLabel(row1, text="Keyword (Title/Author/Publisher):", bg=BG_PANEL).pack(side="left")
        self.search_keyword = ttk.Entry(row1, width=26, font=("Arial", 10))
        self.search_keyword.pack(side="left", padx=(6, 16))
        self.search_keyword.bind("<Return>", lambda _e: self.run_book_search())

        SafeLabel(row1, text="Genre (Subquery):", bg=BG_PANEL).pack(side="left")
        self.genre_combo = ttk.Combobox(row1, width=15, state="readonly")
        self.genre_combo.set("All")
        self.genre_combo.pack(side="left", padx=(6, 16))

        SafeLabel(row1, text="Author:", bg=BG_PANEL).pack(side="left")
        self.author_combo = ttk.Combobox(row1, width=20, state="readonly")
        self.author_combo.set("All")
        self.author_combo.pack(side="left", padx=6)

        # Row 2: Store + Above-Average Price Subquery + Action Buttons
        row2 = tk.Frame(filter_box, bg=BG_PANEL)
        row2.pack(fill="x", pady=(6, 2))

        SafeLabel(row2, text="Store Location:", bg=BG_PANEL).pack(side="left")
        self.store_combo = ttk.Combobox(row2, width=22, state="readonly")
        self.store_combo.set("All")
        self.store_combo.pack(side="left", padx=(6, 16))

        self.above_avg_var = tk.BooleanVar(value=False)
        self._make_checkbox(
            row2,
            text="Above Average Price Only (Subquery)",
            variable=self.above_avg_var,
            bg=BG_PANEL,
            font=("Arial", 9),
        ).pack(side="left", padx=(0, 16))

        tk.Button(
            row2,
            text="Search",
            command=self.run_book_search,
            bg=BROWN_ACCENT,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=14,
        ).pack(side="left", padx=4)

        tk.Button(
            row2,
            text="Reset Filters",
            command=self.reset_book_filters,
            bg="#6B7280",
            fg="white",
            font=("Arial", 10),
            padx=10,
        ).pack(side="left", padx=4)

        # Search Results Table
        table_frame = tk.Frame(page, bg=BG_CREAM)
        table_frame.pack(fill="both", expand=True)

        cols = ("InvID", "BookName", "AuthorName", "Genre", "Publisher", "StoreName", "Price", "InStock")
        self.catalog_tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        col_specs = [
            ("InvID", "Inv ID", 65),
            ("BookName", "Book Title", 210),
            ("AuthorName", "Author", 160),
            ("Genre", "Genre", 105),
            ("Publisher", "Publisher", 145),
            ("StoreName", "Store", 175),
            ("Price", "Price", 80),
            ("InStock", "In Stock", 75),
        ]
        for col, heading, w in col_specs:
            self.catalog_tree.heading(col, text=heading)
            self.catalog_tree.column(col, width=w)
        self.catalog_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.catalog_tree.yview)
        self.catalog_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Bottom Add-to-Cart Bar
        bottom_bar = tk.Frame(page, bg=BG_PANEL, padx=12, pady=10)
        bottom_bar.pack(fill="x", pady=(10, 0))

        SafeLabel(bottom_bar, text="Quantity:", bg=BG_PANEL, font=("Arial", 10, "bold")).pack(side="left")
        self.catalog_qty_entry = ttk.Entry(bottom_bar, width=8, font=("Arial", 10))
        self.catalog_qty_entry.insert(0, "1")
        self.catalog_qty_entry.pack(side="left", padx=(6, 14))

        tk.Button(
            bottom_bar,
            text="+ Add Selected to Cart",
            command=self.handle_add_selected_to_cart,
            bg=BROWN_PRIMARY,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=14,
            pady=4,
        ).pack(side="left")

        tk.Button(
            bottom_bar,
            text="View My Cart ->",
            command=lambda: self.show_page("cart"),
            bg=DARK_GREEN,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=14,
            pady=4,
        ).pack(side="right")

    def refresh_filter_dropdowns(self):
        try:
            opts = db.get_filter_options()
            self.genre_combo["values"] = opts["genres"]
            self.author_combo["values"] = opts["authors"]
            self.store_combo["values"] = opts["stores"]
        except Exception as err:
            messagebox.showerror("Database Error", str(err))

    def reset_book_filters(self):
        self.search_keyword.delete(0, tk.END)
        self.genre_combo.set("All")
        self.author_combo.set("All")
        self.store_combo.set("All")
        self.above_avg_var.set(False)
        self.run_book_search()

    def run_book_search(self):
        try:
            rows = db.search_books(
                search_text=self.search_keyword.get(),
                genre=self.genre_combo.get(),
                author=self.author_combo.get(),
                store=self.store_combo.get(),
                above_avg_price=self.above_avg_var.get(),
            )
            for item in self.catalog_tree.get_children():
                self.catalog_tree.delete(item)
            for r in rows:
                formatted = (r[0], r[1], r[2], r[3], r[4], r[5], f"${r[6]:.2f}", r[7])
                self.catalog_tree.insert("", "end", values=formatted)
        except Exception as err:
            messagebox.showerror("Search Error", str(err))

    def handle_add_selected_to_cart(self):
        if not self.current_buyer:
            messagebox.showwarning("Login Required", "Please log in as a Buyer on Page 1 before adding items to a cart.")
            self.show_page("login")
            return

        selected = self.catalog_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a book from the table first.")
            return

        try:
            qty = int(self.catalog_qty_entry.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Enter a positive whole number for quantity.")
            return

        values = self.catalog_tree.item(selected[0], "values")
        inv_id = int(values[0])

        ok, msg = db.add_to_cart(self.current_buyer["BuyerID"], inv_id, qty)
        if ok:
            messagebox.showinfo("Cart Updated", msg)
        else:
            messagebox.showerror("Cannot Add to Cart", msg)

    # ========================================================================
    # PAGE 3: SHOPPING CART
    # ========================================================================
    def _build_cart_page(self):
        page = tk.Frame(self.content_container, bg=BG_CREAM)
        page.grid(row=0, column=0, sticky="nsew")
        self.pages["cart"] = page

        # Quick Add Bar
        quick_box = ttk.LabelFrame(
            page,
            text=" Quick Add Book to Cart ",
            style="PanelGreen.TLabelframe",
            padding=(12, 8),
        )
        quick_box.pack(fill="x", pady=(0, 10))

        SafeLabel(quick_box, text="Inventory Item:", bg=BG_PANEL).pack(side="left")
        self.cart_quick_combo = ttk.Combobox(quick_box, width=52, state="readonly")
        self.cart_quick_combo.pack(side="left", padx=(6, 12))

        SafeLabel(quick_box, text="Qty:", bg=BG_PANEL).pack(side="left")
        self.cart_quick_qty = ttk.Entry(quick_box, width=6)
        self.cart_quick_qty.insert(0, "1")
        self.cart_quick_qty.pack(side="left", padx=(4, 10))

        tk.Button(
            quick_box,
            text="+ Add to Cart",
            command=self.handle_cart_quick_add,
            bg=BROWN_PRIMARY,
            fg="white",
            font=("Arial", 9, "bold"),
            padx=10,
        ).pack(side="left")

        # Current Shopping Cart Table
        cart_label_frame = ttk.LabelFrame(
            page,
            text=" Current Shopping Cart Items ",
            style="Cream.TLabelframe",
            padding=(10, 8),
        )
        cart_label_frame.pack(fill="both", expand=True)

        cols = ("CartID", "BuyerName", "BookName", "StoreName", "UnitPrice", "CartQty", "InStock", "Subtotal")
        self.cart_tree = ttk.Treeview(cart_label_frame, columns=cols, show="headings")
        for col, heading, w in [
            ("CartID", "Cart ID", 70),
            ("BuyerName", "Buyer", 140),
            ("BookName", "Book Title", 220),
            ("StoreName", "Store", 180),
            ("UnitPrice", "Unit Price", 90),
            ("CartQty", "Qty", 80),
            ("InStock", "In Stock", 80),
            ("Subtotal", "Subtotal", 95),
        ]:
            self.cart_tree.heading(col, text=heading)
            self.cart_tree.column(col, width=w)
        self.cart_tree.pack(fill="both", expand=True)

        # Cart Actions & Aggregated Total Footer
        actions_bar = tk.Frame(page, bg=BG_PANEL, padx=12, pady=10)
        actions_bar.pack(fill="x", pady=(10, 0))

        SafeLabel(actions_bar, text="New Qty:", bg=BG_PANEL).pack(side="left")
        self.cart_update_qty_entry = ttk.Entry(actions_bar, width=6, font=("Arial", 10))
        self.cart_update_qty_entry.insert(0, "1")
        self.cart_update_qty_entry.pack(side="left", padx=(4, 8))

        tk.Button(
            actions_bar,
            text="Update Quantity",
            command=self.handle_update_cart_qty,
            bg=BROWN_ACCENT,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
        ).pack(side="left", padx=4)

        tk.Button(
            actions_bar,
            text="Remove Selected Item",
            command=self.handle_remove_cart_item,
            bg="#991B1B",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
        ).pack(side="left", padx=8)

        tk.Button(
            actions_bar,
            text="Proceed to Checkout ->",
            command=lambda: self.show_page("checkout"),
            bg=DARK_GREEN,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=14,
            pady=4,
        ).pack(side="right")

        self.cart_total_label = SafeLabel(
            actions_bar,
            text="Cart Total: $0.00 (0 books)",
            font=("Arial", 12, "bold"),
            bg=BG_PANEL,
            fg=DARK_GREEN,
            justify="right",
        )
        self.cart_total_label.pack(side="right", padx=18)

    def refresh_cart_page(self):
        try:
            choices = db.get_active_inventory_choices()
            self.quick_inventory_map = {}
            labels = []
            for inv_id, b_name, s_name, price, qty in choices:
                lbl = f"#{inv_id}: {b_name} @ {s_name} (${price:.2f} | {qty} in stock)"
                self.quick_inventory_map[lbl] = inv_id
                labels.append(lbl)
            self.cart_quick_combo["values"] = labels
            if labels:
                self.cart_quick_combo.current(0)
        except Exception as err:
            messagebox.showerror("Database Error", str(err))

        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        if not self.current_buyer:
            self.cart_total_label.config(text="Log in as a Buyer to view your cart")
            return

        try:
            rows = db.get_cart_items(self.current_buyer["BuyerID"])
            for r in rows:
                formatted = (
                    r[0], r[1], r[2], r[3],
                    f"${r[4]:.2f}", r[5], r[6], f"${r[7]:.2f}"
                )
                self.cart_tree.insert("", "end", values=formatted)

            total_books, cart_total = db.get_cart_summary(self.current_buyer["BuyerID"])
            self.cart_total_label.config(
                text=f"Cart Total: ${float(cart_total):.2f} ({int(total_books)} books)"
            )
        except Exception as err:
            messagebox.showerror("Cart Error", str(err))

    def handle_cart_quick_add(self):
        if not self.current_buyer:
            messagebox.showwarning("Login Required", "Please log in as a Buyer first.")
            self.show_page("login")
            return

        lbl = self.cart_quick_combo.get()
        if lbl not in self.quick_inventory_map:
            return
        try:
            qty = int(self.cart_quick_qty.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Enter a positive integer quantity.")
            return

        ok, msg = db.add_to_cart(self.current_buyer["BuyerID"], self.quick_inventory_map[lbl], qty)
        if ok:
            self.refresh_cart_page()
        else:
            messagebox.showerror("Cannot Add", msg)

    def handle_update_cart_qty(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Select a cart row to update.")
            return
        try:
            new_qty = int(self.cart_update_qty_entry.get())
            if new_qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Enter a positive integer quantity.")
            return

        cart_id = int(self.cart_tree.item(selected[0], "values")[0])
        ok, msg = db.update_cart_quantity(cart_id, new_qty)
        if ok:
            self.refresh_cart_page()
        else:
            messagebox.showerror("Update Error", msg)

    def handle_remove_cart_item(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Select a cart row to remove.")
            return
        cart_id = int(self.cart_tree.item(selected[0], "values")[0])
        ok, msg = db.remove_cart_item(cart_id)
        if ok:
            self.refresh_cart_page()
        else:
            messagebox.showerror("Remove Error", msg)

    # ========================================================================
    # PAGE 4: CHECKOUT 
    # ========================================================================
    def _build_checkout_page(self):
        page = tk.Frame(self.content_container, bg=BG_CREAM)
        page.grid(row=0, column=0, sticky="nsew")
        self.pages["checkout"] = page

        summary_frame = ttk.LabelFrame(
            page,
            text=" Order Items Summary (Ready to Commit) ",
            style="Cream.TLabelframe",
            padding=(10, 8),
        )
        summary_frame.pack(fill="both", expand=True, pady=(0, 10))

        cols = ("BookName", "AuthorName", "StoreName", "UnitPrice", "OrderQty", "LineTotal")
        self.checkout_tree = ttk.Treeview(summary_frame, columns=cols, show="headings", height=7)
        for col, heading, w in [
            ("BookName", "Book Title", 240),
            ("AuthorName", "Author", 170),
            ("StoreName", "Store", 190),
            ("UnitPrice", "Unit Price", 95),
            ("OrderQty", "Order Qty", 90),
            ("LineTotal", "Line Total", 105),
        ]:
            self.checkout_tree.heading(col, text=heading)
            self.checkout_tree.column(col, width=w)
        self.checkout_tree.pack(fill="both", expand=True)

        bottom_split = tk.Frame(page, bg=BG_CREAM)
        bottom_split.pack(fill="x")
        bottom_split.grid_columnconfigure(0, weight=1, uniform="chk_cards")
        bottom_split.grid_columnconfigure(1, weight=1, uniform="chk_cards")

        # Left: Buyer Billing & Delivery Details (Editable -> UPDATE buyer)
        billing_card = ttk.LabelFrame(
            bottom_split,
            text=" Buyer Billing & Delivery Details ",
            style="Panel.TLabelframe",
            padding=(12, 10),
        )
        billing_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.chk_buyer_info_lbl = SafeLabel(
            billing_card,
            text="Buyer: Not logged in",
            font=("Arial", 10, "bold"),
            bg=BG_PANEL,
        )
        self.chk_buyer_info_lbl.pack(anchor="w", pady=(0, 6))

        SafeLabel(billing_card, text="Delivery Address:", bg=BG_PANEL).pack(anchor="w")
        self.chk_address_entry = ttk.Entry(billing_card, font=("Arial", 10))
        self.chk_address_entry.pack(fill="x", pady=(2, 6))

        SafeLabel(billing_card, text="Payment Method:", bg=BG_PANEL).pack(anchor="w")
        self.chk_payment_combo = ttk.Combobox(
            billing_card,
            values=["Credit", "Debit", "PayPal", "Apple Pay", "Cash"],
            state="readonly",
        )
        self.chk_payment_combo.pack(fill="x", pady=(2, 8))

        tk.Button(
            billing_card,
            text="Save Updated Address / Payment",
            command=self.handle_update_buyer_checkout,
            bg=BROWN_ACCENT,
            fg="white",
            font=("Arial", 9, "bold"),
            pady=4,
        ).pack(anchor="e")

        # Right: Transaction Summary & Confirmation (COMMIT / ROLLBACK)
        tx_card = ttk.LabelFrame(
            bottom_split,
            text=" Transaction Summary & Confirmation ",
            style="PanelGreen.TLabelframe",
            padding=(12, 10),
        )
        tx_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.chk_total_books_lbl = SafeLabel(
            tx_card, text="Total Books: 0", font=("Arial", 11, "bold"), bg=BG_PANEL
        )
        self.chk_total_books_lbl.pack(anchor="w", pady=2)

        self.chk_order_total_lbl = SafeLabel(
            tx_card,
            text="Order Total: $0.00",
            font=("Arial", 13, "bold"),
            fg=DARK_GREEN,
            bg=BG_PANEL,
        )
        self.chk_order_total_lbl.pack(anchor="w", pady=(2, 8))

        self.simulate_rollback_var = tk.BooleanVar(value=False)
        self._make_checkbox(
            tx_card,
            text="Simulate Failure (Test ROLLBACK)",
            variable=self.simulate_rollback_var,
            bg=BG_PANEL,
            fg="#991B1B",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        btn_row = tk.Frame(tx_card, bg=BG_PANEL)
        btn_row.pack(fill="x")

        tk.Button(
            btn_row,
            text="<- Back to Cart",
            command=lambda: self.show_page("cart"),
            bg="#6B7280",
            fg="white",
            font=("Arial", 10),
            padx=10,
            pady=6,
        ).pack(side="left")

        tk.Button(
            btn_row,
            text="Place Order (COMMIT Transaction)",
            command=self.handle_place_order,
            bg=DARK_GREEN,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=6,
        ).pack(side="right")

    def refresh_checkout_page(self):
        for item in self.checkout_tree.get_children():
            self.checkout_tree.delete(item)

        if not self.current_buyer:
            self.chk_buyer_info_lbl.config(text="Buyer: Please log in on Page 1 first.")
            self.chk_total_books_lbl.config(text="Total Books: 0")
            self.chk_order_total_lbl.config(text="Order Total: $0.00")
            return

        b = self.current_buyer
        self.chk_buyer_info_lbl.config(text=f"Buyer: {b['BuyerName']}  |  Phone: {b['PhoneNumber']}")
        self.chk_address_entry.delete(0, tk.END)
        self.chk_address_entry.insert(0, b["Address"])
        self.chk_payment_combo.set(b["PaymentMethod"])

        try:
            rows = db.get_cart_items(b["BuyerID"])
            for r in rows:
                self.checkout_tree.insert(
                    "",
                    "end",
                    values=(r[2], r[8], r[3], f"${r[4]:.2f}", r[5], f"${r[7]:.2f}"),
                )
            total_books, cart_total = db.get_cart_summary(b["BuyerID"])
            self.chk_total_books_lbl.config(text=f"Total Books: {int(total_books)}")
            self.chk_order_total_lbl.config(text=f"Order Total: ${float(cart_total):.2f}")
        except Exception as err:
            messagebox.showerror("Checkout Error", str(err))

    def handle_update_buyer_checkout(self):
        if not self.current_buyer:
            messagebox.showwarning("Login Required", "Log in as a Buyer first.")
            return
        new_addr = self.chk_address_entry.get().strip()
        new_pay = self.chk_payment_combo.get().strip()
        if not new_addr:
            messagebox.showwarning("Invalid Address", "Address cannot be empty.")
            return
        ok, msg = db.update_buyer_details(self.current_buyer["BuyerID"], new_addr, new_pay)
        if ok:
            self.current_buyer["Address"] = new_addr
            self.current_buyer["PaymentMethod"] = new_pay
            messagebox.showinfo("Updated", msg)
        else:
            messagebox.showerror("Error", msg)

    def handle_place_order(self):
        if not self.current_buyer:
            messagebox.showwarning("Login Required", "Please log in as a Buyer before placing an order.")
            self.show_page("login")
            return

        simulate_fail = self.simulate_rollback_var.get()
        ok, msg = db.checkout_order(self.current_buyer["BuyerID"], simulate_failure=simulate_fail)
        if ok:
            messagebox.showinfo("Transaction Committed", msg)
            self.show_page("admin")
        else:
            messagebox.showerror("Transaction Rolled Back", msg)
            self.refresh_checkout_page()

    # ========================================================================
    # PAGE 5: PAST ORDERS (VIEW), GROUP BY ANALYTICS, STORE CRUD/SOFT DELETE & CSV
    # ========================================================================
    def _build_admin_reports_page(self):
        page = tk.Frame(self.content_container, bg=BG_CREAM)
        page.grid(row=0, column=0, sticky="nsew")
        self.pages["admin"] = page

        notebook = ttk.Notebook(page)
        notebook.pack(fill="both", expand=True)

        # Tab A: Past Orders (vPastOrders View) & Buyer Spending (GROUP BY)
        orders_tab = tk.Frame(notebook, bg=BG_CREAM, padx=8, pady=8)
        notebook.add(orders_tab, text="Past Orders (vPastOrders View) & Buyer Analytics")

        top_controls = tk.Frame(orders_tab, bg=BG_CREAM)
        top_controls.pack(fill="x", pady=(0, 6))

        self.filter_my_orders_var = tk.BooleanVar(value=False)
        self._make_checkbox(
            top_controls,
            text="Show Only Logged-In Buyer's Orders",
            variable=self.filter_my_orders_var,
            bg=BG_CREAM,
            font=("Arial", 10),
            command=self.refresh_orders_tab,
        ).pack(side="left")

        tk.Button(
            top_controls,
            text="Export Customer & Order Report (.csv)",
            command=lambda: self.handle_export_csv("customers"),
            bg=DARK_GREEN,
            fg="white",
            font=("Arial", 9, "bold"),
            padx=10,
        ).pack(side="right")

        # Past Orders Treeview (from vPastOrders)
        orders_frame = ttk.LabelFrame(
            orders_tab,
            text=" Completed Orders (Database View: vPastOrders) ",
            style="Cream.TLabelframe",
            padding=(6, 6),
        )
        orders_frame.pack(fill="both", expand=True, pady=(0, 8))

        o_cols = ("OrderID", "BuyerName", "BookName", "AuthorName", "Genre", "StoreName", "Qty", "UnitPrice", "LineTotal")
        self.past_orders_tree = ttk.Treeview(orders_frame, columns=o_cols, show="headings", height=7)
        for col, heading, w in [
            ("OrderID", "Order ID", 70),
            ("BuyerName", "Buyer", 130),
            ("BookName", "Book Title", 190),
            ("AuthorName", "Author", 140),
            ("Genre", "Genre", 95),
            ("StoreName", "Store", 155),
            ("Qty", "Qty", 55),
            ("UnitPrice", "Unit Price", 80),
            ("LineTotal", "Line Total", 85),
        ]:
            self.past_orders_tree.heading(col, text=heading)
            self.past_orders_tree.column(col, width=w)
        self.past_orders_tree.pack(fill="both", expand=True)

        # Aggregation / GROUP BY Summary Table
        agg_frame = ttk.LabelFrame(
            orders_tab,
            text=" Customer Order Totals (Aggregation: COUNT & SUM with GROUP BY) ",
            style="Cream.TLabelframe",
            padding=(6, 6),
        )
        agg_frame.pack(fill="x")

        a_cols = ("BuyerID", "BuyerName", "TotalOrders", "TotalBooks", "TotalSpent")
        self.buyer_agg_tree = ttk.Treeview(agg_frame, columns=a_cols, show="headings", height=5)
        for col, heading, w in [
            ("BuyerID", "Buyer ID", 80),
            ("BuyerName", "Buyer Name", 220),
            ("TotalOrders", "Total Orders", 120),
            ("TotalBooks", "Total Books", 120),
            ("TotalSpent", "Total Spent", 140),
        ]:
            self.buyer_agg_tree.heading(col, text=heading)
            self.buyer_agg_tree.column(col, width=w)
        self.buyer_agg_tree.pack(fill="x")

        # Tab B: Store Inventory Management (vStoreInventory View, Create, Update, Soft Delete, CSV)
        store_tab = tk.Frame(notebook, bg=BG_CREAM, padx=8, pady=8)
        notebook.add(store_tab, text="Store Inventory Admin (CRUD, Soft Delete & CSV Export)")

        store_top = tk.Frame(store_tab, bg=BG_CREAM)
        store_top.pack(fill="x", pady=(0, 6))

        self.store_scope_lbl = SafeLabel(
            store_top,
            text="Viewing: All Stores (Database View: vStoreInventory)",
            font=("Arial", 10, "bold"),
            bg=BG_CREAM,
            fg=DARK_GREEN,
        )
        self.store_scope_lbl.pack(side="left")

        tk.Button(
            store_top,
            text="Export Store Inventory & Sales Report (.csv)",
            command=lambda: self.handle_export_csv("inventory"),
            bg=DARK_GREEN,
            fg="white",
            font=("Arial", 9, "bold"),
            padx=10,
        ).pack(side="right")

        inv_cols = ("InvID", "StoreName", "BookName", "AuthorName", "Genre", "Price", "Quantity", "Status")
        self.admin_inv_tree = ttk.Treeview(store_tab, columns=inv_cols, show="headings", height=8)
        for col, heading, w in [
            ("InvID", "Inv ID", 65),
            ("StoreName", "Store", 175),
            ("BookName", "Book Title", 210),
            ("AuthorName", "Author", 155),
            ("Genre", "Genre", 100),
            ("Price", "Price", 80),
            ("Quantity", "Quantity", 75),
            ("Status", "Status", 100),
        ]:
            self.admin_inv_tree.heading(col, text=heading)
            self.admin_inv_tree.column(col, width=w)
        self.admin_inv_tree.pack(fill="both", expand=True, pady=(0, 8))
        self.admin_inv_tree.bind("<<TreeviewSelect>>", self._on_admin_inv_select)

        # CRUD Controls Split: Left = Update / Soft Delete Selected | Right = Create New Listing
        crud_split = tk.Frame(store_tab, bg=BG_CREAM)
        crud_split.pack(fill="x")
        crud_split.grid_columnconfigure(0, weight=1)
        crud_split.grid_columnconfigure(1, weight=2)

        # Update & Soft Delete Panel
        mod_frame = ttk.LabelFrame(
            crud_split,
            text=" Update / Soft Delete Selected Inventory ",
            style="PanelBlack.TLabelframe",
            padding=(10, 8),
        )
        mod_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        r_up = tk.Frame(mod_frame, bg=BG_PANEL)
        r_up.pack(fill="x", pady=4)
        SafeLabel(r_up, text="Price ($):", bg=BG_PANEL).pack(side="left")
        self.upd_price_entry = ttk.Entry(r_up, width=8)
        self.upd_price_entry.pack(side="left", padx=(4, 10))

        SafeLabel(r_up, text="Stock:", bg=BG_PANEL).pack(side="left")
        self.upd_qty_entry = ttk.Entry(r_up, width=7)
        self.upd_qty_entry.pack(side="left", padx=4)

        tk.Button(
            mod_frame,
            text="Update Price & Stock",
            command=self.handle_update_inventory,
            bg=BROWN_ACCENT,
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(fill="x", pady=(4, 6))

        soft_row = tk.Frame(mod_frame, bg=BG_PANEL)
        soft_row.pack(fill="x")
        tk.Button(
            soft_row,
            text="Soft Delete (Discontinue)",
            command=lambda: self.handle_soft_delete(False),
            bg="#991B1B",
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(side="left", expand=True, fill="x", padx=(0, 3))

        tk.Button(
            soft_row,
            text="Restore Active",
            command=lambda: self.handle_soft_delete(True),
            bg=DARK_GREEN,
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(side="left", expand=True, fill="x", padx=(3, 0))

        # Add New Book & Inventory Panel (CRUD: Create)
        add_frame = ttk.LabelFrame(
            crud_split,
            text=" Add New Book to Store Inventory (Create Record) ",
            style="PanelBlack.TLabelframe",
            padding=(10, 8),
        )
        add_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        f1 = tk.Frame(add_frame, bg=BG_PANEL)
        f1.pack(fill="x", pady=2)
        SafeLabel(f1, text="Book Title:", bg=BG_PANEL).pack(side="left")
        self.new_book_title = ttk.Entry(f1, width=22)
        self.new_book_title.pack(side="left", padx=(4, 10))

        SafeLabel(f1, text="Author:", bg=BG_PANEL).pack(side="left")
        self.new_book_author = ttk.Combobox(f1, width=18, state="readonly")
        self.new_book_author.pack(side="left", padx=4)

        f2 = tk.Frame(add_frame, bg=BG_PANEL)
        f2.pack(fill="x", pady=2)
        SafeLabel(f2, text="Genre:", bg=BG_PANEL).pack(side="left")
        self.new_book_genre = ttk.Entry(f2, width=12)
        self.new_book_genre.insert(0, "Fiction")
        self.new_book_genre.pack(side="left", padx=(4, 8))

        SafeLabel(f2, text="Publisher:", bg=BG_PANEL).pack(side="left")
        self.new_book_pub = ttk.Entry(f2, width=15)
        self.new_book_pub.insert(0, "Penguin Books")
        self.new_book_pub.pack(side="left", padx=(4, 8))

        SafeLabel(f2, text="Release (YYYY-MM-DD):", bg=BG_PANEL).pack(side="left")
        self.new_book_date = ttk.Entry(f2, width=11)
        self.new_book_date.insert(0, "2024-01-15")
        self.new_book_date.pack(side="left", padx=4)

        f3 = tk.Frame(add_frame, bg=BG_PANEL)
        f3.pack(fill="x", pady=(4, 0))
        SafeLabel(f3, text="Store:", bg=BG_PANEL).pack(side="left")
        self.new_inv_store = ttk.Combobox(f3, width=20, state="readonly")
        self.new_inv_store.pack(side="left", padx=(4, 8))

        SafeLabel(f3, text="Price ($):", bg=BG_PANEL).pack(side="left")
        self.new_inv_price = ttk.Entry(f3, width=7)
        self.new_inv_price.insert(0, "16.99")
        self.new_inv_price.pack(side="left", padx=(4, 8))

        SafeLabel(f3, text="Qty:", bg=BG_PANEL).pack(side="left")
        self.new_inv_qty = ttk.Entry(f3, width=6)
        self.new_inv_qty.insert(0, "10")
        self.new_inv_qty.pack(side="left", padx=(4, 10))

        tk.Button(
            f3,
            text="+ Add Inventory",
            command=self.handle_create_inventory,
            bg=BROWN_PRIMARY,
            fg="white",
            font=("Arial", 9, "bold"),
            padx=10,
        ).pack(side="right")

    def refresh_admin_reports_page(self):
        self.refresh_orders_tab()
        self.refresh_store_admin_tab()

    def refresh_orders_tab(self):
        try:
            buyer_filter = None
            if self.filter_my_orders_var.get() and self.current_buyer:
                buyer_filter = self.current_buyer["BuyerID"]

            orders = db.get_past_orders(buyer_filter)
            for item in self.past_orders_tree.get_children():
                self.past_orders_tree.delete(item)
            for r in orders:
                formatted = (
                    r[0], r[1], r[2], r[3], r[4], r[5],
                    r[6], f"${float(r[7]):.2f}", f"${float(r[8]):.2f}"
                )
                self.past_orders_tree.insert("", "end", values=formatted)

            aggs = db.get_buyer_spending_summary()
            for item in self.buyer_agg_tree.get_children():
                self.buyer_agg_tree.delete(item)
            for r in aggs:
                self.buyer_agg_tree.insert(
                    "", "end", values=(r[0], r[1], r[2], r[3], f"${float(r[4]):.2f}")
                )
        except Exception as err:
            messagebox.showerror("Orders Error", str(err))

    def refresh_store_admin_tab(self):
        try:
            store_id = self.current_store["StoreID"] if self.current_store else None
            if self.current_store:
                self.store_scope_lbl.config(
                    text=f"Viewing Store: {self.current_store['StoreName']} (Database View: vStoreInventory)"
                )
            else:
                self.store_scope_lbl.config(
                    text="Viewing: All Stores (Database View: vStoreInventory)"
                )

            rows = db.get_store_inventory(store_id=store_id, include_inactive=True)
            for item in self.admin_inv_tree.get_children():
                self.admin_inv_tree.delete(item)
            for r in rows:
                formatted = (r[0], r[1], r[2], r[3], r[4], f"${float(r[5]):.2f}", r[6], r[7])
                self.admin_inv_tree.insert("", "end", values=formatted)

            authors, stores = db.get_authors_and_stores()
            self.author_id_map = {f"{a[0]} - {a[1]}": a[0] for a in authors}
            self.store_id_map = {f"{s[0]} - {s[1]}": s[0] for s in stores}

            self.new_book_author["values"] = list(self.author_id_map.keys())
            if self.author_id_map:
                self.new_book_author.current(0)

            self.new_inv_store["values"] = list(self.store_id_map.keys())
            if self.current_store:
                target = f"{self.current_store['StoreID']} - {self.current_store['StoreName']}"
                if target in self.store_id_map:
                    self.new_inv_store.set(target)
            elif self.store_id_map:
                self.new_inv_store.current(0)
        except Exception as err:
            messagebox.showerror("Store Admin Error", str(err))

    def _on_admin_inv_select(self, _event):
        selected = self.admin_inv_tree.selection()
        if not selected:
            return
        vals = self.admin_inv_tree.item(selected[0], "values")
        self.upd_price_entry.delete(0, tk.END)
        self.upd_price_entry.insert(0, vals[5].replace("$", ""))
        self.upd_qty_entry.delete(0, tk.END)
        self.upd_qty_entry.insert(0, vals[6])

    def handle_update_inventory(self):
        selected = self.admin_inv_tree.selection()
        if not selected:
            messagebox.showwarning("Select Row", "Select an inventory row first.")
            return
        inv_id = int(self.admin_inv_tree.item(selected[0], "values")[0])
        try:
            price = float(self.upd_price_entry.get())
            qty = int(self.upd_qty_entry.get())
            if price < 0 or qty < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid non-negative price and stock quantity.")
            return

        ok, msg = db.update_inventory_record(inv_id, price, qty)
        if ok:
            messagebox.showinfo("Updated", msg)
            self.refresh_store_admin_tab()
        else:
            messagebox.showerror("Error", msg)

    def handle_soft_delete(self, restore):
        selected = self.admin_inv_tree.selection()
        if not selected:
            messagebox.showwarning("Select Row", "Select an inventory row first.")
            return
        inv_id = int(self.admin_inv_tree.item(selected[0], "values")[0])
        ok, msg = db.set_inventory_active_status(inv_id, restore)
        if ok:
            messagebox.showinfo("Inventory Status Updated", msg)
            self.refresh_store_admin_tab()
        else:
            messagebox.showerror("Error", msg)

    def handle_create_inventory(self):
        title = self.new_book_title.get().strip()
        author_key = self.new_book_author.get()
        store_key = self.new_inv_store.get()
        genre = self.new_book_genre.get().strip()
        publisher = self.new_book_pub.get().strip()
        rel_date = self.new_book_date.get().strip()

        if not (title and author_key and store_key and rel_date):
            messagebox.showwarning("Missing Fields", "Please complete Title, Author, Release Date, and Store.")
            return

        try:
            price = float(self.new_inv_price.get())
            qty = int(self.new_inv_qty.get())
            if price < 0 or qty < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Numbers", "Enter valid numeric values for Price and Quantity.")
            return

        ok, msg = db.create_book_and_inventory(
            book_name=title,
            author_id=self.author_id_map[author_key],
            genre=genre,
            publisher=publisher,
            release_date=rel_date,
            store_id=self.store_id_map[store_key],
            price=price,
            quantity=qty,
        )
        if ok:
            self.new_book_title.delete(0, tk.END)
            messagebox.showinfo("Created", msg)
            self.refresh_store_admin_tab()
        else:
            messagebox.showerror("Create Error", msg)

    def handle_export_csv(self, report_type):
        default_name = (
            "customer_orders_report.csv"
            if report_type == "customers"
            else "store_inventory_sales_report.csv"
        )
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV Files", "*.csv")],
        )
        if not path:
            return
        ok, msg = db.export_report_csv(report_type, path)
        if ok:
            messagebox.showinfo("Export Complete", msg)
        else:
            messagebox.showerror("Export Error", msg)


if __name__ == "__main__":
    app_root = tk.Tk()
    BookstoreApp(app_root)
    app_root.mainloop()
