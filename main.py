import tkinter as tk
from tkinter import messagebox
from theme import ThemeManager as TM
import database as db
from login import LoginWindow
from page_dashboard import DashboardPage
from page_families import FamiliesPage
from page_donations import DonationsPage
from page_distributions import DistributionsPage

class CharityApp(tk.Tk):
    PAGES = [
        ("🏠 Accueil | لوحة التحكم", "dashboard"),
        ("👨‍👩‍👧 Familles | العائلات", "families"),
        ("💰 Dons | التبرعات", "donations"),
        ("📤 Distributions | توزيع المساعدات", "distributions"),
    ]

    def __init__(self):
        super().__init__()
        self.title("Logiciel de l'Imam | برنامج الإمام لإدارة التبرعات")
        self.geometry("1024x720")
        self.minsize(900, 600)
        
        # فتح البرنامج بأقصى حجم للشاشة تلقائياً
        try: self.state('zoomed') 
        except: self.attributes('-zoomed', True)
            
        self.configure(bg=TM.get_color("bg"))
        db.initialize_database()
        self._pages, self._current = {}, None
        self._build_shell()
        self.withdraw()
        self.after(100, lambda: LoginWindow(self, self._on_auth))

    def _build_shell(self):
        # 1. إعدادات الشبكة للتجاوب مع الشاشة
        self.grid_columnconfigure(1, weight=1) # يجعل المحتوى يأخذ كل العرض المتبقي
        self.grid_rowconfigure(0, weight=1)    # يجعل المحتوى يأخذ كل الارتفاع المتاح

        # 2. القائمة الجانبية (شريط ثابت العرض)
        self.sidebar = tk.Frame(self, bg=TM.get_color("sidebar"), width=TM.SIZES["sidebar_w"])
        self.sidebar.grid(row=0, column=0, sticky="ns") # تلتصق بالأعلى والأسفل فقط
        self.sidebar.pack_propagate(False)

        self.lbl_logo = tk.Label(self.sidebar, text="🕌", font=("", 34), bg=TM.get_color("sidebar"), fg=TM.get_color("accent"))
        self.lbl_logo.pack(pady=(24, 0))
        self.lbl_title = tk.Label(self.sidebar, text="Gestion des Dons\nالتبرعات ادارة", font=TM.FONTS["heading"], fg=TM.get_color("accent"), bg=TM.get_color("sidebar"))
        self.lbl_title.pack(pady=(4, 20))
        
        self._nav_buttons = {}
        for lbl, key in self.PAGES:
            btn = tk.Button(self.sidebar, text=lbl, font=TM.FONTS["body_b"], fg=TM.get_color("text_muted"), bg=TM.get_color("sidebar"), relief="flat", cursor="hand2", command=lambda k=key: self.show_page(k))
            btn.pack(fill="x", pady=2)
            self._nav_buttons[key] = btn

        self.theme_btn = tk.Button(self.sidebar, text="🌓 Thème | المظهر", font=TM.FONTS["small"], fg=TM.get_color("text_muted"), bg=TM.get_color("sidebar"), relief="flat", command=self.toggle_theme)
        self.theme_btn.pack(side="bottom", pady=4)
        
        self.backup_btn = tk.Button(self.sidebar, text="💾 Sauvegarde | نسخ احتياطي", font=TM.FONTS["small"], fg=TM.get_color("text_muted"), bg=TM.get_color("sidebar"), relief="flat", command=self._backup)
        self.backup_btn.pack(side="bottom", pady=4)
        
        self.quit_btn = tk.Button(self.sidebar, text="⏻ Quitter | خروج", font=TM.FONTS["small"], fg=TM.get_color("danger"), bg=TM.get_color("sidebar"), relief="flat", command=self.destroy)
        self.quit_btn.pack(side="bottom", pady=8)

        # 3. منطقة المحتوى (تتمدد لملء الفراغ المتبقي)
        self.content = tk.Frame(self, bg=TM.get_color("bg"))
        self.content.grid(row=0, column=1, sticky="nsew") # تلتصق بالاتجاهات الأربعة

    def _on_auth(self):
        self.deiconify()
        TM.apply_ttk_styles()
        self._build_pages()
        self.show_page("dashboard")

    def _build_pages(self):
        for p in self._pages.values(): p.destroy()
        self._pages = {
            "dashboard": DashboardPage(self.content),
            "families": FamiliesPage(self.content),
            "donations": DonationsPage(self.content),
            "distributions": DistributionsPage(self.content)
        }
        for page in self._pages.values(): page.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_page(self, key):
        if self._current == key: return
        for k, btn in self._nav_buttons.items():
            btn.config(fg=TM.get_color("accent") if k == key else TM.get_color("text_muted"), bg=TM.get_color("card") if k == key else TM.get_color("sidebar"))
        self._pages[key].refresh()
        self._pages[key].lift()
        self._current = key

    def toggle_theme(self):
        TM.toggle_theme()
        self.config(bg=TM.get_color("bg"))
        self.content.config(bg=TM.get_color("bg"))
        self.sidebar.config(bg=TM.get_color("sidebar"))
        self.lbl_logo.config(bg=TM.get_color("sidebar"), fg=TM.get_color("accent"))
        self.lbl_title.config(bg=TM.get_color("sidebar"), fg=TM.get_color("accent"))
        self.theme_btn.config(bg=TM.get_color("sidebar"), fg=TM.get_color("text_muted"))
        self.backup_btn.config(bg=TM.get_color("sidebar"), fg=TM.get_color("text_muted"))
        self.quit_btn.config(bg=TM.get_color("sidebar"), fg=TM.get_color("danger"))
        self._build_pages()
        self.show_page(self._current or "dashboard")

    def _backup(self):
        try:
            filepath = db.backup_database()
            messagebox.showinfo("Succès | نجاح", f"Sauvegarde réussie | تم النسخ الاحتياطي بنجاح :\n{filepath}")
        except Exception as e:
            messagebox.showerror("Erreur | خطأ", f"Échec de la sauvegarde | فشل النسخ الاحتياطي :\n{e}")

if __name__ == "__main__":
    app = CharityApp()
    app.mainloop()
