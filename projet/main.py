import tkinter as tk
from tkinter import messagebox
import theme as th
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
        self.configure(bg=th.BG_DARK)
        db.initialize_database()
        self._pages   = {}
        self._current = None
        self._build_shell()
        self.withdraw()
        self.after(100, self._show_login)

    # ── Sidebar ──────────────────────────────────────────
    def _build_shell(self):
        self.sidebar = tk.Frame(self, bg=th.BG_SIDEBAR, width=th.SIDEBAR_W)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.lbl_logo = tk.Label(self.sidebar, text="🕌", font=("", 34),
                                 bg=th.BG_SIDEBAR, fg=th.ACCENT)
        self.lbl_logo.pack(pady=(24, 0))
        self.lbl_title = tk.Label(self.sidebar,
                                  text="إدارة التبرعات\nGestion des Dons",
                                  font=("Georgia", 11, "bold"), fg=th.ACCENT,
                                  bg=th.BG_SIDEBAR, justify="center")
        self.lbl_title.pack(pady=(4, 20))
        
        self.sep_top = tk.Frame(self.sidebar, bg=th.BORDER, height=1)
        self.sep_top.pack(fill="x", padx=16, pady=4)

        self._nav_buttons = {}
        for lbl, key in self.PAGES:
            btn = tk.Button(self.sidebar, text=lbl, font=th.FONT_BODY_B,
                            fg=th.TEXT_MUTED, bg=th.BG_SIDEBAR,
                            activebackground=th.BG_CARD, activeforeground=th.ACCENT,
                            relief="flat", cursor="hand2",
                            anchor="w", padx=16, pady=10, justify="left",
                            command=lambda k=key: self.show_page(k))
            btn.pack(fill="x", pady=2)
            self._nav_buttons[key] = btn

        # Séparateur bas
        self.sep_bot = tk.Frame(self.sidebar, bg=th.BORDER, height=1)
        self.sep_bot.pack(fill="x", padx=16, pady=8, side="bottom")

        # Bouton Thème
        self.theme_btn = tk.Button(self.sidebar,
                                   text="🌓  Thème / المظهر",
                                   font=th.FONT_SMALL, fg=th.TEXT_MUTED, bg=th.BG_SIDEBAR,
                                   activebackground=th.BG_CARD,
                                   relief="flat", cursor="hand2",
                                   command=self.toggle_theme)
        self.theme_btn.pack(side="bottom", pady=4)

        # Bouton Sauvegarde
        self.backup_btn = tk.Button(self.sidebar,
                                    text="💾  Sauvegarde / نسخ احتياطي",
                                    font=th.FONT_SMALL, fg=th.TEXT_MUTED, bg=th.BG_SIDEBAR,
                                    activebackground=th.BG_CARD,
                                    relief="flat", cursor="hand2",
                                    command=self._backup)
        self.backup_btn.pack(side="bottom", pady=4)

        # Bouton Quitter
        self.quit_btn = tk.Button(self.sidebar,
                                  text="⏻  Quitter / خروج",
                                  font=th.FONT_SMALL, fg=th.DANGER, bg=th.BG_SIDEBAR,
                                  activebackground=th.DANGER, activeforeground=th.TEXT_WHITE,
                                  relief="flat", cursor="hand2",
                                  command=self._quit)
        self.quit_btn.pack(side="bottom", pady=8)

        self.content = tk.Frame(self, bg=th.BG_DARK)
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
            btn.config(fg=th.ACCENT if k == key else th.TEXT_MUTED,
                       bg=th.BG_CARD if k == key else th.BG_SIDEBAR)
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
        self.lbl_logo.config(bg=th.BG_SIDEBAR, fg=th.ACCENT)
        self.lbl_title.config(bg=th.BG_SIDEBAR, fg=th.ACCENT)
        self.sep_top.config(bg=th.BORDER)
        self.sep_bot.config(bg=th.BORDER)
        self.theme_btn.config(bg=th.BG_SIDEBAR, fg=th.TEXT_MUTED)
        self.backup_btn.config(bg=th.BG_SIDEBAR, fg=th.TEXT_MUTED)
        self.quit_btn.config(bg=th.BG_SIDEBAR, fg=th.DANGER)
        
        for k, btn in self._nav_buttons.items():
            btn.config(fg=th.ACCENT if k == self._current else th.TEXT_MUTED,
                       bg=th.BG_CARD if k == self._current else th.BG_SIDEBAR)

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
