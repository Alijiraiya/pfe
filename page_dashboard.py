import tkinter as tk
from theme import ThemeManager as TM
from widgets import create_stat_card, section_title, separator
import database as db

class DashboardPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=TM.get_color("bg"))
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=TM.get_color("bg"))
        header.pack(fill="x", padx=TM.SIZES["pad"]*2, pady=(TM.SIZES["pad"], 5))
        tk.Label(header, text="Tableau de bord |التحكم لوحة", font=TM.FONTS["title"], fg=TM.get_color("accent"), bg=TM.get_color("bg")).pack(side="left")
        # دمج البسملة مع الفرنسية حتى لا يقلبها
        tk.Label(header, text="الرحيم الرحمان الله بسم", font=("Georgia", 13, "italic"), fg=TM.get_color("text_muted"), bg=TM.get_color("bg")).pack(side="right")
        separator(self).pack(fill="x", padx=TM.SIZES["pad"]*2, pady=4)

        self.cards_frame = tk.Frame(self, bg=TM.get_color("bg"))
        self.cards_frame.pack(fill="x", padx=TM.SIZES["pad"]*2, pady=10)
        for i in range(4): self.cards_frame.columnconfigure(i, weight=1)

        self.balance_label = tk.Label(self, text="", font=("Georgia", 16, "bold"), fg=TM.get_color("success"), bg=TM.get_color("bg"))
        self.balance_label.pack(fill="x", padx=TM.SIZES["pad"]*2, pady=4)

        act_frame = tk.Frame(self, bg=TM.get_color("card"), highlightthickness=1, highlightbackground=TM.get_color("border"))
        act_frame.pack(fill="both", expand=True, padx=TM.SIZES["pad"]*2, pady=10)
        section_title(act_frame, "Activité récente |الاخير النشاط").pack(fill="x", padx=TM.SIZES["pad"], pady=(10, 4))
        self.activity_text = tk.Text(act_frame, bg=TM.get_color("card"), fg=TM.get_color("text"), font=TM.FONTS["mono"], relief="flat", state="disabled", height=10, highlightthickness=0)
        self.activity_text.pack(fill="both", expand=True, padx=TM.SIZES["pad"], pady=(0, 10))

    def refresh(self):
        for w in self.cards_frame.winfo_children(): w.destroy()
        stats = db.get_stats()
        
        c1 = create_stat_card(self.cards_frame, "Familles | العائلات", stats["families"])
        c2 = create_stat_card(self.cards_frame, "Enfants | الأطفال", stats["children"])
        c3 = create_stat_card(self.cards_frame, "Donateurs | المتبرعون", stats["donors"])
        c4 = create_stat_card(self.cards_frame, "Dons | التبرعات", stats["donations"])

        c1.grid(row=0, column=0, sticky="nsew", padx=5)
        c2.grid(row=0, column=1, sticky="nsew", padx=5)
        c3.grid(row=0, column=2, sticky="nsew", padx=5)
        c4.grid(row=0, column=3, sticky="nsew", padx=5)

        bal = stats["balance"]
        self.balance_label.config(fg=TM.get_color("success") if bal >= 0 else TM.get_color("danger"),
            text=f"💰 Entrées | المداخيل : {stats['total_in']:,.0f} DA   ||   📤 Sorties | المصاريف : {stats['total_out']:,.0f} DA   ||   ⚖️ Solde | الرصيد : {bal:,.0f} DA")

        lines = []
        for r in db.get_all_donations()[:6]: lines.append(f"➕ Don de | تبرع من {r[1]} : {r[2]:,.0f} DA ({r[4]})")
        for r in db.get_all_distributions()[:6]: lines.append(f"➖ Aide à | مساعدة لـ {r[1]} : {r[2]:,.0f} DA — {r[3]} ({r[4]})")
        lines.sort(reverse=True)

        self.activity_text.config(state="normal")
        self.activity_text.delete("1.0", "end")
        self.activity_text.insert("end", "\n".join(lines[:12]) if lines else "Aucune activité récente | لا يوجد نشاط اخير")
        self.activity_text.config(state="disabled")