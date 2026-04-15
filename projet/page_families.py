import tkinter as tk
from tkinter import messagebox, ttk
import theme as th
from widgets import (styled_button, danger_button, build_treeview,
                     section_title, entry_row, combo_row, separator)
import database as db

class FamiliesPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=th.BG_DARK)
        self._selected_id = None
        self._build()
        self.load_families()

    def _build(self):
        tk.Label(self, text="Gestion des Familles  |  إدارة العائلات",
                 font=th.FONT_TITLE, fg=th.ACCENT, bg=th.BG_DARK).pack(
                     fill="x", padx=th.PAD*2, pady=(th.PAD*2, 4))
        separator(self, bg=th.ACCENT).pack(fill="x", padx=th.PAD*2, pady=4)

        sf = tk.Frame(self, bg=th.BG_DARK)
        sf.pack(fill="x", padx=th.PAD*2, pady=4)
        tk.Label(sf, text="🔍 Recherche / بحث :", font=th.FONT_BODY,
                 fg=th.TEXT_MUTED, bg=th.BG_DARK).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.do_search())
        tk.Entry(sf, textvariable=self.search_var, font=th.FONT_BODY,
                 bg=th.BG_CARD, fg=th.TEXT_WHITE, insertbackground=th.TEXT_WHITE,
                 relief="flat", width=38,
                 highlightthickness=1, highlightcolor=th.ACCENT,
                 highlightbackground=th.BORDER).pack(side="left", padx=8)

        cols   = ["id","name","spouse","phone","marital","members","job","income","housing","score"]
        heads  = ["#","Chef famille","Époux/se","Tél","Situation","Membres","Emploi","Revenu DA","Logement","Score"]
        widths = [35,160,140,100,80,60,110,90,100,55]
        tf, self.tree = build_treeview(self, cols, heads, widths, height=15)
        tf.pack(fill="both", expand=True, padx=th.PAD*2, pady=(4, 0))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        bb = tk.Frame(self, bg=th.BG_DARK)
        bb.pack(pady=8)
        styled_button(bb, "➕ Ajouter / إضافة",       self.open_add_form).pack(side="left", padx=4)
        styled_button(bb, "✏️ Modifier / تعديل",      self.open_edit_form, color=th.ACCENT2, fg=th.TEXT_WHITE).pack(side="left", padx=4)
        danger_button(bb, "🗑️ Supprimer / حذف",       self.delete_family).pack(side="left", padx=4)
        styled_button(bb, "👶 Enfants / أطفال",       self.open_children, color="#5B9BD5", fg=th.TEXT_WHITE).pack(side="left", padx=4)
        styled_button(bb, "📋 Fiche complète / ملف",  self.open_detail,   color="#7D5A9E", fg=th.TEXT_WHITE).pack(side="left", padx=4)
        styled_button(bb, "📤 Distribution / توزيع",  self.open_distribution, color="#9B59B6", fg=th.TEXT_WHITE).pack(side="left", padx=4)

    def load_families(self, rows=None):
        for r in self.tree.get_children():
            self.tree.delete(r)
        data = rows if rows is not None else db.get_all_families()
        for r in data:
            self.tree.insert("", "end", iid=str(r[0]),
                             values=(r[0], r[1], r[2], r[3],
                                     r[10], r[11], r[8],
                                     f"{r[6]:,.0f}", r[16], f"{r[20]:.1f}"))

    def do_search(self):
        q = self.search_var.get().strip()
        self.load_families(db.search_families(q) if q else None)

    def on_select(self, _):
        sel = self.tree.selection()
        self._selected_id = int(sel[0]) if sel else None

    def _get_row(self):
        if not self._selected_id:
            messagebox.showwarning("Sélection",
                                   "Veuillez sélectionner une famille.\nيرجى اختيار عائلة.")
            return None
        return db.get_family_by_id(self._selected_id)

    def open_add_form(self):
        FamilyForm(self, title="Nouvelle Famille  |  عائلة جديدة",
                   on_save=self._save_new)

    def open_edit_form(self):
        row = self._get_row()
        if row:
            FamilyForm(self, title="Modifier Famille  |  تعديل",
                       on_save=self._save_edit, prefill=row)

    def _save_new(self, data):
        db.add_family(*data)
        self.load_families()
        messagebox.showinfo("✅", "Famille ajoutée avec succès.\nتمت إضافة العائلة.")

    def _save_edit(self, data):
        db.update_family(self._selected_id, *data)
        self.load_families()
        messagebox.showinfo("✅", "Famille mise à jour.\nتم التعديل.")

    def delete_family(self):
        row = self._get_row()
        if not row:
            return
        if messagebox.askyesno("Confirmer / تأكيد",
                               f"Supprimer la famille de {row[1]} ?\nحذف عائلة {row[1]} ؟"):
            db.delete_family(self._selected_id)
            self._selected_id = None
            self.load_families()

    def open_children(self):
        row = self._get_row()
        if row:
            ChildrenWindow(self, row[0], row[1])

    def open_detail(self):
        row = self._get_row()
        if row:
            FamilyDetailWindow(self, row)

    def open_distribution(self):
        row = self._get_row()
        if row:
            DistributionDialog(self, row[0], row[1], on_done=self.load_families)

    def refresh(self):
        self.load_families()


