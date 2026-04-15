import tkinter as tk
from tkinter import messagebox
import theme as th
from widgets import (styled_button, danger_button, build_treeview,
                     entry_row, combo_row, separator)
import database as db

class DonationsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=th.BG_DARK)
        self._build()
        self.load_data()

    def _build(self):
        tk.Label(self, text="Gestion des Dons  |  إدارة التبرعات",
                 font=th.FONT_TITLE, fg=th.ACCENT, bg=th.BG_DARK).pack(
                     fill="x", padx=th.PAD*2, pady=(th.PAD*2, 4))
        separator(self, bg=th.ACCENT).pack(fill="x", padx=th.PAD*2, pady=4)

        self.banner = tk.Label(self, text="", font=th.FONT_BODY_B,
                               fg=th.SUCCESS, bg=th.BG_CARD, pady=8)
        self.banner.pack(fill="x", padx=th.PAD*2, pady=4)

        pane = tk.Frame(self, bg=th.BG_DARK)
        pane.pack(fill="both", expand=True, padx=th.PAD*2, pady=4)

        # -- Donateurs --
        left = tk.Frame(pane, bg=th.BG_DARK)
        left.pack(side="left", fill="both", expand=True, padx=(0, th.PAD//2))
        tk.Label(left, text="Donateurs / المتبرعون",
                 font=th.FONT_HEADING, fg=th.ACCENT2, bg=th.BG_DARK).pack(pady=4)

        df, self.donor_tree = build_treeview(left,
            ["id","name","phone","email"],
            ["#","Nom / الاسم","Tél","Email"],
            [40,160,110,160], height=11)
        df.pack(fill="both", expand=True)

        dform = tk.Frame(left, bg=th.BG_DARK); dform.pack(fill="x", pady=4)
        f, self.v_dname,  _ = entry_row(dform, "Nom :", bg=th.BG_DARK, width=14);  f.pack(side="left", padx=2)
        f, self.v_dphone, _ = entry_row(dform, "Tél :", bg=th.BG_DARK, width=10);  f.pack(side="left", padx=2)
        f, self.v_demail, _ = entry_row(dform, "Email :", bg=th.BG_DARK, width=14); f.pack(side="left", padx=2)

        dbb = tk.Frame(left, bg=th.BG_DARK); dbb.pack(pady=2)
        styled_button(dbb, "➕ Ajouter donateur", self._add_donor).pack(side="left", padx=4)
        danger_button(dbb, "🗑️ Supprimer", self._del_donor).pack(side="left", padx=4)

        # -- Dons --
        right = tk.Frame(pane, bg=th.BG_DARK)
        right.pack(side="left", fill="both", expand=True, padx=(th.PAD//2, 0))
        tk.Label(right, text="Dons reçus / التبرعات المستلمة",
                 font=th.FONT_HEADING, fg=th.ACCENT, bg=th.BG_DARK).pack(pady=4)

        donf, self.don_tree = build_treeview(right,
            ["id","donor","amount","type","date","notes"],
            ["#","Donateur","Montant DA","Type","Date","Notes"],
            [40,130,95,90,95,120], height=11)
        donf.pack(fill="both", expand=True)

        donform = tk.Frame(right, bg=th.BG_DARK); donform.pack(fill="x", pady=4)
        f, self.v_amt,   _ = entry_row(donform, "Montant DA :", bg=th.BG_DARK, width=10); f.pack(side="left", padx=2)
        f, self.v_dtype, _ = combo_row(donform, "Type :",
                                        ["Cash","Nourriture","Fournitures","Autre"],
                                        bg=th.BG_DARK, width=12); f.pack(side="left", padx=2)
        f, self.v_dnote, _ = entry_row(donform, "Notes :", bg=th.BG_DARK, width=16); f.pack(side="left", padx=2)

        donbb = tk.Frame(right, bg=th.BG_DARK); donbb.pack(pady=2)
        styled_button(donbb, "➕ Enregistrer don", self._add_donation).pack(side="left", padx=4)
        danger_button(donbb, "🗑️ Supprimer", self._del_donation).pack(side="left", padx=4)

    def load_data(self):
        for r in self.donor_tree.get_children():
            self.donor_tree.delete(r)
        for row in db.get_all_donors():
            self.donor_tree.insert("", "end", iid=str(row[0]), values=row)

        for r in self.don_tree.get_children():
            self.don_tree.delete(r)
        for row in db.get_all_donations():
            self.don_tree.insert("", "end", iid=str(row[0]), values=row)

        ti = db.get_total_donations()
        to = db.get_total_distributions()
        bal = ti - to
        self.banner.config(
            fg=th.SUCCESS if bal >= 0 else th.DANGER,
            text=(f"  💵 Total reçu : {ti:,.0f} DA   |   "
                  f"📤 Total distribué : {to:,.0f} DA   |   "
                  f"⚖️ Solde : {bal:,.0f} DA  ")
        )

    def _add_donor(self):
        name = self.v_dname.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Nom obligatoire.")
            return
        db.add_donor(name, self.v_dphone.get(), self.v_demail.get())
        self.v_dname.set(""); self.v_dphone.set(""); self.v_demail.set("")
        self.load_data()

    def _del_donor(self):
        sel = self.donor_tree.selection()
        if sel and messagebox.askyesno("Confirmer", "Supprimer ce donateur ?"):
            db.delete_donor(int(sel[0]))
            self.load_data()

    def _add_donation(self):
        sel = self.donor_tree.selection()
        if not sel:
            messagebox.showwarning("Sélection",
                "Sélectionnez d'abord un donateur.\nاختر المتبرع أولاً.")
            return
        try:
            amt = float(self.v_amt.get())
        except ValueError:
            messagebox.showerror("Erreur", "Montant invalide.")
            return
        db.add_donation(int(sel[0]), amt, self.v_dtype.get(), self.v_dnote.get())
        self.v_amt.set(""); self.v_dnote.set("")
        self.load_data()

    def _del_donation(self):
        sel = self.don_tree.selection()
        if sel and messagebox.askyesno("Confirmer", "Supprimer ce don ?"):
            db.delete_donation(int(sel[0]))
            self.load_data()

    def refresh(self):
        self.load_data()
