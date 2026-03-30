import tkinter as tk
from tkinter import messagebox
from theme import *
from widgets import separator

DEFAULT_PASSWORD = "imam1234"


class LoginWindow(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Connexion  |  تسجيل الدخول")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.grab_set()
        self._on_success = on_success
        self._attempts   = 0
        self._build()
        self.geometry("420x340")
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build(self):
        tk.Label(self, text="🕌", font=("", 48), bg=BG_DARK).pack(pady=(20, 0))
        tk.Label(self, text="نظام إدارة التبرعات",
                 font=("Georgia", 16, "bold"), fg=ACCENT, bg=BG_DARK).pack()
        tk.Label(self, text="Gestion des Dons — Mosquée",
                 font=FONT_BODY, fg=TEXT_MUTED, bg=BG_DARK).pack(pady=(0, 10))
        separator(self, bg=ACCENT).pack(fill="x", padx=40, pady=4)

        inner = tk.Frame(self, bg=BG_DARK)
        inner.pack(padx=50, pady=10, fill="x")
        tk.Label(inner, text="Mot de passe / كلمة المرور :",
                 font=FONT_BODY, fg=TEXT_MUTED, bg=BG_DARK, anchor="w").pack(fill="x")
        self.v_pwd = tk.StringVar()
        e = tk.Entry(inner, textvariable=self.v_pwd, font=("Helvetica", 13),
                     show="●", bg=BG_CARD, fg=TEXT_WHITE,
                     insertbackground=TEXT_WHITE, relief="flat", width=26,
                     highlightthickness=2, highlightcolor=ACCENT,
                     highlightbackground=BORDER)
        e.pack(fill="x", pady=8, ipady=6)
        e.bind("<Return>", lambda _: self._check())
        e.focus_set()
        self.err_lbl = tk.Label(inner, text="", font=FONT_SMALL, fg=DANGER, bg=BG_DARK)
        self.err_lbl.pack()
        tk.Button(inner, text="Se connecter  /  دخول",
                  font=FONT_BUTTON, bg=ACCENT, fg=TEXT_DARK,
                  relief="flat", cursor="hand2",
                  activebackground=ACCENT2, activeforeground=TEXT_WHITE,
                  padx=20, pady=8, command=self._check).pack(pady=8)

    def _check(self):
        if self.v_pwd.get() == DEFAULT_PASSWORD:
            self._on_success()
            self.destroy()
        else:
            self._attempts += 1
            self.err_lbl.config(
                text=f"❌ Mot de passe incorrect ({self._attempts}/5)")
            self.v_pwd.set("")
            if self._attempts >= 5:
                messagebox.showerror("Accès bloqué / تم الحجب",
                    "Trop de tentatives. L'application va se fermer.\n"
                    "محاولات كثيرة. سيتم الإغلاق.", parent=self)
                self.master.destroy()