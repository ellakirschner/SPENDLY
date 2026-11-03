
import csv
import json
import math
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# =====================================================
# SPENDLY - PINK PERSONAL FINANCE DASHBOARD
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_NAME = os.path.join(BASE_DIR, "expenses.csv")
SETTINGS_FILE = os.path.join(BASE_DIR, "spendly_settings.json")
SAVINGS_FILE = os.path.join(BASE_DIR, "savings_contributions.csv")

HEADERS = ["Date", "Category", "Amount", "Description"]
SAVINGS_HEADERS = ["Date", "Amount", "Description"]

BG = "#FFF7FB"
WHITE = "#FFFFFF"
PINK = "#E76AA3"
DARK_PINK = "#C74480"
PALE_PINK = "#FCE4EF"
SOFT_PINK = "#F8BBD5"
TEXT = "#463442"
MUTED = "#987F91"
GREEN = "#438A70"
RED = "#C94D70"
BORDER = "#F2D9E6"
PURPLE = "#AA91D4"

# Six coordinated colour palettes. The chosen theme is saved in settings JSON.
THEMES = {
    "Strawberry Milk": dict(BG="#FFF7FB", WHITE="#FFFFFF", PINK="#E76AA3", DARK_PINK="#C74480", PALE_PINK="#FCE4EF", SOFT_PINK="#F8BBD5", TEXT="#463442", MUTED="#987F91", BORDER="#F2D9E6"),
    "Lavender Dream": dict(BG="#FAF7FF", WHITE="#FFFFFF", PINK="#A58ADD", DARK_PINK="#7955B7", PALE_PINK="#EDE4FB", SOFT_PINK="#D7C6F2", TEXT="#40364F", MUTED="#82738F", BORDER="#E4D9F1"),
    "Matcha Latte": dict(BG="#F7FBF6", WHITE="#FFFFFF", PINK="#84A88A", DARK_PINK="#54795D", PALE_PINK="#E3F0E3", SOFT_PINK="#C9E1CC", TEXT="#304638", MUTED="#708478", BORDER="#D7E7D9"),
    "Baby Blue": dict(BG="#F6FAFF", WHITE="#FFFFFF", PINK="#7CAAD9", DARK_PINK="#4C7EBA", PALE_PINK="#E3F0FC", SOFT_PINK="#C5DDF5", TEXT="#34475A", MUTED="#7B90A3", BORDER="#D8E7F6"),
    "Peach Sorbet": dict(BG="#FFF9F5", WHITE="#FFFFFF", PINK="#E7A17D", DARK_PINK="#B86642", PALE_PINK="#FBE9DF", SOFT_PINK="#F4D1BD", TEXT="#533E34", MUTED="#987D70", BORDER="#F2DFD3"),
    "Midnight": dict(BG="#222231", WHITE="#35334C", PINK="#8D7CCB", DARK_PINK="#BDA9FF", PALE_PINK="#45415E", SOFT_PINK="#5B527B", TEXT="#F4F0FF", MUTED="#C3BCD4", BORDER="#55506A"),
}


def apply_theme(theme_name):
    """Update colours used when constructing Tkinter widgets."""
    global BG, WHITE, PINK, DARK_PINK, PALE_PINK, SOFT_PINK, TEXT, MUTED, BORDER
    palette = THEMES.get(theme_name, THEMES["Strawberry Milk"])
    for name, value in palette.items():
        globals()[name] = value


DEFAULT_SETTINGS = {
    "monthly_limit": 0.0,
    "savings_goal": 0.0,
    "current_savings": 0.0,
    "theme": "Strawberry Milk"
}

CHART_COLORS = [
    "#E76AA3", "#AA91D4", "#F4B183",
    "#75B8A5", "#F09AA9", "#8BA8E0",
    "#D6A6D9", "#E8C66A"
]

CONFETTI_COLORS = [
    "#E76AA3", "#AA91D4", "#F4B183",
    "#75B8A5", "#F09AA9", "#8BA8E0",
    "#F8BBD5", "#E8C66A"
]


# =====================================================
# DATA FUNCTIONS
# =====================================================

def initialize_file():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(HEADERS)


