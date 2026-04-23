import tkinter as tk
from tkinter import messagebox
from theme import ThemeManager as TM
from widgets import create_button, create_treeview, entry_row, separator
import database as db
from water_filling import WaterFillingDistribution

class DistributionsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=TM.get_color("bg"))
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        tk.Label(self, text="Distribution (Water-Filling) | المساعدات توزيع", font=TM.FONTS["title"], fg=TM.get_color("accent"), bg=TM.get_color("bg")).pack(side="top", padx=40, pady=20)
        separator(self).pack(side="top", fill="x", padx=40, pady=4)

        input_frame = tk.Frame(self, bg=TM.get_color("bg"))
        input_frame.pack(side="top", fill="x", padx=40, pady=10)
        f, self.v_budget, _ = entry_row(input_frame, "Budget total | المبلغ الإجمالي للتوزيع :"); f.pack(side="right", padx=10, fill="x", expand=True)
        create_button(input_frame, "⚙️ Calculer | حساب التوزيع", self._run_simulation).pack(side="right")

        hist_frame = tk.Frame(self, bg=TM.get_color("bg"))
        hist_frame.pack(side="bottom", fill="x", padx=40, pady=10)
        tk.Label(hist_frame, text="Historique | التاريخي السجل ", font=TM.FONTS["heading"], fg=TM.get_color("accent"), bg=TM.get_color("bg")).pack(pady=5)
        self.hc, self.hist_tree = create_treeview(hist_frame, ["id","f","amt","d"], ["#", "Famille | العائلة", "Montant | المبلغ", "Date | التاريخ"], [50,250,150,150], height=6)
        self.hc.pack(fill="both", expand=True)

        self.btn_confirm = create_button(self, "✅ Valider | اعتماد التوزيع", self._confirm_dist)
        self.btn_confirm.pack(side="bottom", pady=10)
        self.btn_confirm.config(state="disabled")

        cols = ("name", "score", "amount")
        heads = ("Famille | اسم العائلة", "Score SVF | نقاط", "Montant (DA) | المبلغ المستحق")
        self.container, self.tree = create_treeview(self, cols, heads, [250, 150, 200], height=8)
        self.container.pack(side="top", fill="both", expand=True, padx=40, pady=10)

    def _run_simulation(self):
        try:
            budget = float(self.v_budget.get())
            families = [{'id': f[0], 'head_name': f[1], 'svf_score': f[20]} for f in db.get_all_families() if f[20] > 0]
            wf = WaterFillingDistribution(budget)
            result = wf.calculate(families)
            if result['success']:
                for item in self.tree.get_children(): self.tree.delete(item)
                for res in result['distributions']: 
                    self.tree.insert("", "end", values=(res['head_name'], res['svf_score'], f"{res['amount']:,.0f}"))
                self.btn_confirm.config(state="normal")
                self.simulation_data = result['distributions']
        except ValueError: messagebox.showerror("Erreur | خطأ", "Montant invalide | مبلغ غير صحيح")

    def _confirm_dist(self):
        for res in self.simulation_data: 
            db.add_distribution(res['family_id'], res['amount'], "Water-Filling | خوارزمية", "Automatique | توزيع تلقائي")
        self.btn_confirm.config(state="disabled")
        messagebox.showinfo("Succès | نجاح", "Enregistré | تم الحفظ بنجاح")
        self.refresh()

    def refresh(self):
        for r in self.hist_tree.get_children(): self.hist_tree.delete(r)
        for r in db.get_all_distributions(): 
            self.hist_tree.insert("", "end", values=(r[0], r[1], f"{r[2]:,.0f}", r[4]))