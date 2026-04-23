import tkinter as tk
from tkinter import messagebox, ttk
from theme import ThemeManager as TM
from widgets import create_button, create_treeview, entry_row, combo_row, separator
import database as db
from svf_calculator import SVFCalculator

class FamiliesPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=TM.get_color("bg"))
        self._selected_id = None
        self._build()

    def _build(self):
        tk.Label(self, text="Gestion des Familles |العائلات ادارة", font=TM.FONTS["title"], fg=TM.get_color("accent"), bg=TM.get_color("bg")).pack(side="top", fill="x", padx=TM.SIZES["pad"]*2, pady=(TM.SIZES["pad"]*2, 4))
        separator(self).pack(side="top", fill="x", padx=TM.SIZES["pad"]*2, pady=4)

        sf = tk.Frame(self, bg=TM.get_color("bg"))
        sf.pack(side="top", fill="x", padx=TM.SIZES["pad"]*2, pady=4)
        tk.Label(sf, text="🔍 Recherche | بحث :", font=TM.FONTS["body"], fg=TM.get_color("text_muted"), bg=TM.get_color("bg")).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.do_search())
        tk.Entry(sf, textvariable=self.search_var, font=TM.FONTS["body"], bg=TM.get_color("card"), fg=TM.get_color("text"), insertbackground=TM.get_color("text"), relief="flat", width=38, highlightthickness=1, highlightcolor=TM.get_color("accent"), highlightbackground=TM.get_color("border")).pack(side="left", padx=8)

        bb = tk.Frame(self, bg=TM.get_color("bg"))
        bb.pack(side="bottom", pady=15)
        
        create_button(bb, "➕ Ajouter | إضافة", self.open_add_form).pack(side="left", padx=4)
        create_button(bb, "✏️ Modifier | تعديل", self.open_edit_form).pack(side="left", padx=4)
        create_button(bb, "🗑️ Supprimer | حذف", self.delete_family, "danger").pack(side="left", padx=4)
        create_button(bb, "👶 Enfants | الأطفال", self.open_children).pack(side="left", padx=4)
        create_button(bb, "📋 Fiche | الملف الكامل", self.open_detail).pack(side="left", padx=4)

        cols = ["id","name","phone","members","income","score", "cat"]
        heads = ["#", "Chef | رب العائلة", "Tél | الهاتف", "Membres | الأفراد", "Revenu | الدخل DA", "Score SVF | نقاط", "Catégorie | التصنيف"]
        widths = [45, 200, 110, 110, 120, 110, 150]
        self.container, self.tree = create_treeview(self, cols, heads, widths, height=10)
        self.container.pack(side="top", fill="both", expand=True, padx=TM.SIZES["pad"]*2, pady=(4, 10))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def load_families(self, rows=None):
        for r in self.tree.get_children(): self.tree.delete(r)
        data = rows if rows is not None else db.get_all_families()
        for r in data:
            score = r[20]
            cat = SVFCalculator.get_category(score)
            self.tree.insert("", "end", iid=str(r[0]), values=(r[0], r[1], r[3], r[11], f"{r[6]:,.0f}", score, cat))

    def do_search(self):
        q = self.search_var.get().strip()
        self.load_families(db.search_families(q) if q else None)

    def on_select(self, _):
        sel = self.tree.selection()
        self._selected_id = int(sel[0]) if sel else None

    def _get_row(self):
        if not self._selected_id:
            messagebox.showwarning("Attention | تنبيه", "Veuillez sélectionner une famille | يرجى اختيار عائلة.")
            return None
        return db.get_family_by_id(self._selected_id)

    def open_add_form(self): FamilyForm(self, title="Nouvelle Famille | عائلة اضافة", on_save=self._save_new)
    def open_edit_form(self):
        row = self._get_row()
        if row: FamilyForm(self, title="Modifier Famille | عائلة تعديل", on_save=self._save_edit, prefill=row)

    def _save_new(self, data):
        db.add_family(*data)
        self.load_families()
        messagebox.showinfo("Succès | نجاح", "Ajouté avec succès | تمت الإضافة بنجاح.")

    def _save_edit(self, data):
        db.update_family(self._selected_id, *data)
        self.load_families()
        messagebox.showinfo("Succès | نجاح", "Modifié avec succès | تم التعديل بنجاح.")

    def delete_family(self):
        row = self._get_row()
        if not row: return
        if messagebox.askyesno("Confirmation | تأكيد", f"Voulez-vous supprimer {row[1]} ? | هل تريد حذف العائلة {row[1]} ؟"):
            db.delete_family(self._selected_id)
            self._selected_id = None
            self.load_families()

    def open_children(self):
        row = self._get_row()
        if row: ChildrenWindow(self, row[0], row[1])

    def open_detail(self):
        row = self._get_row()
        if row: FamilyDetailWindow(self, row)

    def refresh(self): self.load_families()


