import tkinter as tk
from tkinter import ttk
from theme import *


def styled_button(parent, text, command, color=ACCENT, fg=TEXT_DARK, width=None):
    kw = dict(bg=color, fg=fg, font=FONT_BUTTON, relief="flat", cursor="hand2",
              activebackground=ACCENT2, activeforeground=TEXT_WHITE, padx=12, pady=5)
    if width:
        kw["width"] = width
    return tk.Button(parent, text=text, command=command, **kw)

def danger_button(parent, text, command, width=None):
    return styled_button(parent, text, command, color=DANGER, fg=TEXT_WHITE, width=width)

def label(parent, text, font=FONT_BODY, fg=TEXT_WHITE, bg=None, **kw):
    try:
        bg = bg or parent.cget("bg")
    except Exception:
        bg = BG_CARD
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kw)

def card_frame(parent, **kw):
    return tk.Frame(parent, bg=BG_CARD, relief="flat", **kw)

def section_title(parent, text, bg=BG_CARD):
    f = tk.Frame(parent, bg=bg)
    tk.Label(f, text=text, font=FONT_HEADING, fg=ACCENT, bg=bg).pack(side="left")
    tk.Frame(f, bg=ACCENT, height=2).pack(side="left", fill="x", expand=True, padx=10, pady=8)
    return f

def entry_row(parent, label_text, bg=BG_CARD, width=28):
    f = tk.Frame(parent, bg=bg)
    tk.Label(f, text=label_text, font=FONT_BODY, fg=TEXT_MUTED,
             bg=bg, width=22, anchor="w").pack(side="left")
    var = tk.StringVar()
    e = tk.Entry(f, textvariable=var, font=FONT_BODY,
                 bg=BG_DARK, fg=TEXT_WHITE, insertbackground=TEXT_WHITE,
                 relief="flat", width=width,
                 highlightthickness=1, highlightcolor=ACCENT,
                 highlightbackground=BORDER)
    e.pack(side="left", padx=(4, 0))
    return f, var, e

def combo_row(parent, label_text, values, bg=BG_CARD, width=26):
    f = tk.Frame(parent, bg=bg)
    tk.Label(f, text=label_text, font=FONT_BODY, fg=TEXT_MUTED,
             bg=bg, width=22, anchor="w").pack(side="left")
    var = tk.StringVar(value=values[0] if values else "")
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.TCombobox",
                    fieldbackground=BG_DARK, background=BG_DARK,
                    foreground=TEXT_WHITE, selectbackground=ACCENT,
                    selectforeground=TEXT_DARK, arrowcolor=ACCENT)
    cb = ttk.Combobox(f, textvariable=var, values=values,
                      font=FONT_BODY, width=width,
                      style="Dark.TCombobox", state="readonly")
    cb.pack(side="left", padx=(4, 0))
    return f, var, cb

def build_treeview(parent, columns, headings, col_widths, height=14):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.Treeview",
                    background=BG_CARD, foreground=TEXT_WHITE,
                    fieldbackground=BG_CARD, rowheight=ROW_H, font=FONT_BODY)
    style.configure("Dark.Treeview.Heading",
                    background=BG_SIDEBAR, foreground=ACCENT,
                    font=FONT_BODY_B, relief="flat")
    style.map("Dark.Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", TEXT_DARK)])
    frame = tk.Frame(parent, bg=BG_DARK)
    tree  = ttk.Treeview(frame, columns=columns, show="headings",
                         height=height, style="Dark.Treeview")
    for col, head, w in zip(columns, headings, col_widths):
        tree.heading(col, text=head)
        tree.column(col, width=w, anchor="center")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    return frame, tree

def stat_card(parent, title_fr, title_ar, value, color=ACCENT):
    f = tk.Frame(parent, bg=BG_CARD, padx=20, pady=14,
                 highlightthickness=1, highlightbackground=color)
    tk.Label(f, text=title_fr, font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD).pack()
    tk.Label(f, text=title_ar, font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD).pack()
    tk.Label(f, text=str(value), font=("Georgia", 26, "bold"), fg=color, bg=BG_CARD).pack()
    return f

def separator(parent, bg=BORDER):
    return tk.Frame(parent, bg=bg, height=1)

def scrollable_frame(parent, bg=BG_CARD):
    container = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(container, bg=bg, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return container, inner