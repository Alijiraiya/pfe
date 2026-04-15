import tkinter as tk
from tkinter import ttk
import theme as th


def styled_button(parent, text, command, color=None, fg=None, width=None):
    c = color if color else th.ACCENT
    f = fg if fg else th.TEXT_DARK
    kw = dict(bg=c, fg=f, font=th.FONT_BUTTON, relief="flat", cursor="hand2",
              activebackground=th.ACCENT2, activeforeground=th.TEXT_WHITE, padx=12, pady=5)
    if width:
        kw["width"] = width
    return tk.Button(parent, text=text, command=command, **kw)

def danger_button(parent, text, command, width=None):
    return styled_button(parent, text, command, color=th.DANGER, fg=th.TEXT_WHITE, width=width)

def label(parent, text, font=None, fg=None, bg=None, **kw):
    fnt = font if font else th.FONT_BODY
    fore = fg if fg else th.TEXT_WHITE
    try:
        back = bg or parent.cget("bg")
    except Exception:
        back = th.BG_CARD
    return tk.Label(parent, text=text, font=fnt, fg=fore, bg=back, **kw)

def card_frame(parent, **kw):
    return tk.Frame(parent, bg=th.BG_CARD, relief="flat", **kw)

def section_title(parent, text, bg=None):
    b = bg if bg else th.BG_CARD
    f = tk.Frame(parent, bg=b)
    tk.Label(f, text=text, font=th.FONT_HEADING, fg=th.ACCENT, bg=b).pack(side="left")
    tk.Frame(f, bg=th.ACCENT, height=2).pack(side="left", fill="x", expand=True, padx=10, pady=8)
    return f

def entry_row(parent, label_text, bg=None, width=28):
    b = bg if bg else th.BG_CARD
    f = tk.Frame(parent, bg=b)
    tk.Label(f, text=label_text, font=th.FONT_BODY, fg=th.TEXT_MUTED,
             bg=b, width=22, anchor="w").pack(side="left")
    var = tk.StringVar()
    e = tk.Entry(f, textvariable=var, font=th.FONT_BODY,
                 bg=th.BG_DARK, fg=th.TEXT_WHITE, insertbackground=th.TEXT_WHITE,
                 relief="flat", width=width,
                 highlightthickness=1, highlightcolor=th.ACCENT,
                 highlightbackground=th.BORDER)
    e.pack(side="left", padx=(4, 0))
    return f, var, e

def combo_row(parent, label_text, values, bg=None, width=26):
    b = bg if bg else th.BG_CARD
    f = tk.Frame(parent, bg=b)
    tk.Label(f, text=label_text, font=th.FONT_BODY, fg=th.TEXT_MUTED,
             bg=b, width=22, anchor="w").pack(side="left")
    var = tk.StringVar(value=values[0] if values else "")
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.TCombobox",
                    fieldbackground=th.BG_DARK, background=th.BG_DARK,
                    foreground=th.TEXT_WHITE, selectbackground=th.ACCENT,
                    selectforeground=th.TEXT_DARK, arrowcolor=th.ACCENT)
    cb = ttk.Combobox(f, textvariable=var, values=values,
                      font=th.FONT_BODY, width=width,
                      style="Dark.TCombobox", state="readonly")
    cb.pack(side="left", padx=(4, 0))
    return f, var, cb

def build_treeview(parent, columns, headings, col_widths, height=14):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.Treeview",
                    background=th.BG_CARD, foreground=th.TEXT_WHITE,
                    fieldbackground=th.BG_CARD, rowheight=th.ROW_H, font=th.FONT_BODY)
    style.configure("Dark.Treeview.Heading",
                    background=th.BG_SIDEBAR, foreground=th.ACCENT,
                    font=th.FONT_BODY_B, relief="flat")
    style.map("Dark.Treeview",
              background=[("selected", th.ACCENT)],
              foreground=[("selected", th.TEXT_DARK)])
    frame = tk.Frame(parent, bg=th.BG_DARK)
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

def stat_card(parent, title_fr, title_ar, value, color=None):
    c = color if color else th.ACCENT
    f = tk.Frame(parent, bg=th.BG_CARD, padx=20, pady=14,
                 highlightthickness=1, highlightbackground=c)
    tk.Label(f, text=title_fr, font=th.FONT_SMALL, fg=th.TEXT_MUTED, bg=th.BG_CARD).pack()
    tk.Label(f, text=title_ar, font=th.FONT_SMALL, fg=th.TEXT_MUTED, bg=th.BG_CARD).pack()
    tk.Label(f, text=str(value), font=("Georgia", 26, "bold"), fg=c, bg=th.BG_CARD).pack()
    return f

def separator(parent, bg=None):
    b = bg if bg else th.BORDER
    return tk.Frame(parent, bg=b, height=1)

def scrollable_frame(parent, bg=None):
    b = bg if bg else th.BG_CARD
    container = tk.Frame(parent, bg=b)
    canvas = tk.Canvas(container, bg=b, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=b)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return container, inner