class FamilyForm(tk.Toplevel):
    EMPLOY = ["Salarie CDI | موظف دائم", "Salarie CDD | مؤقت", "Independant | حر", "Retraite | متقاعد", "Chomeur | بطال", "Aides sociales | مساعدات", "Autre | آخر"]
    MARITAL = ["Marie | متزوج(ة)", "Veuf | أرمل(ة)", "Divorce | مطلق(ة)"]
    SOCIAL = ["Difficile | حالة صعبة", "Veuve | أرملة", "Divorcee | مطلقة", "Orphelins | أيتام"]
    HEALTH = ["Bonne | جيدة", "Maladie chronique | مرض مزمن", "Handicap | إعاقة"]
    YESNO = ["Non | لا", "Oui | نعم"]
    HTYPE = ["Maison | منزل مستقل", "Appartement | شقة", "Logement temporaire | سكن مؤقت"]
    HCOND = ["Bon | جيد", "Moyen | متوسط", "Mauvais | سيء"]

    def __init__(self, parent, title, on_save, prefill=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=TM.get_color("bg"))
        self.grab_set()
        self._on_save = on_save
        self._p = prefill
        
        self.geometry("820x560")
        self.minsize(750, 500)
        self._build(title)

    def _build(self, title):
        tk.Label(self, text=title, font=TM.FONTS["heading"], fg=TM.get_color("accent"), bg=TM.get_color("bg")).pack(side="top", pady=(10, 2))
        separator(self).pack(side="top", fill="x", padx=16)

        bf = tk.Frame(self, bg=TM.get_color("bg"))
        bf.pack(side="bottom", pady=10)
        create_button(bf, "💾 Enregistrer | حفظ", self._save).pack(side="left", padx=10)
        create_button(bf, "✖ Annuler | إلغاء", self.destroy, "danger").pack(side="left", padx=10)

        nb = ttk.Notebook(self, style="Custom.TNotebook")
        nb.pack(side="top", fill="both", expand=True, padx=12, pady=4)

        t1 = tk.Frame(nb, bg=TM.get_color("card")); nb.add(t1, text=" Identité | الهوية ")
        t2 = tk.Frame(nb, bg=TM.get_color("card")); nb.add(t2, text=" Finances | المالية ")
        t3 = tk.Frame(nb, bg=TM.get_color("card")); nb.add(t3, text=" Logement | السكن ")
        t4 = tk.Frame(nb, bg=TM.get_color("card")); nb.add(t4, text=" Santé | الصحة ")

        self._tab_identite(t1)
        self._tab_finances(t2)
        self._tab_logement(t3)
        self._tab_sante(t4)
        if self._p: self._prefill()

    def _r(self, p, lbl, w=24): return entry_row(p, lbl, width=w)
    def _c(self, p, lbl, vals, w=26): return combo_row(p, lbl, vals, width=w)
    def _pk(self, f): f.pack(fill="x", padx=20, pady=2)

    def _tab_identite(self, t):
        tk.Label(t, text="Informations d'identité | معلومات الهوية", font=TM.FONTS["body_b"], fg=TM.get_color("accent"), bg=TM.get_color("card")).pack(pady=(5, 2))
        f, self.v_head, _ = self._r(t, "Nom Chef | اسم رب الأسرة :"); self._pk(f)
        f, self.v_spouse, _ = self._r(t, "Conjoint(e) | اسم الزوج(ة) :"); self._pk(f)
        f, self.v_phone, _ = self._r(t, "Téléphone | الهاتف :"); self._pk(f)
        f, self.v_addr, _ = self._r(t, "Adresse | العنوان :"); self._pk(f)
        f, self.v_ccp, _ = self._r(t, "N° CCP | رقم الحساب البريدي :"); self._pk(f)
        f, self.v_members, _ = self._r(t, "Nb Membres | عدد الأفراد :", 6); self._pk(f); self.v_members.set("1")
        f, self.v_marital, _ = self._c(t, "Sit. Familiale | الحالة الزوجية :", self.MARITAL); self._pk(f)
        f, self.v_social, _ = self._c(t, "Sit. Sociale | الوضع الاجتماعي :", self.SOCIAL); self._pk(f)

    def _tab_finances(self, t):
        tk.Label(t, text="Situation financière | الوضع المالي", font=TM.FONTS["body_b"], fg=TM.get_color("accent"), bg=TM.get_color("card")).pack(pady=(5, 2))
        f, self.v_income, _ = self._r(t, "Revenu (DA) | الدخل الشهري :", 14); self._pk(f); self.v_income.set("0")
        f, self.v_rent, _ = self._r(t, "Loyer (DA) | الإيجار :", 14); self._pk(f); self.v_rent.set("0")
        f, self.v_src, _ = self._r(t, "Sources | مصادر الدخل :", 24); self._pk(f)
        f, self.v_employ, _ = self._c(t, "Type d'emploi | نوع العمل :", self.EMPLOY); self._pk(f)

    def _tab_logement(self, t):
        tk.Label(t, text="Conditions de logement | ظروف السكن", font=TM.FONTS["body_b"], fg=TM.get_color("accent"), bg=TM.get_color("card")).pack(pady=(5, 2))
        f, self.v_renting, _ = self._c(t, "Locataire | مستأجر :", self.YESNO); self._pk(f)
        f, self.v_htype, _ = self._c(t, "Type | نوع السكن :", self.HTYPE); self._pk(f)
        f, self.v_hsurf, _ = self._r(t, "Surface (m²) | المساحة :", 10); self._pk(f); self.v_hsurf.set("0")
        f, self.v_hrooms, _ = self._r(t, "Pièces | عدد الغرف :", 6); self._pk(f); self.v_hrooms.set("1")
        f, self.v_hcond, _ = self._c(t, "État | الحالة العامة :", self.HCOND); self._pk(f)

    def _tab_sante(self, t):
        tk.Label(t, text="Santé de la famille | صحة الأسرة", font=TM.FONTS["body_b"], fg=TM.get_color("accent"), bg=TM.get_color("card")).pack(pady=(5, 2))
        f, self.v_health, _ = self._c(t, "État santé | الحالة الصحية :", self.HEALTH); self._pk(f)
        f, self.v_chronic, _ = self._r(t, "Maladie chro. | أمراض مزمنة :", 24); self._pk(f)

    def _prefill(self):
        p = self._p
        self.v_head.set(p[1] or ""); self.v_spouse.set(p[2] or ""); self.v_phone.set(p[3] or ""); self.v_addr.set(p[4] or "")
        self.v_ccp.set(p[5] or ""); self.v_income.set(str(p[6])); self.v_rent.set(str(p[7])); self.v_employ.set(p[8])
        self.v_src.set(p[9] or ""); self.v_marital.set(p[10]); self.v_members.set(str(p[11])); self.v_social.set(p[12])
        self.v_health.set(p[13]); self.v_chronic.set(p[14] or ""); self.v_renting.set(p[15]); self.v_htype.set(p[16])
        self.v_hsurf.set(str(p[17])); self.v_hrooms.set(str(p[18])); self.v_hcond.set(p[19])

    def _save(self):
        head = self.v_head.get().strip()
        if not head:
            messagebox.showerror("Erreur | خطأ", "Nom obligatoire | الاسم إلزامي.", parent=self)
            return
        try:
            income = float(self.v_income.get() or 0)
            rent = float(self.v_rent.get() or 0)
            surf = float(self.v_hsurf.get() or 0)
            rooms = int(self.v_hrooms.get() or 1)
            members = int(self.v_members.get() or 1)
        except ValueError:
            messagebox.showerror("Erreur | خطأ", "Vérifiez les nombres | تحقق من الأرقام.", parent=self)
            return
        
        family_data = {
            'monthly_income': income,
            'children_count': members - 1,
            'social_status': self.v_social.get(),
            'health_status': self.v_health.get(),
            'is_renting': self.v_renting.get(),
            'benefit_count': len(db.get_distributions_by_family(self._p[0])) if self._p else 0
        }
        svf_score = SVFCalculator.calculate(family_data)

        self._on_save((
            head, self.v_spouse.get().strip(), self.v_phone.get().strip(), self.v_addr.get().strip(),
            self.v_ccp.get().strip() or None, income, rent, self.v_employ.get(), self.v_src.get().strip(),
            self.v_marital.get(), members, self.v_social.get(), self.v_health.get(), self.v_chronic.get().strip(),
            self.v_renting.get(), self.v_htype.get(), surf, rooms, self.v_hcond.get(), svf_score
        ))
        self.destroy()


