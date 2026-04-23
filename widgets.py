import tkinter as tk
from tkinter import ttk
from theme import ThemeManager as TM

def create_button(parent, text, command, style_type="primary", width=None):
    bg_color = TM.get_color("danger") if style_type == "danger" else TM.get_color("accent")
    fg_color = TM.get_color("text") if style_type == "danger" else TM.get_color("text_dark")
    btn = tk.Button(parent, text=text, command=command, bg=bg_color, fg=fg_color,
                    font=TM.FONTS["button"], relief="flat", cursor="hand2", 
                    activebackground=TM.get_color("accent_hover"), activeforeground=TM.get_color("text"), padx=12, pady=5)
    if width: btn.config(width=width)
    return btn

def create_stat_card(parent, title, value):
    card = tk.Frame(parent, bg=TM.get_color("card"), padx=20, pady=14, highlightthickness=1, highlightbackground=TM.get_color("accent"))
    tk.Label(card, text=title, font=TM.FONTS["small"], fg=TM.get_color("text_muted"), bg=TM.get_color("card")).pack()
    tk.Label(card, text=str(value), font=("Georgia", 24, "bold"), fg=TM.get_color("accent"), bg=TM.get_color("card")).pack()
    return card

def create_treeview(parent, columns, headings, col_widths, height=14):
    frame = tk.Frame(parent, bg=TM.get_color("bg"))
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=height, style="Custom.Treeview")
    for col, head, w in zip(columns, headings, col_widths):
        tree.heading(col, text=head)
        tree.column(col, width=w, minwidth=50, stretch=tk.YES, anchor="center")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    return frame, tree

def entry_row(parent, label_text, width=28):
    b = TM.get_color("card")
    f = tk.Frame(parent, bg=b)
    tk.Label(f, text=label_text, font=TM.FONTS["body"], fg=TM.get_color("text_muted"), bg=b, width=25, anchor="w").pack(side="left")
    var = tk.StringVar()
    e = tk.Entry(f, textvariable=var, font=TM.FONTS["body"], bg=TM.get_color("bg"), fg=TM.get_color("text"), insertbackground=TM.get_color("text"), relief="flat", width=width, highlightthickness=1, highlightcolor=TM.get_color("accent"), highlightbackground=TM.get_color("border"))
    e.pack(side="left", padx=(4, 0), fill="x", expand=True)
    return f, var, e

def combo_row(parent, label_text, values, width=26):
    b = TM.get_color("card")
    f = tk.Frame(parent, bg=b)
    tk.Label(f, text=label_text, font=TM.FONTS["body"], fg=TM.get_color("text_muted"), bg=b, width=25, anchor="w").pack(side="left")
    var = tk.StringVar(value=values[0] if values else "")
    cb = ttk.Combobox(f, textvariable=var, values=values, font=TM.FONTS["body"], width=width, state="readonly", style="Custom.TCombobox")
    cb.pack(side="left", padx=(4, 0), fill="x", expand=True)
    return f, var, cb

def separator(parent):
    return tk.Frame(parent, bg=TM.get_color("border"), height=1)

def section_title(parent, text):
    b = TM.get_color("card")
    f = tk.Frame(parent, bg=b)
    tk.Label(f, text=text, font=TM.FONTS["heading"], fg=TM.get_color("accent"), bg=b).pack(side="left")
    tk.Frame(f, bg=TM.get_color("accent"), height=2).pack(side="left", fill="x", expand=True, padx=10, pady=8)
    return f