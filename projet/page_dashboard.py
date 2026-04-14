import tkinter as tk
from theme import *
from widgets import stat_card, section_title, separator
import database as db


class DashboardPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=BG_DARK)
        header.pack(fill="x", padx=PAD*2, pady=(PAD*2, PAD))
        tk.Label(header, text="Tableau de bord  |  لوحة التحكم",
                 font=FONT_TITLE, fg=ACCENT, bg=BG_DARK).pack(side="left")
        tk.Label(header, text="الرحيم الرحمن الله بسم",
                 font=("Georgia", 13, "italic"), fg=TEXT_MUTED, bg=BG_DARK).pack(side="right")
        separator(self, bg=ACCENT).pack(fill="x", padx=PAD*2, pady=4)

        self.cards_frame = tk.Frame(self, bg=BG_DARK)
        self.cards_frame.pack(fill="x", padx=PAD*2, pady=PAD)

        self.balance_label = tk.Label(self, text="",
                                      font=("Georgia", 17, "bold"),
                                      fg=SUCCESS, bg=BG_DARK)
        self.balance_label.pack(fill="x", padx=PAD*2, pady=4)

        act_frame = tk.Frame(self, bg=BG_CARD,
                             highlightthickness=1, highlightbackground=BORDER)
        act_frame.pack(fill="both", expand=True, padx=PAD*2, pady=PAD)
        section_title(act_frame, "Activité récente  |  النشاط الأخير",
                      bg=BG_CARD).pack(fill="x", padx=PAD, pady=(PAD, 4))
        self.activity_text = tk.Text(act_frame, bg=BG_CARD, fg=TEXT_WHITE,
                                     font=FONT_MONO, relief="flat",
                                     state="disabled", height=10,
                                     highlightthickness=0)
        self.activity_text.pack(fill="both", expand=True, padx=PAD, pady=(0, PAD))
        self.refresh()

    def refresh(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        stats = db.get_stats()
        for fr, ar, val, col in [
            ("Familles",  "عائلات",   stats["families"],  ACCENT),
            ("Enfants",   "أطفال",    stats["children"],  ACCENT2),
            ("Donateurs", "متبرعون",  stats["donors"],    "#5B9BD5"),
            ("Dons",      "تبرعات",   stats["donations"], "#9B59B6"),
        ]:
            stat_card(self.cards_frame, fr, ar, val, col).pack(side="left", padx=8, pady=4)

        bal = stats["balance"]
        self.balance_label.config(
            fg=SUCCESS if bal >= 0 else DANGER,
            text=(f"💰 Entrées : {stats['total_in']:,.0f} DA   |   "
                  f"📤 Sorties : {stats['total_out']:,.0f} DA   |   "
                  f"⚖️ Solde : {bal:,.0f} DA"))

        lines = []
        for r in db.get_all_donations()[:6]:
            lines.append(f"➕ Don de {r[1]} : {r[2]:,.0f} DA ({r[4]})")
        for r in db.get_all_distributions()[:6]:
            lines.append(f"➖ Aide à {r[1]} : {r[2]:,.0f} DA — {r[3]} ({r[4]})")
        lines.sort(reverse=True)

        self.activity_text.config(state="normal")
        self.activity_text.delete("1.0", "end")
        self.activity_text.insert("end",
            "\n".join(lines[:12]) if lines
            else "Aucune activité récente.  |  لا يوجد نشاط حديث.")
        self.activity_text.config(state="disabled")