# ══════════════════════════════════════════════════════
#  FAMILY FORM  (4 onglets)
# ══════════════════════════════════════════════════════
class FamilyForm(tk.Toplevel):
    EMPLOY  = ["Salarie CDI","Salarie CDD","Independant","Retraite","Chomeur","Aides sociales","Autre"]
    MARITAL = ["Marie","Veuf","Divorce"]
    SOCIAL  = ["Difficile","Veuve","Divorcee","Orphelins"]
    HEALTH  = ["Bonne","Maladie chronique","Handicap"]
    YESNO   = ["Non","Oui"]
    HTYPE   = ["Maison","Appartement","Logement temporaire"]
    HCOND   = ["Bon","Moyen","Mauvais"]

    def __init__(self, parent, title, on_save, prefill=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=th.BG_DARK)
        self.grab_set()
        self._on_save = on_save
        self._p = prefill
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"700x600+{(sw-700)//2}+{(sh-600)//2}")
        self._build()

    def _build(self):
        tk.Label(self, text=self.title(), font=th.FONT_HEADING,
                 fg=th.ACCENT, bg=th.BG_DARK).pack(pady=(12, 4))
        separator(self, bg=th.ACCENT).pack(fill="x", padx=16)

        apply_ttk_styles_nb()
        nb = ttk.Notebook(self, style="D.TNotebook")
        nb.pack(fill="both", expand=True, padx=12, pady=6)

        t1 = tk.Frame(nb, bg=th.BG_CARD); nb.add(t1, text="  Identité  ")
        t2 = tk.Frame(nb, bg=th.BG_CARD); nb.add(t2, text="  Finances  ")
        t3 = tk.Frame(nb, bg=th.BG_CARD); nb.add(t3, text="  Logement  ")
        t4 = tk.Frame(nb, bg=th.BG_CARD); nb.add(t4, text="  Santé     ")

        self._tab_identite(t1)
        self._tab_finances(t2)
        self._tab_logement(t3)
        self._tab_sante(t4)
        if self._p:
            self._prefill()

        separator(self, bg=th.BORDER).pack(fill="x", padx=16, pady=4)
        bf = tk.Frame(self, bg=th.BG_DARK)
        bf.pack(pady=8)
        styled_button(bf, "💾 Enregistrer / حفظ", self._save).pack(side="left", padx=10)
        danger_button(bf, "✖ Annuler / إلغاء",   self.destroy).pack(side="left", padx=10)

    def _r(self, p, lbl, w=24): return entry_row(p, lbl, bg=th.BG_CARD, width=w)
    def _c(self, p, lbl, vals, w=18): return combo_row(p, lbl, vals, bg=th.BG_CARD, width=w)
    def _pk(self, f): f.pack(fill="x", padx=20, pady=3)

    def _tab_identite(self, t):
        tk.Label(t, text="Informations d'identité / معلومات الهوية",
                 font=th.FONT_BODY_B, fg=th.ACCENT, bg=th.BG_CARD).pack(pady=(10, 4))
        f, self.v_head,    _ = self._r(t, "Nom chef de famille / اسم رب الأسرة :"); self._pk(f)
        f, self.v_spouse,  _ = self._r(t, "Nom époux/se / اسم الزوج(ة) :");         self._pk(f)
        f, self.v_phone,   _ = self._r(t, "Téléphone / الهاتف :");                   self._pk(f)
        f, self.v_addr,    _ = self._r(t, "Adresse / العنوان :");                    self._pk(f)
        f, self.v_ccp,     _ = self._r(t, "N° CCP / رقم الحساب البريدي :");          self._pk(f)
        f, self.v_members, _ = self._r(t, "Nombre de membres / عدد الأفراد :", 6);   self._pk(f)
        self.v_members.set("1")
        f, self.v_marital, _ = self._c(t, "Situation matrimoniale / الوضع الزوجي :", self.MARITAL); self._pk(f)
        f, self.v_social,  _ = self._c(t, "Situation sociale / الوضع الاجتماعي :", self.SOCIAL);    self._pk(f)

    def _tab_finances(self, t):
        tk.Label(t, text="Situation financière / الوضع المالي",
                 font=th.FONT_BODY_B, fg=th.ACCENT, bg=th.BG_CARD).pack(pady=(10, 4))
        f, self.v_income, _ = self._r(t, "Revenu mensuel (DA) / الدخل الشهري :", 14); self._pk(f)
        self.v_income.set("0")
        f, self.v_rent,   _ = self._r(t, "Montant loyer (DA) / مبلغ الإيجار :", 14);  self._pk(f)
        self.v_rent.set("0")
        f, self.v_src,    _ = self._r(t, "Sources de revenus / مصادر الدخل :", 24);   self._pk(f)
        f, self.v_employ, _ = self._c(t, "Type d'emploi / نوع العمل :", self.EMPLOY);  self._pk(f)

    def _tab_logement(self, t):
        tk.Label(t, text="Conditions de logement / ظروف السكن",
                 font=th.FONT_BODY_B, fg=th.ACCENT, bg=th.BG_CARD).pack(pady=(10, 4))
        f, self.v_renting, _ = self._c(t, "Locataire / مستأجر :", self.YESNO);           self._pk(f)
        f, self.v_htype,   _ = self._c(t, "Type logement / نوع السكن :", self.HTYPE);     self._pk(f)
        f, self.v_hsurf,   _ = self._r(t, "Surface (m²) / المساحة :", 10);                self._pk(f)
        self.v_hsurf.set("0")
        f, self.v_hrooms,  _ = self._r(t, "Nombre de pièces / عدد الغرف :", 6);           self._pk(f)
        self.v_hrooms.set("1")
        f, self.v_hcond,   _ = self._c(t, "État général / الحالة العامة :", self.HCOND);  self._pk(f)

    def _tab_sante(self, t):
        tk.Label(t, text="Santé de la famille / صحة الأسرة",
                 font=th.FONT_BODY_B, fg=th.ACCENT, bg=th.BG_CARD).pack(pady=(10, 4))
        f, self.v_health,  _ = self._c(t, "État de santé / الحالة الصحية :", self.HEALTH); self._pk(f)
        f, self.v_chronic, _ = self._r(t, "Maladies chroniques / أمراض مزمنة :", 24);      self._pk(f)

    def _prefill(self):
        p = self._p
        self.v_head.set(p[1] or "");   self.v_spouse.set(p[2] or "")
        self.v_phone.set(p[3] or "");  self.v_addr.set(p[4] or "")
        self.v_ccp.set(p[5] or "");    self.v_income.set(str(p[6]))
        self.v_rent.set(str(p[7]));    self.v_employ.set(p[8])
        self.v_src.set(p[9] or "");    self.v_marital.set(p[10])
        self.v_members.set(str(p[11]));self.v_social.set(p[12])
        self.v_health.set(p[13]);      self.v_chronic.set(p[14] or "")
        self.v_renting.set(p[15]);     self.v_htype.set(p[16])
        self.v_hsurf.set(str(p[17]));  self.v_hrooms.set(str(p[18]))
        self.v_hcond.set(p[19])

    def _save(self):
        head = self.v_head.get().strip()
        if not head:
            messagebox.showerror("Erreur", "Nom obligatoire.\nالاسم إلزامي.", parent=self)
            return
        try:
            income  = float(self.v_income.get() or 0)
            rent    = float(self.v_rent.get() or 0)
            surf    = float(self.v_hsurf.get() or 0)
            rooms   = int(self.v_hrooms.get() or 1)
            members = int(self.v_members.get() or 1)
        except ValueError:
            messagebox.showerror("Erreur",
                "Vérifiez les champs numériques.\nتحقق من الحقول الرقمية.", parent=self)
            return
        self._on_save((
            head, self.v_spouse.get().strip(),
            self.v_phone.get().strip(), self.v_addr.get().strip(),
            self.v_ccp.get().strip() or None,
            income, rent, self.v_employ.get(), self.v_src.get().strip(),
            self.v_marital.get(), members, self.v_social.get(),
            self.v_health.get(), self.v_chronic.get().strip(),
            self.v_renting.get(), self.v_htype.get(), surf,
            rooms, self.v_hcond.get()
        ))
        self.destroy()


