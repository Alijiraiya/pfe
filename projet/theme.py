import tkinter as tk
from tkinter import ttk

# ── PALETTES ──────────────────────────────────────────
DARK_THEME = {
    "BG_DARK":    "#0F1923",
    "BG_CARD":    "#162030",
    "BG_SIDEBAR": "#0A1219",
    "ACCENT":     "#C9A84C",
    "ACCENT2":    "#1E7F6E",
    "TEXT_WHITE": "#EEE8DC",
    "TEXT_MUTED": "#7A8899",
    "TEXT_DARK":  "#0F1923",
    "DANGER":     "#C0392B",
    "SUCCESS":    "#27AE60",
    "BORDER":     "#243040",
    "HOVER_CARD": "#1C2D40",
}

LIGHT_THEME = {
    "BG_DARK":    "#F0F2F5",
    "BG_CARD":    "#FFFFFF",
    "BG_SIDEBAR": "#DDE1E7",
    "ACCENT":     "#B8860B",
    "ACCENT2":    "#1E7F6E",
    "TEXT_WHITE": "#1A2332",
    "TEXT_MUTED": "#5D6D7E",
    "TEXT_DARK":  "#FFFFFF",
    "DANGER":     "#E74C3C",
    "SUCCESS":    "#27AE60",
    "BORDER":     "#C0C8D0",
    "HOVER_CARD": "#E8ECF0",
}

# Valeurs globales actives (sombre par défaut)
BG_DARK    = DARK_THEME["BG_DARK"]
BG_CARD    = DARK_THEME["BG_CARD"]
BG_SIDEBAR = DARK_THEME["BG_SIDEBAR"]
ACCENT     = DARK_THEME["ACCENT"]
ACCENT2    = DARK_THEME["ACCENT2"]
TEXT_WHITE = DARK_THEME["TEXT_WHITE"]
TEXT_MUTED = DARK_THEME["TEXT_MUTED"]
TEXT_DARK  = DARK_THEME["TEXT_DARK"]
DANGER     = DARK_THEME["DANGER"]
SUCCESS    = DARK_THEME["SUCCESS"]
BORDER     = DARK_THEME["BORDER"]
HOVER_CARD = DARK_THEME["HOVER_CARD"]

CURRENT_THEME = "dark"

# ── FONTS ─────────────────────────────────────────────
FONT_TITLE   = ("Georgia", 22, "bold")
FONT_HEADING = ("Georgia", 14, "bold")
FONT_BODY    = ("Helvetica", 11)
FONT_BODY_B  = ("Helvetica", 11, "bold")
FONT_SMALL   = ("Helvetica", 9)
FONT_BUTTON  = ("Helvetica", 10, "bold")
FONT_MONO    = ("Courier", 10)

# ── SIZES ─────────────────────────────────────────────
SIDEBAR_W = 230
PAD       = 16
RADIUS    = 6
BTN_H     = 36
ROW_H     = 32


def set_theme(mode):
    global BG_DARK, BG_CARD, BG_SIDEBAR, ACCENT, ACCENT2, TEXT_WHITE
    global TEXT_MUTED, TEXT_DARK, DANGER, SUCCESS, BORDER, HOVER_CARD, CURRENT_THEME
    t = LIGHT_THEME if mode == "light" else DARK_THEME
    CURRENT_THEME = mode
    BG_DARK    = t["BG_DARK"];   BG_CARD    = t["BG_CARD"]
    BG_SIDEBAR = t["BG_SIDEBAR"]; ACCENT     = t["ACCENT"]
    ACCENT2    = t["ACCENT2"];   TEXT_WHITE = t["TEXT_WHITE"]
    TEXT_MUTED = t["TEXT_MUTED"]; TEXT_DARK  = t["TEXT_DARK"]
    DANGER     = t["DANGER"];    SUCCESS    = t["SUCCESS"]
    BORDER     = t["BORDER"];    HOVER_CARD = t["HOVER_CARD"]


def apply_ttk_styles():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.TCombobox",
                    fieldbackground=BG_CARD, background=BG_CARD,
                    foreground=TEXT_WHITE,
                    selectbackground=ACCENT, selectforeground=TEXT_DARK,
                    arrowcolor=ACCENT)
    style.configure("Dark.Treeview",
                    background=BG_CARD, foreground=TEXT_WHITE,
                    fieldbackground=BG_CARD, rowheight=ROW_H, font=FONT_BODY)
    style.configure("Dark.Treeview.Heading",
                    background=BG_SIDEBAR, foreground=ACCENT,
                    font=FONT_BODY_B, relief="flat")
    style.map("Dark.Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", TEXT_DARK)])
    style.configure("D.TNotebook", background=BG_DARK, borderwidth=0)
    style.configure("D.TNotebook.Tab", background=BG_SIDEBAR,
                    foreground=TEXT_MUTED, font=FONT_BODY_B, padding=[10, 5])
    style.map("D.TNotebook.Tab",
              background=[("selected", BG_CARD)],
              foreground=[("selected", ACCENT)])