class ChildrenWindow(tk.Toplevel):
    def __init__(self, parent, fid, name):
        super().__init__(parent); self.title(f"Enfants | أطفال - {name}"); self.configure(bg=TM.get_color("bg")); self.geometry("800x500"); self.fid = fid; self._build(); self.load()
    def _build(self):
        self.c, self.tree = create_treeview(self, ["id","n","d"], ["#", "Nom | الاسم", "Date Nais. | تاريخ الميلاد"], [50,200,150]); self.c.pack(fill="both", expand=True, padx=20, pady=20)
    def load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        for r in db.get_children_by_family(self.fid): self.tree.insert("", "end", values=(r[0], r[2], r[3]))


class FamilyDetailWindow(tk.Toplevel):
    def __init__(self, parent, row):
        super().__init__(parent); self.title(row[1]); self.configure(bg=TM.get_color("bg")); self.geometry("600x400")
        tk.Label(self, text=f"Fiche Famille | ملف العائلة : {row[1]}", font=TM.FONTS["title"], fg=TM.get_color("accent"), bg=TM.get_color("bg")).pack(pady=20)
        tk.Label(self, text=f"Score SVF | نقاط : {row[20]}", font=TM.FONTS["heading"], fg=TM.get_color("text"), bg=TM.get_color("bg")).pack(pady=10)
        create_button(self, "Fermer | إغلاق", self.destroy).pack(pady=20)