import tkinter as tk
from tkinter import messagebox
from theme import *
from widgets import (styled_button, danger_button, build_treeview,
                     entry_row, combo_row, separator)
import database as db


class DistributionsPage(tk.Frame):
    TYPES = ["Financiere","Alimentaire","Medicale","Fournitures","Autre"]

    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)
        self.family_names = []
        self.family_ids   = []
        self._build()
        self.load_data()

    def _build(self):
        tk.Label(self, text="Distributions / Aides  |  توزيع المساعدات",
                 font=FONT_TITLE, fg=ACCENT, bg=BG_DARK).pack(
                     fill="x", padx=PAD*2, pady=(PAD*2, 4))
        separator(self, bg=ACCENT).pack(fill="x", padx=PAD*2, pady=4)

        self.banner = tk.Label(self, text="", font=FONT_BODY_B,
                               fg=SUCCESS, bg=BG_CARD, pady=8)
        self.banner.pack(fill="x", padx=PAD*2, pady=4)

        tf, self.tree = build_treeview(self,
            ["id","family","amount","type","date","notes"],
            ["#","Famille / العائلة","Montant DA","Type","Date","Notes"],
            [40,200,100,110,110,250], height=13)
        tf.pack(fill="both", expand=True, padx=PAD*2, pady=PAD)

        form = tk.Frame(self, bg=BG_DARK)
        form.pack(fill="x", padx=PAD*2, pady=4)

        tk.Label(form, text="Famille / العائلة :", font=FONT_BODY,
                 fg=TEXT_MUTED, bg=BG_DARK).pack(side="left")
        self.v_family = tk.StringVar()
        self.family_cb = tk.OptionMenu(form, self.v_family, "")
        self.family_cb.config(bg=BG_CARD, fg=TEXT_WHITE, font=FONT_BODY,
                              activebackground=ACCENT, highlightthickness=0)
        self.family_cb["menu"].config(bg=BG_CARD, fg=TEXT_WHITE, font=FONT_BODY)
        self.family_cb.pack(side="left", padx=8)

        f, self.v_amt,  _ = entry_row(form, "Montant DA :", bg=BG_DARK, width=10); f.pack(side="left", padx=6)
        f, self.v_type, _ = combo_row(form, "Type :", self.TYPES, bg=BG_DARK, width=14);   f.pack(side="left", padx=6)
        f, self.v_note, _ = entry_row(form, "Notes :", bg=BG_DARK, width=20); f.pack(side="left", padx=6)

        bb = tk.Frame(self, bg=BG_DARK); bb.pack(pady=6)
        styled_button(bb, "➕ Enregistrer aide / تسجيل مساعدة", self._add).pack(side="left", padx=8)
        danger_button(bb, "🗑️ Supprimer / حذف", self._delete).pack(side="left", padx=8)

    def _refresh_combo(self):
        self.family_names, self.family_ids = [], []
        for row in db.get_all_families():
            self.family_ids.append(row[0])
            self.family_names.append(row[1])
        menu = self.family_cb["menu"]
        menu.delete(0, "end")
        for name in self.family_names:
            menu.add_command(label=name, command=lambda n=name: self.v_family.set(n))
        if self.family_names:
            self.v_family.set(self.family_names[0])
        else:
            self.v_family.set("Aucune famille")

    def load_data(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for row in db.get_all_distributions():
            self.tree.insert("", "end", iid=str(row[0]), values=row)

        ti = db.get_total_donations()
        to = db.get_total_distributions()
        bal = ti - to
        self.banner.config(
            fg=SUCCESS if bal >= 0 else DANGER,
            text=(f"  💵 Total reçu : {ti:,.0f} DA   |   "
                  f"📤 Total distribué : {to:,.0f} DA   |   "
                  f"⚖️ Solde : {bal:,.0f} DA  ")
        )
        self._refresh_combo()

    def _add(self):
        name = self.v_family.get()
        if not name or name not in self.family_names:
            messagebox.showwarning("Sélection",
                "Sélectionnez une famille.\nاختر عائلة.")
            return
        try:
            amt = float(self.v_amt.get())
        except ValueError:
            messagebox.showerror("Erreur", "Montant invalide.")
            return
        bal = db.get_balance()
        if amt > bal:
            messagebox.showerror("Solde insuffisant",
                                 f"Solde disponible : {bal:,.0f} DA")
            return
        fid = self.family_ids[self.family_names.index(name)]
        db.add_distribution(fid, amt, self.v_type.get(), self.v_note.get())
        self.v_amt.set(""); self.v_note.set("")
        self.load_data()
        messagebox.showinfo("✅", "Aide enregistrée.\nتم تسجيل المساعدة.")

    def _delete(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Confirmer", "Supprimer cette distribution ?"):
            db.delete_distribution(int(sel[0]))
            self.load_data()

    def refresh(self):
        self.load_data()