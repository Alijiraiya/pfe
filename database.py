import sqlite3
import shutil
import os
from datetime import datetime

DB_NAME = "charity.db"

def connect():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    conn = connect()
    c = conn.cursor()
    
    # إنشاء جدول العائلات مع حقل svf_score وحقل is_active للحذف المنطقي
    c.execute("""
    CREATE TABLE IF NOT EXISTS family (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        head_name TEXT NOT NULL,
        spouse_name TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        address TEXT DEFAULT '',
        postal_account TEXT UNIQUE,
        monthly_income REAL DEFAULT 0,
        rent_amount REAL DEFAULT 0,
        employment_status TEXT DEFAULT 'Chomeur',
        income_sources TEXT DEFAULT '',
        marital_status TEXT DEFAULT 'Marie',
        total_members INTEGER DEFAULT 1,
        social_status TEXT DEFAULT 'Difficile',
        health_status TEXT DEFAULT 'Bonne',
        chronic_diseases TEXT DEFAULT '',
        is_renting TEXT DEFAULT 'Non',
        housing_type TEXT DEFAULT 'Maison',
        housing_surface REAL DEFAULT 0,
        rooms_count INTEGER DEFAULT 1,
        housing_condition TEXT DEFAULT 'Moyen',
        svf_score REAL DEFAULT 0,
        is_active INTEGER DEFAULT 1
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS child (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        family_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        date_of_birth TEXT NOT NULL,
        gender TEXT DEFAULT 'Masculin',
        is_orphan TEXT DEFAULT 'Non',
        school_status TEXT DEFAULT 'Scolarise',
        school_level TEXT DEFAULT '',
        school_name TEXT DEFAULT '',
        school_results TEXT DEFAULT '',
        dropout_risk TEXT DEFAULT 'Non',
        health_status TEXT DEFAULT 'Bonne',
        disease_type TEXT DEFAULT '',
        allergies TEXT DEFAULT '',
        needs_medical_follow TEXT DEFAULT 'Non',
        vaccines_up_to_date TEXT DEFAULT 'Oui',
        specific_needs TEXT DEFAULT '',
        FOREIGN KEY (family_id) REFERENCES family(id) ON DELETE CASCADE
    )""")
    
    # إنشاء جدول المتبرعين مع حقل is_active للحذف المنطقي
    c.execute("""
    CREATE TABLE IF NOT EXISTS donor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT DEFAULT '',
        email TEXT DEFAULT '',
        is_active INTEGER DEFAULT 1
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS donation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        donation_type TEXT DEFAULT 'Cash',
        donation_date TEXT NOT NULL,
        notes TEXT DEFAULT '',
        FOREIGN KEY (donor_id) REFERENCES donor(id) ON DELETE CASCADE
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS distribution (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        family_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        distribution_type TEXT DEFAULT 'Financiere',
        distribution_date TEXT NOT NULL,
        notes TEXT DEFAULT '',
        FOREIGN KEY (family_id) REFERENCES family(id) ON DELETE CASCADE
    )""")
    
    # تحديث قاعدة البيانات القديمة إن وُجدت (لإضافة أعمدة الحذف المنطقي بأمان)
    try: c.execute("ALTER TABLE family ADD COLUMN is_active INTEGER DEFAULT 1")
    except: pass
    try: c.execute("ALTER TABLE donor ADD COLUMN is_active INTEGER DEFAULT 1")
    except: pass

    conn.commit()
    conn.close()

def backup_database():
    if not os.path.exists("backups"): os.makedirs("backups")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bfile = f"backups/charity_backup_{ts}.db"
    shutil.copy2(DB_NAME, bfile)
    return bfile

def execute_query(query, params=()):
    conn = connect()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()

def fetch_all(query, params=()):
    conn = connect()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_one(query, params=()):
    conn = connect()
    cur = conn.cursor()
    cur.execute(query, params)
    row = cur.fetchone()
    conn.close()
    return row

