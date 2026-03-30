import tkinter as tk
from tkinter import messagebox
import theme as th
from theme import *
import database as db
from login import LoginWindow
from page_dashboard import DashboardPage
from page_families import FamiliesPage
from page_donations import DonationsPage
from page_distributions import DistributionsPage


class CharityApp(tk.Tk):
    PAGES = [
        ("🏠  Tableau de bord\n        لوحة التحكم",   "dashboard"),
        ("👨‍👩‍👧  Familles\n        العائلات",             "families"),
        ("💰  Dons reçus\n        التبرعات",            "donations"),
        ("📤  Distributions\n       توزيع المساعدات",  "distributions"),
    ]

    def __init__(self):
        super().__init__()
        self.title("إدارة أموال التبرعات — برنامج الإمام")
        self.geometry("1280x760")
        self.minsize(950, 620)
        self.configure(bg=BG_DARK)
        db.initialize_database()
        self._pages   = {}
        self._current = None
        self._build_shell()
        self.withdraw()
        self.after(100, self._show_login)

    # ── Sidebar ──────────────────────────────────────────
    def _build_shell(self):
        self.sidebar = tk.Frame(self, bg=BG_SIDEBAR, width=SIDEBAR_W)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="🕌", font=("", 34),
                 bg=BG_SIDEBAR, fg=ACCENT).pack(pady=(24, 0))
        tk.Label(self.sidebar,
                 text="إدارة التبرعات\nGestion des Dons",
                 font=("Georgia", 11, "bold"), fg=ACCENT,
                 bg=BG_SIDEBAR, justify="center").pack(pady=(4, 20))
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=4)

        self._nav_buttons = {}
        for lbl, key in self.PAGES:
            btn = tk.Button(self.sidebar, text=lbl, font=FONT_BODY_B,
                            fg=TEXT_MUTED, bg=BG_SIDEBAR,
                            activebackground=BG_CARD, activeforeground=ACCENT,
                            relief="flat", cursor="hand2",
                            anchor="w", padx=16, pady=10, justify="left",
                            command=lambda k=key: self.show_page(k))
            btn.pack(fill="x", pady=2)
            self._nav_buttons[key] = btn

        # Séparateur bas
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(
            fill="x", padx=16, pady=8, side="bottom")

        # Bouton Thème
        self.theme_btn = tk.Button(self.sidebar,
                                   text="🌓  Thème / Theme",
                                   font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_SIDEBAR,
                                   activebackground=BG_CARD,
                                   relief="flat", cursor="hand2",
                                   command=self.toggle_theme)
        self.theme_btn.pack(side="bottom", pady=4)

        # Bouton Sauvegarde
        tk.Button(self.sidebar,
                  text="💾  Sauvegarde / نسخ احتياطي",
                  font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_SIDEBAR,
                  activebackground=BG_CARD,
                  relief="flat", cursor="hand2",
                  command=self._backup).pack(side="bottom", pady=4)

        # Bouton Quitter
        tk.Button(self.sidebar,
                  text="⏻  Quitter / خروج",
                  font=FONT_SMALL, fg=DANGER, bg=BG_SIDEBAR,
                  activebackground=DANGER, activeforeground=TEXT_WHITE,
                  relief="flat", cursor="hand2",
                  command=self._quit).pack(side="bottom", pady=8)

        self.content = tk.Frame(self, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True)

    # ── Login ─────────────────────────────────────────────
    def _show_login(self):
        LoginWindow(self, on_success=self._on_auth)

    def _on_auth(self):
        self.deiconify()
        self._build_pages()
        self.show_page("dashboard")

    def _build_pages(self):
        for p in self._pages.values():
            p.destroy()
        self._pages.clear()
        self._pages["dashboard"]     = DashboardPage(self.content)
        self._pages["families"]      = FamiliesPage(self.content)
        self._pages["donations"]     = DonationsPage(self.content)
        self._pages["distributions"] = DistributionsPage(self.content)
        for page in self._pages.values():
            page.place(relx=0, rely=0, relwidth=1, relheight=1)

    # ── Navigation ────────────────────────────────────────
    def show_page(self, key):
        if self._current == key:
            return
        for k, btn in self._nav_buttons.items():
            btn.config(fg=ACCENT if k == key else TEXT_MUTED,
                       bg=BG_CARD if k == key else BG_SIDEBAR)
        page = self._pages[key]
        if hasattr(page, "refresh"):
            page.refresh()
        page.lift()
        self._current = key

    # ── Thème ─────────────────────────────────────────────
    def toggle_theme(self):
        new = "light" if th.CURRENT_THEME == "dark" else "dark"
        th.set_theme(new)
        th.apply_ttk_styles()
        self.config(bg=th.BG_DARK)
        self.content.config(bg=th.BG_DARK)
        self._update_sidebar()
        self._build_pages()
        if self._current:
            self.show_page(self._current)
        else:
            self.show_page("dashboard")

    def _update_sidebar(self):
        self.sidebar.config(bg=th.BG_SIDEBAR)
        def _recurse(w):
            try:
                if isinstance(w, tk.Frame):
                    w.config(bg=th.BG_SIDEBAR)
                elif isinstance(w, tk.Label):
                    w.config(bg=th.BG_SIDEBAR)
                elif isinstance(w, tk.Button):
                    if w not in self._nav_buttons.values():
                        w.config(bg=th.BG_SIDEBAR, fg=th.TEXT_MUTED)
                for c in w.winfo_children():
                    _recurse(c)
            except Exception:
                pass
        _recurse(self.sidebar)
        for k, btn in self._nav_buttons.items():
            btn.config(fg=th.ACCENT if k == self._current else th.TEXT_MUTED,
                       bg=th.BG_CARD if k == self._current else th.BG_SIDEBAR)
        self.theme_btn.config(bg=th.BG_SIDEBAR, fg=th.TEXT_MUTED)

    # ── Sauvegarde ────────────────────────────────────────
    def _backup(self):
        try:
            f = db.backup_database()
            messagebox.showinfo("Sauvegarde / نسخ احتياطي",
                                f"Sauvegarde effectuée :\n{f}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec : {e}")

    # ── Quitter ───────────────────────────────────────────
    def _quit(self):
        if messagebox.askyesno("Quitter / خروج",
                               "Fermer l'application ?\nهل تريد الخروج ؟"):
            self.destroy()


if __name__ == "__main__":
    app = CharityApp()
    app.mainloop()