def apply_ttk_styles_nb():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("D.TNotebook",     background=th.BG_DARK, borderwidth=0)
    s.configure("D.TNotebook.Tab", background=th.BG_SIDEBAR, foreground=th.TEXT_MUTED,
                font=th.FONT_BODY_B, padding=[10, 5])
    s.map("D.TNotebook.Tab",
          background=[("selected", th.BG_CARD)],
          foreground=[("selected", th.ACCENT)])


# ══════════════════════════════════════════════════════
#  CHILDREN WINDOW
# ══════════════════════════════════════════════════════
class ChildrenWindow(tk.Toplevel):
    GENDER  = ["Masculin","Feminin"]
    YESNO   = ["Non","Oui"]
    SCHOOL  = ["Scolarise","Non scolarise","Universitaire","Formation professionnelle"]
    RESULTS = ["Excellent","Bien","Moyen","Faible",""]
    HEALTH  = ["Bonne","Maladie chronique","Handicap"]

    def __init__(self, parent, family_id, family_name):
        super().__init__(parent)
        self.title(f"Enfants — {family_name}  |  أطفال")
        self.configure(bg=th.BG_DARK)
        self.grab_set()
        self.fid   = family_id
        self.fname = family_name
        self._sel  = None
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"980x660+{(sw-980)//2}+{(sh-660)//2}")
        self._build()
        self._load()

    def _build(self):
        tk.Label(self, text=f"Enfants de : {self.fname}  |  أطفال",
                 font=th.FONT_HEADING, fg=th.ACCENT, bg=th.BG_DARK).pack(pady=(12, 4))
        separator(self, bg=th.ACCENT).pack(fill="x", padx=16)

        cols  = ["id","name","dob","gender","orphan","school","level","health","follow","vaccines"]
        heads = ["#","Nom","Naissance","Sexe","Orphelin","Scolarité","Niveau","Santé","Suivi","Vaccins"]
        widths= [35,130,100,75,65,120,90,100,60,65]
        tf, self.tree = build_treeview(self, cols, heads, widths, height=9)
        tf.pack(fill="both", expand=True, padx=16, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_sel)

        apply_ttk_styles_nb()
        nb = ttk.Notebook(self, style="D.TNotebook")
        nb.pack(fill="x", padx=16, pady=4)

        ti = tk.Frame(nb, bg=th.BG_CARD); nb.add(ti, text="  Identité / Scolarité  ")
        ts = tk.Frame(nb, bg=th.BG_CARD); nb.add(ts, text="  Santé / Besoins  ")

        # Tab 1
        row1 = tk.Frame(ti, bg=th.BG_CARD); row1.pack(fill="x", padx=10, pady=4)
        f, self.vc_name,   _ = entry_row(row1, "Nom :", bg=th.BG_CARD, width=16);           f.pack(side="left", padx=4)
        f, self.vc_dob,    _ = entry_row(row1, "Naissance (AAAA-MM-JJ) :", bg=th.BG_CARD, width=12); f.pack(side="left", padx=4)
        self.vc_dob.set("YYYY-MM-DD")
        f, self.vc_gender, _ = combo_row(row1, "Sexe :", self.GENDER, bg=th.BG_CARD, width=10); f.pack(side="left", padx=4)
        f, self.vc_orphan, _ = combo_row(row1, "Orphelin :", self.YESNO, bg=th.BG_CARD, width=6);  f.pack(side="left", padx=4)

        row2 = tk.Frame(ti, bg=th.BG_CARD); row2.pack(fill="x", padx=10, pady=4)
        f, self.vc_school,  _ = combo_row(row2, "Scolarité :", self.SCHOOL, bg=th.BG_CARD, width=18); f.pack(side="left", padx=4)
        f, self.vc_level,   _ = entry_row(row2, "Niveau :", bg=th.BG_CARD, width=12);  f.pack(side="left", padx=4)
        f, self.vc_sname,   _ = entry_row(row2, "Établissement :", bg=th.BG_CARD, width=16); f.pack(side="left", padx=4)

        row3 = tk.Frame(ti, bg=th.BG_CARD); row3.pack(fill="x", padx=10, pady=4)
        f, self.vc_results, _ = combo_row(row3, "Résultats :", self.RESULTS, bg=th.BG_CARD, width=12); f.pack(side="left", padx=4)
        f, self.vc_dropout, _ = combo_row(row3, "Risque décrochage :", self.YESNO, bg=th.BG_CARD, width=6); f.pack(side="left", padx=4)

        # Tab 2
        row4 = tk.Frame(ts, bg=th.BG_CARD); row4.pack(fill="x", padx=10, pady=4)
        f, self.vc_health,   _ = combo_row(row4, "Santé :", self.HEALTH, bg=th.BG_CARD, width=16);  f.pack(side="left", padx=4)
        f, self.vc_disease,  _ = entry_row(row4, "Type maladie :", bg=th.BG_CARD, width=16);        f.pack(side="left", padx=4)
        f, self.vc_allergy,  _ = entry_row(row4, "Allergies :", bg=th.BG_CARD, width=14);           f.pack(side="left", padx=4)

        row5 = tk.Frame(ts, bg=th.BG_CARD); row5.pack(fill="x", padx=10, pady=4)
        f, self.vc_follow,   _ = combo_row(row5, "Suivi médical :", self.YESNO, bg=th.BG_CARD, width=6);   f.pack(side="left", padx=4)
        f, self.vc_vaccines, _ = combo_row(row5, "Vaccins à jour :", self.YESNO, bg=th.BG_CARD, width=6);  f.pack(side="left", padx=4)
        f, self.vc_needs,    _ = entry_row(row5, "Besoins spécifiques :", bg=th.BG_CARD, width=24);         f.pack(side="left", padx=4)

        bb = tk.Frame(self, bg=th.BG_DARK); bb.pack(pady=6)
        styled_button(bb, "➕ Ajouter enfant",   self._add).pack(side="left", padx=4)
        styled_button(bb, "✏️ Modifier",         self._edit, color=th.ACCENT2, fg=th.TEXT_WHITE).pack(side="left", padx=4)
        danger_button(bb, "🗑️ Supprimer",        self._delete).pack(side="left", padx=4)

    def _load(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for row in db.get_children_by_family(self.fid):
            self.tree.insert("", "end", iid=str(row[0]),
                             values=(row[0],row[2],row[3],row[4],row[5],
                                     row[6],row[7],row[11],row[14],row[15]))

    def _on_sel(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        self._sel = int(sel[0])
        for row in db.get_children_by_family(self.fid):
            if row[0] == self._sel:
                self.vc_name.set(row[2]);     self.vc_dob.set(row[3])
                self.vc_gender.set(row[4]);   self.vc_orphan.set(row[5])
                self.vc_school.set(row[6]);   self.vc_level.set(row[7] or "")
                self.vc_sname.set(row[8] or ""); self.vc_results.set(row[9] or "")
                self.vc_dropout.set(row[10]); self.vc_health.set(row[11])
                self.vc_disease.set(row[12] or ""); self.vc_allergy.set(row[13] or "")
                self.vc_follow.set(row[14]);  self.vc_vaccines.set(row[15])
                self.vc_needs.set(row[16] or "")
                break

    def _get_data(self):
        name = self.vc_name.get().strip()
        dob  = self.vc_dob.get().strip()
        if not name or not dob or dob == "YYYY-MM-DD":
            messagebox.showerror("Erreur", "Nom et date obligatoires.", parent=self)
            return None
        return (name, dob, self.vc_gender.get(), self.vc_orphan.get(),
                self.vc_school.get(), self.vc_level.get(), self.vc_sname.get(),
                self.vc_results.get(), self.vc_dropout.get(),
                self.vc_health.get(), self.vc_disease.get(),
                self.vc_allergy.get(), self.vc_follow.get(),
                self.vc_vaccines.get(), self.vc_needs.get())

    def _add(self):
        data = self._get_data()
        if data:
            db.add_child(self.fid, *data)
            self._load()

    def _edit(self):
        if not self._sel:
            return
        data = self._get_data()
        if data:
            db.update_child(self._sel, *data)
            self._load()

    def _delete(self):
        if not self._sel:
            return
        if messagebox.askyesno("Confirmer", "Supprimer cet enfant ?", parent=self):
            db.delete_child(self._sel)
            self._sel = None
            self._load()


# ══════════════════════════════════════════════════════
#  FAMILY DETAIL WINDOW
# ══════════════════════════════════════════════════════
class FamilyDetailWindow(tk.Toplevel):
    def __init__(self, parent, row):
        super().__init__(parent)
        self.title(f"Fiche complète — {row[1]}")
        self.configure(bg=th.BG_DARK)
        self.grab_set()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"720x700+{(sw-720)//2}+{(sh-700)//2}")
        self._build(row)

    def _line(self, parent, lbl, val):
        f = tk.Frame(parent, bg=th.BG_CARD)
        tk.Label(f, text=lbl + "  ", font=th.FONT_BODY_B, fg=th.TEXT_MUTED,
                 bg=th.BG_CARD, width=30, anchor="w").pack(side="left")
        tk.Label(f, text=str(val), font=th.FONT_BODY, fg=th.TEXT_WHITE,
                 bg=th.BG_CARD, anchor="w").pack(side="left")
        return f

    def _build(self, p):
        tk.Label(self, text=f"Fiche Famille — {p[1]}",
                 font=th.FONT_TITLE, fg=th.ACCENT, bg=th.BG_DARK).pack(pady=(16, 4))
        separator(self, bg=th.ACCENT).pack(fill="x", padx=20)

        canvas = tk.Canvas(self, bg=th.BG_DARK, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=th.BG_DARK)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        vsb.pack(side="right", fill="y")

        sections = [
            ("👤 Identité / الهوية", [
                ("Nom chef de famille", p[1]),
                ("Nom époux/se",        p[2] or "—"),
                ("Téléphone",           p[3] or "—"),
                ("Adresse",             p[4] or "—"),
                ("N° CCP",              p[5] or "—"),
                ("Situation matrimoniale", p[10]),
                ("Nombre de membres",   p[11]),
                ("Situation sociale",   p[12]),
            ]),
            ("💼 Finances / المالية", [
                ("Revenu mensuel (DA)", f"{p[6]:,.0f}"),
                ("Loyer (DA)",          f"{p[7]:,.0f}"),
                ("Sources de revenus",  p[9] or "—"),
                ("Type d'emploi",       p[8]),
            ]),
            ("🏠 Logement / السكن", [
                ("Locataire",           p[15]),
                ("Type logement",       p[16]),
                ("Surface (m²)",        p[17]),
                ("Nombre de pièces",    p[18]),
                ("État général",        p[19]),
            ]),
            ("❤️ Santé / الصحة", [
                ("État de santé",       p[13]),
                ("Maladies chroniques", p[14] or "—"),
            ]),
        ]

        for sec_title, lines in sections:
            sec = tk.Frame(inner, bg=th.BG_CARD,
                           highlightthickness=1, highlightbackground=th.BORDER)
            sec.pack(fill="x", pady=6, padx=4)
            tk.Label(sec, text=sec_title, font=th.FONT_HEADING,
                     fg=th.ACCENT, bg=th.BG_CARD).pack(anchor="w", padx=12, pady=(8, 4))
            separator(sec, bg=th.BORDER).pack(fill="x", padx=12)
            for lbl, val in lines:
                self._line(sec, lbl, val).pack(fill="x", padx=20, pady=2)
            tk.Label(sec, text="", bg=th.BG_CARD).pack()

        # Historique des aides
        sec = tk.Frame(inner, bg=th.BG_CARD,
                       highlightthickness=1, highlightbackground=th.BORDER)
        sec.pack(fill="x", pady=6, padx=4)
        tk.Label(sec, text="📋 Historique des aides / سجل المساعدات",
                 font=th.FONT_HEADING, fg=th.ACCENT, bg=th.BG_CARD).pack(anchor="w", padx=12, pady=(8, 4))
        separator(sec, bg=th.BORDER).pack(fill="x", padx=12)
        dists = db.get_distributions_by_family(p[0])
        total_recu = 0
        if dists:
            for d in dists:
                total_recu += d[2]
                txt = f"  {d[5]}  •  {d[2]:,.0f} DA  •  {d[3]}  •  {d[4]}"
                tk.Label(sec, text=txt, font=th.FONT_BODY,
                         fg=th.TEXT_WHITE, bg=th.BG_CARD).pack(anchor="w", padx=20, pady=2)
            tk.Label(sec, text=f"  Total reçu : {total_recu:,.0f} DA",
                     font=th.FONT_BODY_B, fg=th.ACCENT, bg=th.BG_CARD).pack(anchor="w", padx=20, pady=4)
        else:
            tk.Label(sec, text="  Aucune aide enregistrée.",
                     font=th.FONT_BODY, fg=th.TEXT_MUTED, bg=th.BG_CARD).pack(anchor="w", padx=20, pady=6)

        children = db.get_children_by_family(p[0])
        if children:
            tk.Label(sec, text=f"  Enfants enregistrés : {len(children)}",
                     font=th.FONT_BODY_B, fg=th.ACCENT2, bg=th.BG_CARD).pack(anchor="w", padx=20, pady=4)
        tk.Label(sec, text="", bg=th.BG_CARD).pack()

        styled_button(self, "✖ Fermer", self.destroy,
                      color=th.DANGER, fg=th.TEXT_WHITE).pack(pady=10)


# ══════════════════════════════════════════════════════
#  DISTRIBUTION DIALOG
# ══════════════════════════════════════════════════════
class DistributionDialog(tk.Toplevel):
    TYPES = ["Financiere","Alimentaire","Medicale","Fournitures","Autre"]

    def __init__(self, parent, family_id, family_name, on_done):
        super().__init__(parent)
        self.title(f"Distribution — {family_name}")
        self.configure(bg=th.BG_DARK)
        self.grab_set()
        self.resizable(False, False)
        self._fid     = family_id
        self._on_done = on_done
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"460x310+{(sw-460)//2}+{(sh-310)//2}")
        self._build(family_name)

    def _build(self, name):
        tk.Label(self, text=f"Aide pour : {name}",
                 font=th.FONT_HEADING, fg=th.ACCENT, bg=th.BG_DARK).pack(pady=(16, 4))
        separator(self, bg=th.ACCENT).pack(fill="x", padx=20)

        inner = tk.Frame(self, bg=th.BG_DARK)
        inner.pack(padx=30, pady=12, fill="x")
        f, self.v_amt,  _ = entry_row(inner, "Montant (DA) / المبلغ :", bg=th.BG_DARK, width=16); f.pack(fill="x", pady=4)
        f, self.v_type, _ = combo_row(inner, "Type d'aide / نوع المساعدة :", self.TYPES, bg=th.BG_DARK, width=16); f.pack(fill="x", pady=4)
        f, self.v_note, _ = entry_row(inner, "Notes / ملاحظات :", bg=th.BG_DARK, width=22); f.pack(fill="x", pady=4)

        bb = tk.Frame(self, bg=th.BG_DARK); bb.pack(pady=10)
        styled_button(bb, "💾 Valider / تأكيد", self._save).pack(side="left", padx=8)
        danger_button(bb, "✖ Annuler / إلغاء",  self.destroy).pack(side="left", padx=8)

    def _save(self):
        try:
            amt = float(self.v_amt.get())
        except ValueError:
            messagebox.showerror("Erreur", "Montant invalide.", parent=self)
            return
        bal = db.get_balance()
        if amt > bal:
            messagebox.showerror("Solde insuffisant",
                                 f"Solde disponible : {bal:,.0f} DA", parent=self)
            return
        db.add_distribution(self._fid, amt, self.v_type.get(), self.v_note.get())
        messagebox.showinfo("✅", "Aide enregistrée.\nتم تسجيل المساعدة.", parent=self)
        self._on_done()
        self.destroy()