# --- دوال العائلات ---
def add_family(*args):
    q = """INSERT INTO family (head_name, spouse_name, phone, address, postal_account, monthly_income, rent_amount, employment_status, income_sources, marital_status, total_members, social_status, health_status, chronic_diseases, is_renting, housing_type, housing_surface, rooms_count, housing_condition, svf_score) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    execute_query(q, args)
    
def update_family(fid, *args):
    q = """UPDATE family SET head_name=?, spouse_name=?, phone=?, address=?, postal_account=?, monthly_income=?, rent_amount=?, employment_status=?, income_sources=?, marital_status=?, total_members=?, social_status=?, health_status=?, chronic_diseases=?, is_renting=?, housing_type=?, housing_surface=?, rooms_count=?, housing_condition=?, svf_score=? WHERE id=?"""
    execute_query(q, args + (fid,))

def delete_family(fid): 
    execute_query("UPDATE family SET is_active=0 WHERE id=?", (fid,))

def get_all_families(): 
    return fetch_all("SELECT * FROM family WHERE is_active=1 ORDER BY id DESC")

def get_family_by_id(fid): 
    return fetch_one("SELECT * FROM family WHERE id=?", (fid,))

def search_families(term): 
    return fetch_all("SELECT * FROM family WHERE is_active=1 AND (head_name LIKE ? OR phone LIKE ?)", (f"%{term}%", f"%{term}%"))

# --- دوال الأطفال ---
def add_child(fid, *args): 
    execute_query("INSERT INTO child (family_id, name, date_of_birth, gender, is_orphan, school_status, school_level, school_name, school_results, dropout_risk, health_status, disease_type, allergies, needs_medical_follow, vaccines_up_to_date, specific_needs) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (fid,) + args)

def update_child(cid, *args): 
    execute_query("UPDATE child SET name=?, date_of_birth=?, gender=?, is_orphan=?, school_status=?, school_level=?, school_name=?, school_results=?, dropout_risk=?, health_status=?, disease_type=?, allergies=?, needs_medical_follow=?, vaccines_up_to_date=?, specific_needs=? WHERE id=?", args + (cid,))

def delete_child(cid): 
    execute_query("DELETE FROM child WHERE id=?", (cid,))

def get_children_by_family(fid): 
    return fetch_all("SELECT * FROM child WHERE family_id=?", (fid,))

# --- دوال المتبرعين ---
def add_donor(name, phone, email): 
    execute_query("INSERT INTO donor (name, phone, email) VALUES (?,?,?)", (name, phone, email))

def delete_donor(did): 
    execute_query("UPDATE donor SET is_active=0 WHERE id=?", (did,))

def get_all_donors(): 
    return fetch_all("SELECT * FROM donor WHERE is_active=1 ORDER BY id DESC")

# --- دوال التبرعات (المداخيل) ---
def add_donation(did, amt, dtype, notes): 
    execute_query("INSERT INTO donation (donor_id, amount, donation_type, donation_date, notes) VALUES (?,?,?,?,?)", (did, amt, dtype, datetime.now().strftime("%Y-%m-%d"), notes))

def delete_donation(did): 
    execute_query("DELETE FROM donation WHERE id=?", (did,))

def get_all_donations(): 
    return fetch_all("SELECT d.id, dn.name, d.amount, d.donation_type, d.donation_date, d.notes FROM donation d JOIN donor dn ON d.donor_id = dn.id ORDER BY d.id DESC")

def get_total_donations(): 
    return fetch_one("SELECT SUM(amount) FROM donation")[0] or 0

# --- دوال المساعدات (المصاريف) ---
def add_distribution(fid, amt, dtype, notes): 
    execute_query("INSERT INTO distribution (family_id, amount, distribution_type, distribution_date, notes) VALUES (?,?,?,?,?)", (fid, amt, dtype, datetime.now().strftime("%Y-%m-%d"), notes))

def delete_distribution(did): 
    execute_query("DELETE FROM distribution WHERE id=?", (did,))

def get_all_distributions(): 
    return fetch_all("SELECT d.id, f.head_name, d.amount, d.distribution_type, d.distribution_date, d.notes FROM distribution d JOIN family f ON d.family_id = f.id ORDER BY d.id DESC")

def get_distributions_by_family(fid): 
    return fetch_all("SELECT d.id, f.head_name, d.amount, d.distribution_type, d.distribution_date, d.notes FROM distribution d JOIN family f ON d.family_id = f.id WHERE d.family_id=? ORDER BY d.id DESC", (fid,))

def get_total_distributions(): 
    return fetch_one("SELECT SUM(amount) FROM distribution")[0] or 0

# --- دوال الإحصائيات والرصيد ---
def get_balance(): 
    return get_total_donations() - get_total_distributions()

def get_stats():
    return {
        "families": fetch_one("SELECT COUNT(*) FROM family WHERE is_active=1")[0],
        # جلب عدد الأطفال الخاصين بالعائلات غير المحذوفة فقط
        "children": fetch_one("SELECT COUNT(c.id) FROM child c JOIN family f ON c.family_id = f.id WHERE f.is_active=1")[0],
        "donors": fetch_one("SELECT COUNT(*) FROM donor WHERE is_active=1")[0],
        "donations": fetch_one("SELECT COUNT(*) FROM donation")[0],
        "total_in": get_total_donations(),
        "total_out": get_total_distributions(),
        "balance": get_balance()
    }
