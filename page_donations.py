import tkinter as tk
from tkinter import messagebox
from theme import ThemeManager as TM
from widgets import create_button, create_treeview, entry_row, combo_row, separator
import database as db

class DonationsPage(tk.Frame):
    TYPES_DON = ["Cash | نقداً", "Nourriture | طعام", "Fournitures | مستلزمات", "Autre | آخر"]

    def __init__(self, parent):
        super().__init__(parent, bg=TM.get_color("bg"))
        self._build()
        self.load_data()

    def _build(self):
        tk.Label(self, text="Gestion des Dons | إدارة التبرعات", font=TM.FONTS["title"], fg=TM.get_color("accent"), bg=TM.get_color("bg")).pack(side="top", fill="x", padx=TM.SIZES["pad"]*2, pady=(TM.SIZES["pad"], 4))
        separator(self).pack(side="top", fill="x", padx=TM.SIZES["pad"]*2, pady=4)

        self.banner = tk.Label(self, text="", font=TM.FONTS["body_b"], fg=TM.get_color("success"), bg=TM.get_color("card"), pady=8)
        self.banner.pack(side="top", fill="x", padx=TM.SIZES["pad"]*2, pady=4)

        pane = tk.Frame(self, bg=TM.get_color("bg"))
        pane.pack(side="top", fill="both", expand=True, padx=TM.SIZES["pad"]*2, pady=4)
        pane.columnconfigure(0, weight=1)
        pane.columnconfigure(1, weight=1)
        pane.rowconfigure(0, weight=1)

        # -- قسم المتبرعين --
        left = tk.Frame(pane, bg=TM.get_color("bg"))
        left.grid(row=0, column=0, sticky="nsew", padx=(0, TM.SIZES["pad"]//2))
        tk.Label(left, text="Donateurs | المتبرعون", font=TM.FONTS["heading"], fg=TM.get_color("accent"), bg=TM.get_color("bg")).pack(side="top", pady=4)

        dbb = tk.Frame(left, bg=TM.get_color("bg"))
        dbb.pack(side="bottom", pady=10)
        create_button(dbb, "➕ Ajouter | إضافة متبرع", self._add_donor).pack(side="left", padx=4)
        create_button(dbb, "🗑️ Supprimer | حذف", self._del_donor, "danger").pack(side="left", padx=4)

        dform = tk.Frame(left, bg=TM.get_color("bg"))
        dform.pack(side="bottom", fill="x", pady=4)
        # التعديل هنا: ترتيب عمودي side="top" بدلاً من أفقي لمنع اختفاء الخانات
        f, self.v_dname, _ = entry_row(dform, "Nom | الاسم :", width=14); f.pack(side="top", pady=2, fill="x")
        f, self.v_dphone, _ = entry_row(dform, "Tél | الهاتف :", width=10); f.pack(side="top", pady=2, fill="x")

        self.df_c, self.donor_tree = create_treeview(left, ["id","name","phone"], ["#", "Nom | الاسم", "Tél | الهاتف"], [40,160,110], height=8)
        self.df_c.pack(side="top", fill="both", expand=True)

        # -- قسم التبرعات --
        right = tk.Frame(pane, bg=TM.get_color("bg"))
        right.grid(row=0, column=1, sticky="nsew", padx=(TM.SIZES["pad"]//2, 0))
        tk.Label(right, text="Dons reçus | التبرعات المستلمة", font=TM.FONTS["heading"], fg=TM.get_color("accent"), bg=TM.get_color("bg")).pack(side="top", pady=4)

        donbb = tk.Frame(right, bg=TM.get_color("bg"))
        donbb.pack(side="bottom", pady=10)
        create_button(donbb, "➕ Enregistrer | تسجيل تبرع", self._add_donation).pack(side="left", padx=4)
        create_button(donbb, "🗑️ Supprimer | حذف", self._del_donation, "danger").pack(side="left", padx=4)

        donform = tk.Frame(right, bg=TM.get_color("bg"))
        donform.pack(side="bottom", fill="x", pady=4)
        # التعديل هنا أيضاً: ترتيب عمودي side="top"
        f, self.v_amt, _ = entry_row(donform, "Montant | المبلغ :", width=10); f.pack(side="top", pady=2, fill="x")
        f, self.v_type, _ = combo_row(donform, "Type | النوع :", self.TYPES_DON, width=15); f.pack(side="top", pady=2, fill="x")

        self.donf_c, self.don_tree = create_treeview(right, ["id","donor","amount","date", "type"], ["#", "Donateur | المتبرع", "Montant | المبلغ", "Date | التاريخ", "Type | النوع"], [40,130,95,95, 90], height=8)
        self.donf_c.pack(side="top", fill="both", expand=True)

    def load_data(self):
        for r in self.donor_tree.get_children(): self.donor_tree.delete(r)
        for row in db.get_all_donors(): self.donor_tree.insert("", "end", iid=str(row[0]), values=(row[0], row[1], row[2]))

        for r in self.don_tree.get_children(): self.don_tree.delete(r)
        for row in db.get_all_donations(): self.don_tree.insert("", "end", iid=str(row[0]), values=(row[0], row[1], f"{row[2]:,.0f}", row[4], row[3]))

        bal = db.get_balance()
        self.banner.config(fg=TM.get_color("success") if bal >= 0 else TM.get_color("danger"), text=f"Solde | الرصيد المتاح : {bal:,.0f} DA")

    def _add_donor(self):
        if not self.v_dname.get().strip(): return messagebox.showerror("Erreur | خطأ", "Nom obligatoire | الاسم إلزامي.")
        db.add_donor(self.v_dname.get().strip(), self.v_dphone.get(), "")
        self.load_data()

    def _del_donor(self):
        s = self.donor_tree.selection()
        if s and messagebox.askyesno("Confirmation | تأكيد", "Supprimer? | هل أنت متأكد من الحذف؟"): db.delete_donor(int(s[0])); self.load_data()

    def _add_donation(self):
        s = self.donor_tree.selection()
        if not s: return messagebox.showwarning("Info | تنبيه", "Sélect. donateur | اختر متبرعاً.")
        try: amt = float(self.v_amt.get())
        except: return messagebox.showerror("Erreur | خطأ", "Montant invalide | مبلغ غير صحيح.")
        db.add_donation(int(s[0]), amt, self.v_type.get(), "")
        self.load_data()

    def _del_donation(self):
        s = self.don_tree.selection()
        if s and messagebox.askyesno("Confirmation | تأكيد", "Supprimer? | هل أنت متأكد من الحذف؟"): db.delete_donation(int(s[0])); self.load_data()

    def refresh(self): self.load_data()