def initialize_savings_file():
    if not os.path.exists(SAVINGS_FILE):
        with open(SAVINGS_FILE, "w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(SAVINGS_HEADERS)


def load_settings():
    settings = DEFAULT_SETTINGS.copy()

    if not os.path.exists(SETTINGS_FILE):
        return settings

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            saved = json.load(file)

        if isinstance(saved, dict):
            settings.update(saved)

        for key in ("monthly_limit", "savings_goal", "current_savings"):
            settings[key] = float(settings[key])
        if settings.get("theme") not in THEMES:
            settings["theme"] = "Strawberry Milk"

        return settings

    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        messagebox.showwarning(
            "Settings",
            "Settings could not be read. Default values will be used. "
            "Your original settings file has not been deleted."
        )
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def read_expenses():
    expenses = []

    if not os.path.exists(FILE_NAME):
        return expenses

    with open(FILE_NAME, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            try:
                category = (row.get("Category") or "").strip()
                amount = float(row.get("Amount", ""))

                if not category or not math.isfinite(amount):
                    continue

                expenses.append({
                    "Date": row.get("Date", ""),
                    "Category": category,
                    "Amount": amount,
                    "Description": row.get("Description", "")
                })

            except (ValueError, TypeError):
                continue

    return expenses


def read_savings_contributions():
    contributions = []

    if not os.path.exists(SAVINGS_FILE):
        return contributions

    with open(
        SAVINGS_FILE, "r", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            try:
                amount = float(row.get("Amount", ""))

                if not math.isfinite(amount) or amount <= 0:
                    continue

                contributions.append({
                    "Date": row.get("Date", ""),
                    "Amount": amount,
                    "Description": row.get("Description", "")
                })

            except (ValueError, TypeError):
                continue

    return contributions


def get_monthly_spending():
    month = datetime.now().strftime("%Y-%m")

    return sum(
        expense["Amount"]
        for expense in read_expenses()
        if expense["Date"].startswith(month)
    )


# =====================================================
# APPLICATION
# =====================================================

class SpendlyApp:

    def __init__(self, root):
        self.root = root
        self.settings = load_settings()
        apply_theme(self.settings.get("theme", "Strawberry Milk"))
        self.current_page = "Dashboard"
        self.last_alert_month = None
        self.last_alert_level = 0
        self.confetti_running = False
        self.confetti_particles = []

        self.root.title("Spendly ✨ | Your money, simplified")
        self.root.geometry("1200x780")
        self.root.minsize(900, 650)
        self.root.configure(bg=BG)

        self.setup_styles()
        initialize_file()
        initialize_savings_file()
        self.build_layout()
        self.show_page("Dashboard")
        self.refresh_all()

    # -------------------------------------------------
    # STYLES
    # -------------------------------------------------

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Pink.Horizontal.TProgressbar",
            troughcolor=PALE_PINK,
            background=PINK,
            thickness=14,
            borderwidth=0
        )

        style.configure(
            "TEntry", fieldbackground=WHITE, foreground=TEXT,
            bordercolor=BORDER, insertcolor=TEXT
        )
        style.configure(
            "TCombobox", fieldbackground=WHITE, foreground=TEXT,
            background=WHITE
        )

        style.configure(
            "Spendly.Treeview",
            background=WHITE,
            fieldbackground=WHITE,
            foreground=TEXT,
            rowheight=34,
            borderwidth=0,
            font=("Helvetica", 10)
        )

        style.configure(
            "Spendly.Treeview.Heading",
            background=PALE_PINK,
            foreground=TEXT,
            font=("Helvetica", 10, "bold"),
            padding=9,
            relief="flat"
        )

        style.map(
            "Spendly.Treeview",
            background=[("selected", PALE_PINK)],
            foreground=[("selected", TEXT)]
        )

    def label(self, parent, text, size=11, color=None, bold=False):
        return tk.Label(
            parent,
            text=text,
            bg=parent.cget("bg"),
            fg=TEXT if color is None else color,
            font=("Helvetica", size, "bold" if bold else "normal"),
            anchor="w"
        )

    def card(self, parent, padding=18):
        return tk.Frame(
            parent,
            bg=WHITE,
            padx=padding,
            pady=padding,
            highlightbackground=BORDER,
            highlightthickness=1
        )

    def button(self, parent, text, command, primary=True):
        # A clickable label keeps the pink styling on macOS,
        # where native Tk buttons may ignore background colours.
        bg = PINK if primary else PALE_PINK
        fg = "#FFFFFF" if primary else DARK_PINK
        hover = DARK_PINK if primary else SOFT_PINK
        widget = tk.Label(
            parent, text=text, bg=bg, fg=fg,
            font=("Helvetica", 10, "bold"),
            padx=18, pady=12, cursor="hand2",
            takefocus=1
        )
        widget.bind("<Button-1>", lambda event: command())
        widget.bind("<Return>", lambda event: command())
        widget.bind("<space>", lambda event: command())
        widget.bind("<Enter>", lambda event: widget.configure(bg=hover))
        widget.bind("<Leave>", lambda event: widget.configure(bg=bg))
        return widget

    # -------------------------------------------------
    # MAIN LAYOUT AND SIDEBAR
    # -------------------------------------------------

    def build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=WHITE, width=215)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="Spendly ✨",
            bg=WHITE,
            fg=DARK_PINK,
            font=("Helvetica", 25, "bold")
        ).pack(anchor="w", padx=22, pady=(28, 0))

        tk.Label(
            self.sidebar,
            text="YOUR MONEY, SIMPLIFIED",
            bg=WHITE,
            fg=MUTED,
            font=("Helvetica", 8, "bold")
        ).pack(anchor="w", padx=23, pady=(3, 28))

        self.nav_buttons = {}

        for name, symbol in [
            ("Dashboard", "⌂"),
            ("Expenses", "↗"),
            ("Add Expense", "+"),
            ("Budget & Savings", "$"),
            ("Customise", "✦")
        ]:
            # A Label is used for sidebar navigation because native macOS
            # Tk buttons can ignore foreground/background theme colours.
            btn = tk.Label(
                self.sidebar,
                text=f"  {symbol}   {name}",
                anchor="w",
                bg=WHITE,
                fg=TEXT,
                padx=18,
                pady=13,
                cursor="hand2",
                font=("Helvetica", 11)
            )
            btn.bind("<Button-1>", lambda event, page=name: self.show_page(page))
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[name] = btn

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(
            fill="x", padx=18, pady=18
        )

        tk.Label(
            self.sidebar,
            text="A little progress adds up.",
            bg=WHITE,
            fg=MUTED,
            wraplength=165,
            justify="left",
            font=("Helvetica", 10, "italic")
        ).pack(anchor="w", padx=23)

        self.sidebar_spending = tk.StringVar(value="$0.00")

        tk.Label(
            self.sidebar,
            text="SPENT THIS MONTH",
            bg=WHITE,
            fg=MUTED,
            font=("Helvetica", 8, "bold")
        ).pack(anchor="w", padx=23, pady=(30, 4))

        tk.Label(
            self.sidebar,
            textvariable=self.sidebar_spending,
            bg=WHITE,
            fg=DARK_PINK,
            font=("Helvetica", 19, "bold")
        ).pack(anchor="w", padx=23)

        self.main_area = tk.Frame(self.root, bg=BG)
        self.main_area.pack(side="left", fill="both", expand=True)

        self.topbar = tk.Frame(self.main_area, bg=BG)
        self.topbar.pack(fill="x", padx=30, pady=(22, 12))

        self.page_title = tk.Label(
            self.topbar,
            text="Dashboard",
            bg=BG,
            fg=TEXT,
            font=("Helvetica", 22, "bold")
        )
        self.page_title.pack(side="left")

        self.today_label = tk.Label(
            self.topbar,
            text=datetime.now().strftime("%A, %d %B %Y"),
            bg=BG,
            fg=MUTED,
            font=("Helvetica", 10)
        )
        self.today_label.pack(side="right", pady=8)

        self.content = tk.Frame(self.main_area, bg=BG)
        self.content.pack(fill="both", expand=True, padx=26, pady=(0, 24))

        self.pages = {
            "Dashboard": self.build_dashboard,
            "Expenses": self.build_expenses_page,
            "Add Expense": self.build_add_page,
            "Budget & Savings": self.build_budget_page,
            "Customise": self.build_customise_page
        }

    def show_page(self, name):
        self.current_page = name

        for widget in self.content.winfo_children():
            widget.destroy()

        self.page_title.config(text=name)

        for page_name, btn in self.nav_buttons.items():
            active = page_name == name
            btn.config(
                bg=PALE_PINK if active else WHITE,
                fg=(TEXT if self.settings.get("theme") == "Midnight" else DARK_PINK) if active else TEXT,
                font=("Helvetica", 11, "bold" if active else "normal")
            )

        self.pages[name]()
        self.refresh_all()

    # -------------------------------------------------
    # REUSABLE SUMMARY CARDS
    # -------------------------------------------------

    def summary_card(self, parent, title, variable, note, column):
        parent.grid_columnconfigure(column, weight=1)

        frame = self.card(parent, 16)
        frame.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=6,
            pady=5
        )

        self.label(frame, title.upper(), 9, MUTED, True).pack(anchor="w")

        tk.Label(
            frame,
            textvariable=variable,
            bg=WHITE,
            fg=DARK_PINK,
            font=("Helvetica", 20, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(12, 5))

        self.label(frame, note, 9, MUTED).pack(anchor="w")

    # -------------------------------------------------
    # DASHBOARD
    # -------------------------------------------------

    def build_dashboard(self):
        frame = self.content

        self.label(frame, "Welcome back ✨", 17, TEXT, True).pack(
            anchor="w", pady=(0, 3)
        )

        self.label(
            frame,
            "Here's how your money is looking this month.",
            10,
            MUTED
        ).pack(anchor="w", pady=(0, 14))

        self.spent_var = tk.StringVar(value="$0.00")
        self.remaining_var = tk.StringVar(value="No limit set")
        self.savings_var = tk.StringVar(value="$0.00")

        cards = tk.Frame(frame, bg=BG)
        cards.pack(fill="x", pady=(0, 12))

        self.summary_card(
            cards, "Monthly spending", self.spent_var,
            "Recorded this calendar month", 0
        )
        self.summary_card(
            cards, "Budget remaining", self.remaining_var,
            "After this month's expenses", 1
        )
        self.summary_card(
            cards, "Current savings", self.savings_var,
            "Your savings balance", 2
        )

        lower = tk.Frame(frame, bg=BG)
        lower.pack(fill="both", expand=True)

        left = tk.Frame(lower, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 7))

        right = tk.Frame(lower, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(7, 0))

        budget_card = self.card(left, 17)
        budget_card.pack(fill="x", pady=(0, 12))

        self.label(
            budget_card, "Monthly budget", 13, TEXT, True
        ).pack(anchor="w")

        self.budget_text = tk.StringVar(value="Set a budget to get started.")
        tk.Label(
            budget_card,
            textvariable=self.budget_text,
            bg=WHITE,
            fg=MUTED,
            font=("Helvetica", 10),
            justify="left",
            wraplength=380
        ).pack(anchor="w", pady=(8, 12))

        self.budget_progress = ttk.Progressbar(
            budget_card,
            style="Pink.Horizontal.TProgressbar",
            maximum=100
        )
        self.budget_progress.pack(fill="x")

        savings_card = self.card(left, 17)
        savings_card.pack(fill="x", pady=(0, 12))

        self.label(
            savings_card, "Savings goal ✨", 13, TEXT, True
        ).pack(anchor="w")

        self.savings_text = tk.StringVar(value="Set a savings goal.")
        tk.Label(
            savings_card,
            textvariable=self.savings_text,
            bg=WHITE,
            fg=MUTED,
            font=("Helvetica", 10),
            justify="left",
            wraplength=380
        ).pack(anchor="w", pady=(8, 12))

        self.savings_progress = ttk.Progressbar(
            savings_card,
            style="Pink.Horizontal.TProgressbar",
            maximum=100
        )
        self.savings_progress.pack(fill="x")

        chart_card = self.card(right, 15)
        chart_card.pack(fill="both", expand=True, pady=(0, 12))

        self.label(
            chart_card, "Spending by category", 13, TEXT, True
        ).pack(anchor="w")

        self.chart = tk.Canvas(
            chart_card,
            bg=WHITE,
            highlightthickness=0,
            height=230
        )
        self.chart.pack(fill="both", expand=True, pady=(8, 0))

        self.chart.bind(
            "<Configure>",
            lambda event: self.draw_category_chart()
        )

        buttons = tk.Frame(frame, bg=BG)
        buttons.pack(fill="x", pady=(0, 4))

        self.button(
            buttons, "+ Add expense",
            lambda: self.show_page("Add Expense")
        ).pack(side="left", padx=(0, 8))

        self.button(
            buttons, "View expenses",
            lambda: self.show_page("Expenses"),
            primary=False
        ).pack(side="left")

        self.button(
            buttons, "Reset totals",
            self.reset_totals,
            primary=False
        ).pack(side="right")

    # -------------------------------------------------
    # ADD EXPENSE PAGE
    # -------------------------------------------------

    def build_add_page(self):
        frame = self.content

        self.label(frame, "Add a purchase ✨", 17, TEXT, True).pack(
            anchor="w", pady=(0, 5)
        )

        self.label(
            frame,
            "Record your spending to keep your budget up to date.",
            10,
            MUTED
        ).pack(anchor="w", pady=(0, 18))

        form = self.card(frame, 24)
        form.pack(fill="x", anchor="n")

        self.category_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.description_var = tk.StringVar()

        fields = [
            ("Category", ttk.Combobox(
                form,
                textvariable=self.category_var,
                values=[
                    "Food", "Shopping", "Travel", "Transport",
                    "Beauty", "Entertainment", "Bills", "Health",
                    "Education", "Other"
                ],
                font=("Helvetica", 11)
            )),
            ("Amount ($)", ttk.Entry(
                form, textvariable=self.amount_var,
                font=("Helvetica", 11)
            )),
            ("Description", ttk.Entry(
                form, textvariable=self.description_var,
                font=("Helvetica", 11)
            ))
        ]

        for row, (title, widget) in enumerate(fields):
            tk.Label(
                form,
                text=title,
                bg=WHITE,
                fg=TEXT,
                font=("Helvetica", 10, "bold")
            ).grid(row=row, column=0, sticky="w", pady=12, padx=(0, 22))

            widget.grid(row=row, column=1, sticky="ew", pady=12)

        form.columnconfigure(1, weight=1)

        self.button(
            form, "Save expense ✨", self.add_expense
        ).grid(row=3, column=1, sticky="w", pady=(18, 0))

        tk.Label(
            frame,
            text="Your expense will be saved to expenses.csv.",
            bg=BG,
            fg=MUTED,
            font=("Helvetica", 9)
        ).pack(anchor="w", pady=14)

    def add_expense(self):
        category = self.category_var.get().strip()
        description = self.description_var.get().strip()

        if not category:
            messagebox.showerror("Missing category", "Please enter a category.")
            return

        try:
            amount = float(self.amount_var.get().strip())

            if not math.isfinite(amount) or amount <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid amount",
                "Enter a valid amount greater than $0."
            )
            return

        previous = get_monthly_spending()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with open(FILE_NAME, "a", newline="", encoding="utf-8") as file:
                csv.writer(file).writerow(
                    [date, category, amount, description]
                )
        except OSError as error:
            messagebox.showerror("Could not save expense", str(error))
            return

        self.refresh_all()

        current = get_monthly_spending()
        limit = self.settings["monthly_limit"]

        if limit > 0:
            if previous < limit <= current:
                messagebox.showwarning(
                    "Budget reached!",
                    f"You've reached your ${limit:.2f} monthly limit.\n\n"
                    f"Total spent this month: ${current:.2f}"
                )
            elif previous < limit * 0.8 <= current < limit:
                messagebox.showwarning(
                    "Budget alert ✨",
                    f"You've used at least 80% of your budget.\n\n"
                    f"Spent: ${current:.2f}\n"
                    f"Limit: ${limit:.2f}"
                )
            elif current > limit and previous >= limit:
                messagebox.showwarning(
                    "Over budget!",
                    f"You're now ${current - limit:.2f} over budget."
                )

        messagebox.showinfo(
            "Expense saved ✨",
            f"${amount:.2f} added to {category}."
        )

        self.show_page("Dashboard")

    # -------------------------------------------------
    # EXPENSES PAGE
    # -------------------------------------------------

    def build_expenses_page(self):
        frame = self.content

        self.label(frame, "Your transactions", 17, TEXT, True).pack(
            anchor="w", pady=(0, 4)
        )

        self.label(
            frame,
            "Your recorded expenses and category breakdown.",
            10,
            MUTED
        ).pack(anchor="w", pady=(0, 14))

        table_card = self.card(frame, 12)
        table_card.pack(fill="both", expand=True)

        columns = ("Date", "Category", "Amount", "Description")

        self.tree = ttk.Treeview(
            table_card,
            columns=columns,
            show="headings",
            style="Spendly.Treeview"
        )

        widths = {
            "Date": 155,
            "Category": 110,
            "Amount": 100,
            "Description": 250
        }

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(
                column,
                width=widths[column],
                minwidth=70,
                anchor="w"
            )

        scrollbar = ttk.Scrollbar(
            table_card,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        totals_card = self.card(frame, 16)
        totals_card.pack(fill="x", pady=(12, 0))

        self.label(
            totals_card, "Totals by category", 12, TEXT, True
        ).pack(anchor="w")

        self.category_totals = tk.StringVar(
            value="No expenses recorded yet."
        )

        tk.Label(
            totals_card,
            textvariable=self.category_totals,
            bg=WHITE,
            fg=MUTED,
            justify="left",
            anchor="w",
            font=("Helvetica", 10),
            wraplength=850
        ).pack(fill="x", pady=(8, 0))

        buttons = tk.Frame(frame, bg=BG)
        buttons.pack(fill="x", pady=(12, 0))

        self.button(
            buttons, "+ Add expense",
            lambda: self.show_page("Add Expense")
        ).pack(side="left")

        self.button(
            buttons, "Reset totals",
            self.reset_totals, primary=False
        ).pack(side="right")

    # -------------------------------------------------
    # CUSTOMISE PAGE
    # -------------------------------------------------

    def build_customise_page(self):
        frame = self.content
        self.label(frame, "Make Spendly yours ✨", 18, TEXT, True).pack(
            anchor="w", pady=(0, 5))
        self.label(frame, "Choose a colour palette. Your choice is saved automatically.",
                   10, MUTED).pack(anchor="w", pady=(0, 16))

        panel = self.card(frame, 20)
        panel.pack(fill="x")
        self.label(panel, "COLOUR THEMES", 10, MUTED, True).pack(
            anchor="w", pady=(0, 12))

        theme_grid = tk.Frame(panel, bg=WHITE)
        theme_grid.pack(fill="x")
        self.theme_tiles = {}
        selected = self.settings.get("theme", "Strawberry Milk")

        for index, (name, palette) in enumerate(THEMES.items()):
            row, col = divmod(index, 3)
            theme_grid.columnconfigure(col, weight=1)
            tile = tk.Frame(theme_grid, bg=WHITE,
                            highlightthickness=2 if name == selected else 1,
                            highlightbackground=PINK if name == selected else BORDER,
                            padx=12, pady=12, cursor="hand2")
            tile.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
            swatches = tk.Frame(tile, bg=WHITE)
            swatches.pack(anchor="w", pady=(0, 9))
            for key in ("PINK", "DARK_PINK", "PALE_PINK", "BG"):
                tk.Frame(swatches, bg=palette[key], width=24, height=24,
                         highlightthickness=1, highlightbackground=BORDER).pack(
                    side="left", padx=(0, 5))
            title = tk.Label(tile, text=name + ("  ✓" if name == selected else ""),
                             bg=WHITE, fg=TEXT, font=("Helvetica", 11, "bold"),
                             cursor="hand2")
            title.pack(anchor="w")
            for widget in (tile, title, swatches):
                widget.bind("<Button-1>", lambda event, choice=name: self.change_theme(choice))
            for widget in swatches.winfo_children():
                widget.bind("<Button-1>", lambda event, choice=name: self.change_theme(choice))
            self.theme_tiles[name] = tile

        self.label(frame, "Changes apply to the whole app immediately, including your charts and buttons.",
                   10, MUTED).pack(anchor="w", pady=(16, 0))
        self.label(frame, "Your expenses, savings balance, and history are not affected.",
                   10, MUTED).pack(anchor="w", pady=(4, 0))

    def change_theme(self, name):
        if name not in THEMES or name == self.settings.get("theme"):
            return
        updated = self.settings.copy()
        updated["theme"] = name
        try:
            save_settings(updated)
        except OSError as error:
            messagebox.showerror("Could not save theme", str(error))
            return
        self.settings = updated
        apply_theme(name)
        self.root.configure(bg=BG)
        self.setup_styles()
        # Rebuild the widgets to ensure every background, chart and button updates.
        for widget in self.root.winfo_children():
            widget.destroy()
        self.build_layout()
        self.show_page("Customise")

    # -------------------------------------------------
    # BUDGET & SAVINGS PAGE
    # -------------------------------------------------

    def build_budget_page(self):
        frame = self.content

        self.label(frame, "Your money goals ✨", 17, TEXT, True).pack(
            anchor="w", pady=(0, 5)
        )

        self.label(
            frame,
            "Set your budget, track deposits and celebrate your progress.",
            10,
            MUTED
        ).pack(anchor="w", pady=(0, 12))

        # Budget settings
        form = self.card(frame, 18)
        form.pack(fill="x", anchor="n")

        self.limit_var = tk.StringVar()
        self.goal_var = tk.StringVar()
        self.current_savings_var = tk.StringVar()

        fields = [
            ("Monthly spending limit ($)", self.limit_var),
            ("Savings goal ($)", self.goal_var),
            ("Current savings ($)", self.current_savings_var)
        ]

        for row, (title, variable) in enumerate(fields):
            tk.Label(
                form,
                text=title,
                bg=WHITE,
                fg=TEXT,
                font=("Helvetica", 10, "bold")
            ).grid(row=row, column=0, sticky="w", pady=7, padx=(0, 22))

            ttk.Entry(
                form,
                textvariable=variable,
                font=("Helvetica", 11)
            ).grid(row=row, column=1, sticky="ew", pady=7)

        form.columnconfigure(1, weight=1)

        goal_buttons = tk.Frame(form, bg=WHITE)
        goal_buttons.grid(row=3, column=1, sticky="w", pady=(12, 0))

        self.button(
            goal_buttons, "Save my goals ✨", self.save_budget
        ).pack(side="left", padx=(0, 10))

        self.button(
            goal_buttons, "Reset savings balance", self.reset_savings_balance,
            primary=False
        ).pack(side="left")

        # Add a savings contribution
        contribution_card = self.card(frame, 18)
        contribution_card.pack(fill="x", pady=(12, 0))

        self.label(
            contribution_card, "Add to your savings ✨", 13, TEXT, True
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        self.contribution_amount_var = tk.StringVar()
        self.contribution_description_var = tk.StringVar()

        contribution_fields = [
            ("Contribution amount ($)", self.contribution_amount_var),
            ("Description (optional)", self.contribution_description_var)
        ]

        for row, (title, variable) in enumerate(contribution_fields, start=1):
            tk.Label(
                contribution_card,
                text=title,
                bg=WHITE,
                fg=TEXT,
                font=("Helvetica", 10, "bold")
            ).grid(
                row=row, column=0, sticky="w",
                pady=6, padx=(0, 18)
            )

            ttk.Entry(
                contribution_card,
                textvariable=variable,
                font=("Helvetica", 11)
            ).grid(row=row, column=1, sticky="ew", pady=6)

        contribution_card.columnconfigure(1, weight=1)

        self.button(
            contribution_card,
            "Add savings contribution ✨",
            self.add_savings_contribution
        ).grid(row=3, column=1, sticky="w", pady=(14, 4))

        # Contribution history
        history_card = self.card(frame, 12)
        history_card.pack(fill="both", expand=True, pady=(12, 0))

        # Keep the reset button in the history header so it is always easy to find.
        history_header = tk.Frame(history_card, bg=WHITE)
        history_header.pack(fill="x", pady=(0, 10))

        self.label(
            history_header, "Savings contribution history", 12, TEXT, True
        ).pack(side="left", anchor="w", pady=8)

        self.button(
            history_header,
            "Reset contribution history",
            self.reset_savings_history,
            primary=False
        ).pack(side="right", padx=(12, 0))

        columns = ("Date", "Amount", "Description")

        self.savings_tree = ttk.Treeview(
            history_card,
            columns=columns,
            show="headings",
            style="Spendly.Treeview",
            height=4
        )

        widths = {
            "Date": 165,
            "Amount": 110,
            "Description": 350
        }

        for column in columns:
            self.savings_tree.heading(column, text=column)
            self.savings_tree.column(
                column,
                width=widths[column],
                minwidth=75,
                anchor="w"
            )

        self.savings_tree.pack(
            fill="both", expand=True, pady=(0, 6)
        )

        self.savings_history_total = tk.StringVar(value="Total contributed: $0.00")

        tk.Label(
            history_card,
            textvariable=self.savings_history_total,
            bg=WHITE,
            fg=DARK_PINK,
            font=("Helvetica", 10, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(4, 0))

        tk.Label(
            frame,
            text=(
                "Contributions are added to your current savings balance "
                "and recorded separately in savings_contributions.csv."
            ),
            bg=BG,
            fg=MUTED,
            font=("Helvetica", 9),
            wraplength=800,
            justify="left"
        ).pack(anchor="w", pady=(8, 0))

    def save_budget(self):
        try:
            limit = float(self.limit_var.get().strip())
            goal = float(self.goal_var.get().strip())
            savings = float(self.current_savings_var.get().strip())

            values = (limit, goal, savings)

            if any(not math.isfinite(value) or value < 0 for value in values):
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Check your numbers",
                "Enter valid, non-negative amounts in all three fields."
            )
            return

        self.settings["monthly_limit"] = limit
        self.settings["savings_goal"] = goal
        self.settings["current_savings"] = savings

        try:
            save_settings(self.settings)
        except OSError as error:
            messagebox.showerror("Could not save settings", str(error))
            return

        self.refresh_all()

        if goal > 0 and savings >= goal:
            messagebox.showinfo(
                "Savings goal achieved! ✨",
                f"You've saved ${savings:.2f} towards your "
                f"${goal:.2f} goal. Congratulations!"
            )
        else:
            messagebox.showinfo(
                "Goals saved ✨",
                "Your budget and savings settings have been saved."
            )

    # -------------------------------------------------
    # SAVINGS CONTRIBUTIONS
    # -------------------------------------------------

    def add_savings_contribution(self):
        try:
            amount = float(self.contribution_amount_var.get().strip())

            if not math.isfinite(amount) or amount <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid contribution",
                "Enter a valid savings contribution greater than $0."
            )
            return

        description = self.contribution_description_var.get().strip()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_balance = self.settings["current_savings"] + amount
        updated_settings = self.settings.copy()
        updated_settings["current_savings"] = new_balance

        # Save the contribution record first.
        try:
            initialize_savings_file()

            with open(
                SAVINGS_FILE, "a", newline="", encoding="utf-8"
            ) as file:
                csv.writer(file).writerow([date, amount, description])

        except OSError as error:
            messagebox.showerror(
                "Could not save contribution",
                f"Your contribution could not be recorded.\n\n{error}"
            )
            return

        # Update the current savings balance.
        try:
            save_settings(updated_settings)
        except OSError as error:
            messagebox.showerror(
                "Settings could not be saved",
                "The contribution was recorded, but your savings balance "
                "could not be updated automatically.\n\n"
                f"Please check your settings file.\n\n{error}"
            )
            self.refresh_all()
            return

        self.settings = updated_settings
        self.contribution_amount_var.set("")
        self.contribution_description_var.set("")

        self.refresh_all()

        goal = self.settings["savings_goal"]

        if goal > 0 and new_balance >= goal:
            messagebox.showinfo(
                "You did it! 🎉",
                f"You've reached your savings goal!\n\n"
                f"Your savings balance is ${new_balance:,.2f}."
            )
        else:
            messagebox.showinfo(
                "Savings added ✨",
                f"${amount:,.2f} has been added to your savings!\n\n"
                f"New balance: ${new_balance:,.2f}"
            )


        # The popup above is modal; start the animation once dismissed.
        self.root.after(150, self.show_confetti)

    # -------------------------------------------------
    # CONFETTI ANIMATION
    # -------------------------------------------------

    def show_confetti(self):
        """Display a separate, visible celebration window with falling confetti."""
        if self.confetti_running:
            return
        self.confetti_running = True
        self.root.update_idletasks()

        # A separate window is more dependable than placing an overlay
        # inside a complex Tkinter layout on macOS.
        width = max(550, self.root.winfo_width())
        height = max(450, self.root.winfo_height())
        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        popup = tk.Toplevel(self.root)
        popup.title("Spendly savings celebration ✨")
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.configure(bg=BG)
        popup.transient(self.root)
        popup.lift()
        popup.attributes("-topmost", True)
        popup.after(250, lambda: popup.attributes("-topmost", False) if popup.winfo_exists() else None)

        canvas = tk.Canvas(popup, bg=BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_text(
            width / 2, height / 2 - 40,
            text="Savings added! ✨", fill=DARK_PINK,
            font=("Helvetica", 32, "bold")
        )
        canvas.create_text(
            width / 2, height / 2 + 10,
            text="You're one step closer to your goal ✨",
            fill=TEXT, font=("Helvetica", 15)
        )

        particles = []
        for _ in range(180):
            size = random.randint(6, 13)
            px = random.randint(0, width)
            # Some confetti is visible immediately, the rest falls from above.
            py = random.randint(-height, 80)
            color = random.choice(CONFETTI_COLORS)
            item = canvas.create_rectangle(
                px, py, px + size, py + size,
                fill=color, outline=""
            )
            particles.append((item, random.uniform(-2, 2), random.uniform(5, 11)))

        def close_celebration():
            self.confetti_running = False
            try:
                if popup.winfo_exists():
                    popup.destroy()
            except tk.TclError:
                pass

        popup.protocol("WM_DELETE_WINDOW", close_celebration)
        frame = 0

        def animate():
            nonlocal frame
            try:
                if not popup.winfo_exists():
                    self.confetti_running = False
                    return
                frame += 1
                for item, drift, speed in particles:
                    canvas.move(item, drift, speed)
                if frame < 120:
                    popup.after(25, animate)
                else:
                    close_celebration()
            except tk.TclError:
                self.confetti_running = False

        popup.after(25, animate)

    # -------------------------------------------------
    # RESET CURRENT SAVINGS BALANCE (KEEP HISTORY)
    # -------------------------------------------------

    def reset_savings_balance(self):
        confirmed = messagebox.askyesno(
            "Reset savings balance?",
            "This will set your current savings balance to $0.00.\n\n"
            "Your savings goal, savings contribution history, monthly budget "
            "and expenses will stay unchanged.\n\n"
            "Do you want to continue?",
            icon="warning",
            parent=self.root
        )
        if not confirmed:
            return

        updated_settings = self.settings.copy()
        updated_settings["current_savings"] = 0.0
        try:
            save_settings(updated_settings)
        except OSError as error:
            messagebox.showerror(
                "Could not reset savings balance", str(error), parent=self.root
            )
            return

        self.settings = updated_settings
        self.refresh_all()
        messagebox.showinfo(
            "Savings balance reset ✨",
            "Your current savings balance is now $0.00. "
            "Your savings goal and contribution history are unchanged.",
            parent=self.root
        )

    # -------------------------------------------------
    # RESET SAVINGS CONTRIBUTION HISTORY
    # -------------------------------------------------

    def reset_savings_history(self):
        confirmed = messagebox.askyesno(
            "Reset savings history?",
            "This will permanently delete your recorded savings contributions "
            "and reset the contribution history total to $0.00.\n\n"
            "Your current savings balance, savings goal, monthly budget "
            "and expenses will NOT be changed.\n\n"
            "Do you want to continue?",
            icon="warning",
            parent=self.root
        )
        if not confirmed:
            return

        try:
            with open(SAVINGS_FILE, "w", newline="", encoding="utf-8") as file:
                csv.writer(file).writerow(SAVINGS_HEADERS)
        except OSError as error:
            messagebox.showerror(
                "Could not reset savings history", str(error), parent=self.root
            )
            return

        self.refresh_all()
        messagebox.showinfo(
            "Savings history reset ✨",
            "Your savings contribution history has been cleared. "
            "Your current savings balance and goal are unchanged.",
            parent=self.root
        )

    # -------------------------------------------------
    # RESET EXPENSE TOTALS
    # -------------------------------------------------

    def reset_totals(self):
        confirmed = messagebox.askyesno(
            "Reset totals?",
            "This will permanently clear all recorded expenses.\n\n"
            "Your spending limit, savings goal, current savings "
            "and savings contribution history will remain unchanged.\n\n"
            "Do you want to continue?",
            icon="warning"
        )

        if not confirmed:
            return

        try:
            with open(
                FILE_NAME, "w", newline="", encoding="utf-8"
            ) as file:
                csv.writer(file).writerow(HEADERS)

        except OSError as error:
            messagebox.showerror("Could not reset expenses", str(error))
            return

        self.refresh_all()

        messagebox.showinfo(
            "Totals reset ✨",
            "Your expenses have been cleared. Your saved goals and "
            "savings contribution history remain."
        )

    # -------------------------------------------------
    # REFRESH DATA
    # -------------------------------------------------

    def refresh_all(self):
        self.settings = load_settings()

        spent = get_monthly_spending()
        limit = self.settings["monthly_limit"]
        goal = self.settings["savings_goal"]
        savings = self.settings["current_savings"]

        if hasattr(self, "sidebar_spending"):
            self.sidebar_spending.set(f"${spent:,.2f}")

        if self.current_page == "Dashboard" and hasattr(self, "spent_var") and self.budget_progress.winfo_exists():
            self.spent_var.set(f"${spent:,.2f}")

            if limit > 0:
                remaining = limit - spent

                if remaining >= 0:
                    self.remaining_var.set(f"${remaining:,.2f}")
                else:
                    self.remaining_var.set(f"-${abs(remaining):,.2f}")

                percentage = spent / limit * 100
                self.budget_progress["value"] = min(percentage, 100)

                if spent >= limit:
                    self.budget_text.set(
                        f"Over budget by ${spent - limit:,.2f}. "
                        "Consider pausing non-essential spending."
                    )
                elif percentage >= 80:
                    self.budget_text.set(
                        f"{percentage:.1f}% used. "
                        f"${remaining:,.2f} left — getting close!"
                    )
                else:
                    self.budget_text.set(
                        f"${remaining:,.2f} remaining from your "
                        f"${limit:,.2f} limit."
                    )
            else:
                self.remaining_var.set("No limit set")
                self.budget_progress["value"] = 0
                self.budget_text.set(
                    "Set a monthly spending limit in Budget & Savings."
                )

            self.savings_var.set(f"${savings:,.2f}")

            if goal > 0:
                progress = min(savings / goal * 100, 100)
                self.savings_progress["value"] = progress
                remaining = max(goal - savings, 0)

                if savings >= goal:
                    self.savings_text.set(
                        f"Goal achieved! You've saved ${savings:,.2f}. 🎉"
                    )
                else:
                    self.savings_text.set(
                        f"{progress:.1f}% complete. "
                        f"${remaining:,.2f} left to save."
                    )
            else:
                self.savings_progress["value"] = 0
                self.savings_text.set(
                    "Set a savings goal in Budget & Savings."
                )

        if self.current_page == "Budget & Savings" and hasattr(self, "limit_var"):
            self.limit_var.set(str(limit))
            self.goal_var.set(str(goal))
            self.current_savings_var.set(str(savings))

        if self.current_page == "Expenses" and hasattr(self, "tree") and self.tree.winfo_exists():
            self.refresh_expense_table()

        if self.current_page == "Budget & Savings" and hasattr(self, "savings_tree") and self.savings_tree.winfo_exists():
            self.refresh_savings_history()

        if self.current_page == "Dashboard" and hasattr(self, "chart") and self.chart.winfo_exists():
            self.root.after_idle(self.draw_category_chart)

    def refresh_expense_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        expenses = read_expenses()

        for expense in reversed(expenses):
            try:
                date_display = datetime.strptime(
                    expense["Date"], "%Y-%m-%d %H:%M:%S"
                ).strftime("%d %b %Y, %I:%M %p")
            except ValueError:
                date_display = expense["Date"]

            self.tree.insert(
                "",
                "end",
                values=(
                    date_display,
                    expense["Category"],
                    f"${expense['Amount']:.2f}",
                    expense["Description"]
                )
            )

        totals = {}

        for expense in expenses:
            category = expense["Category"]
            totals[category] = totals.get(category, 0) + expense["Amount"]

        if totals:
            lines = [
                f"{category}: ${amount:.2f}"
                for category, amount in sorted(totals.items())
            ]
            self.category_totals.set("     •     ".join(lines))
        else:
            self.category_totals.set("No expenses recorded yet.")

    def refresh_savings_history(self):
        for item in self.savings_tree.get_children():
            self.savings_tree.delete(item)

        contributions = read_savings_contributions()

        for contribution in reversed(contributions):
            try:
                date_display = datetime.strptime(
                    contribution["Date"], "%Y-%m-%d %H:%M:%S"
                ).strftime("%d %b %Y, %I:%M %p")
            except ValueError:
                date_display = contribution["Date"]

            self.savings_tree.insert(
                "",
                "end",
                values=(
                    date_display,
                    f"${contribution['Amount']:.2f}",
                    contribution["Description"]
                )
            )

        total = sum(item["Amount"] for item in contributions)

        self.savings_history_total.set(
            f"Total recorded contributions: ${total:,.2f}"
        )

    # -------------------------------------------------
    # DRAW CATEGORY DONUT CHART
    # -------------------------------------------------

    def draw_category_chart(self):
        if not hasattr(self, "chart"):
            return

        canvas = self.chart
        canvas.delete("all")

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        if width < 80 or height < 80:
            return

        month = datetime.now().strftime("%Y-%m")
        totals = {}

        for expense in read_expenses():
            if expense["Date"].startswith(month):
                category = expense["Category"]
                totals[category] = (
                    totals.get(category, 0) + expense["Amount"]
                )

        totals = {
            name: amount
            for name, amount in sorted(
                totals.items(), key=lambda item: item[1], reverse=True
            )
            if amount > 0
        }

        total = sum(totals.values())

        if total <= 0:
            canvas.create_text(
                width / 2,
                height / 2,
                text="Your category chart will appear\nwhen you add expenses ✨",
                fill=MUTED,
                font=("Helvetica", 11),
                justify="center"
            )
            return

        diameter = min(155, height - 65, width * 0.43)
        diameter = max(diameter, 80)

        x0 = 10
        y0 = max(5, (height - diameter) / 2 - 10)
        x1 = x0 + diameter
        y1 = y0 + diameter

        start = 90

        palette_colors = [PINK, "#AA91D4", "#F4B183", "#75B8A5",
                          "#F09AA9", "#8BA8E0", "#D6A6D9", "#E8C66A"]
        for index, (category, amount) in enumerate(totals.items()):
            extent = amount / total * 360

            canvas.create_arc(
                x0, y0, x1, y1,
                start=start,
                extent=-extent,
                fill=palette_colors[index % len(palette_colors)],
                outline=WHITE,
                width=2,
                style="pieslice"
            )

            start -= extent

        hole = diameter * 0.55
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2

        canvas.create_oval(
            cx - hole / 2, cy - hole / 2,
            cx + hole / 2, cy + hole / 2,
            fill=WHITE,
            outline=WHITE
        )

        canvas.create_text(
            cx, cy - 7,
            text=f"${total:,.0f}",
            fill=DARK_PINK,
            font=("Helvetica", 13, "bold")
        )

        canvas.create_text(
            cx, cy + 12,
            text="THIS MONTH",
            fill=MUTED,
            font=("Helvetica", 7, "bold")
        )

        legend_x = x1 + 14
        legend_y = max(12, y0 + 5)
        available_height = max(1, height - legend_y - 8)
        row_height = min(
            24, max(15, available_height / min(len(totals), 8))
        )

        for index, (category, amount) in enumerate(list(totals.items())[:8]):
            y = legend_y + index * row_height

            if y > height - 14:
                break

            canvas.create_oval(
                legend_x, y, legend_x + 9, y + 9,
                fill=palette_colors[index % len(palette_colors)],
                outline=""
            )

            canvas.create_text(
                legend_x + 15, y + 4,
                text=category[:13],
                anchor="w",
                fill=TEXT,
                font=("Helvetica", 8)
            )

            canvas.create_text(
                width - 5, y + 4,
                text=f"${amount:,.0f}",
                anchor="e",
                fill=MUTED,
                font=("Helvetica", 8)
            )

        if len(totals) > 8:
            canvas.create_text(
                legend_x + 15,
                height - 8,
                text=f"+ {len(totals) - 8} more categories",
                anchor="w",
                fill=MUTED,
                font=("Helvetica", 8)
            )


# =====================================================
# RUN THE APP
# =====================================================

if __name__ == "__main__":
    initialize_file()
    initialize_savings_file()

    root = tk.Tk()
    app = SpendlyApp(root)
    root.mainloop()
    