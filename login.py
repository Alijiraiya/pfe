import tkinter as tk
from tkinter import messagebox
from theme import ThemeManager as TM
from widgets import separator

DEFAULT_PASSWORD = "imam1234"

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Connexion | تسجيل الدخول")
        self.configure(bg=TM.get_color("bg"))
        self.resizable(False, False)
        self.grab_set()
        self._on_success = on_success
        self._attempts = 0
        self._build()
        self.geometry("450x360")
        self._center()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build(self):
        tk.Label(self, text="🕌", font=("", 48), bg=TM.get_color("bg")).pack(pady=(20, 0))
        tk.Label(self, text="Système de Gestion des Dons | التبرعات ادارة نظام", font=("Georgia", 14, "bold"), fg=TM.get_color("accent"), bg=TM.get_color("bg")).pack()
        tk.Label(self, text="Mosquée | المسجد", font=TM.FONTS["body"], fg=TM.get_color("text_muted"), bg=TM.get_color("bg")).pack(pady=(0, 10))
        separator(self).pack(fill="x", padx=40, pady=10)

        inner = tk.Frame(self, bg=TM.get_color("bg"))
        inner.pack(padx=50, pady=10, fill="x")
        tk.Label(inner, text="Mot de passe | كلمة المرور :", font=TM.FONTS["body"], fg=TM.get_color("text_muted"), bg=TM.get_color("bg"), anchor="w").pack(fill="x")
        self.v_pwd = tk.StringVar()
        e = tk.Entry(inner, textvariable=self.v_pwd, font=("Helvetica", 13), show="●", bg=TM.get_color("card"), fg=TM.get_color("text"), insertbackground=TM.get_color("text"), relief="flat", width=26, highlightthickness=2, highlightcolor=TM.get_color("accent"), highlightbackground=TM.get_color("border"))
        e.pack(fill="x", pady=8, ipady=6)
        e.bind("<Return>", lambda _: self._check())
        e.focus_set()
        self.err_lbl = tk.Label(inner, text="", font=TM.FONTS["small"], fg=TM.get_color("danger"), bg=TM.get_color("bg"))
        self.err_lbl.pack()
        tk.Button(inner, text="Se connecter | دخول", font=TM.FONTS["button"], bg=TM.get_color("accent"), fg=TM.get_color("text_dark"), relief="flat", cursor="hand2", activebackground=TM.get_color("accent_hover"), activeforeground=TM.get_color("text"), padx=20, pady=8, command=self._check).pack(pady=8)

    def _check(self):
        if self.v_pwd.get() == DEFAULT_PASSWORD:
            self._on_success()
            self.destroy()
        else:
            self._attempts += 1
            self.err_lbl.config(text=f"❌ Mot de passe incorrect | كلمة المرور غير صحيحة ({self._attempts}/5)")
            self.v_pwd.set("")
            if self._attempts >= 5:
                messagebox.showerror("Accès bloqué | تم الحجب", "Trop de tentatives. Fermeture. | محاولات كثيرة. سيتم الإغلاق.", parent=self)
                self.master.destroy()