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

    # ── FAMILY ────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS family (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        head_name           TEXT NOT NULL,
        spouse_name         TEXT DEFAULT '',
        phone               TEXT DEFAULT '',
        address             TEXT DEFAULT '',
        postal_account      TEXT UNIQUE,
        monthly_income      REAL DEFAULT 0,
        rent_amount         REAL DEFAULT 0,
        employment_status   TEXT DEFAULT 'Salarie'
            CHECK (employment_status IN ('Salarie CDI','Salarie CDD','Independant','Retraite','Chomeur','Aides sociales','Autre')),
        income_sources      TEXT DEFAULT '',
        marital_status      TEXT DEFAULT 'Marie'
            CHECK (marital_status IN ('Marie','Veuf','Divorce')),
        total_members       INTEGER DEFAULT 1,
        social_status       TEXT DEFAULT 'Difficile'
            CHECK (social_status IN ('Difficile','Veuve','Divorcee','Orphelins')),
        health_status       TEXT DEFAULT 'Bonne'
            CHECK (health_status IN ('Bonne','Maladie chronique','Handicap')),
        chronic_diseases    TEXT DEFAULT '',
        is_renting          TEXT DEFAULT 'Non'
            CHECK (is_renting IN ('Oui','Non')),
        housing_type        TEXT DEFAULT 'Appartement'
            CHECK (housing_type IN ('Maison','Appartement','Logement temporaire')),
        housing_surface     REAL DEFAULT 0,
        housing_rooms       INTEGER DEFAULT 1,
        housing_condition   TEXT DEFAULT 'Bon'
            CHECK (housing_condition IN ('Bon','Moyen','Mauvais')),
        svf_score           REAL DEFAULT 0
    )""")

    # ── CHILD ─────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS child (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        family_id            INTEGER NOT NULL,
        name                 TEXT NOT NULL,
        date_of_birth        DATE NOT NULL,
        gender               TEXT DEFAULT 'Masculin'
            CHECK (gender IN ('Masculin','Feminin')),
        is_orphan            TEXT DEFAULT 'Non'
            CHECK (is_orphan IN ('Oui','Non')),
        school_status        TEXT DEFAULT 'Scolarise'
            CHECK (school_status IN ('Scolarise','Non scolarise','Universitaire','Formation professionnelle')),
        school_level         TEXT DEFAULT '',
        school_name          TEXT DEFAULT '',
        school_results       TEXT DEFAULT ''
            CHECK (school_results IN ('Excellent','Bien','Moyen','Faible','')),
        dropout_risk         TEXT DEFAULT 'Non'
            CHECK (dropout_risk IN ('Oui','Non')),
        health_status        TEXT DEFAULT 'Bonne'
            CHECK (health_status IN ('Bonne','Maladie chronique','Handicap')),
        disease_type         TEXT DEFAULT '',
        allergies            TEXT DEFAULT '',
        needs_medical_follow TEXT DEFAULT 'Non'
            CHECK (needs_medical_follow IN ('Oui','Non')),
        vaccines_up_to_date  TEXT DEFAULT 'Oui'
            CHECK (vaccines_up_to_date IN ('Oui','Non')),
        specific_needs       TEXT DEFAULT '',
        FOREIGN KEY (family_id) REFERENCES family(id) ON DELETE CASCADE
    )""")

    # ── DONOR ─────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS donor (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone     TEXT DEFAULT '',
        email     TEXT DEFAULT ''
    )""")

    # ── DONATION ──────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS donation (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id      INTEGER NOT NULL,
        amount        REAL NOT NULL,
        donation_type TEXT DEFAULT 'Cash'
            CHECK (donation_type IN ('Cash','Nourriture','Fournitures','Autre')),
        donation_date DATE DEFAULT CURRENT_DATE,
        notes         TEXT DEFAULT '',
        FOREIGN KEY (donor_id) REFERENCES donor(id)
    )""")

    # ── DISTRIBUTION ──────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS distribution (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        family_id         INTEGER NOT NULL,
        amount            REAL NOT NULL,
        distribution_type TEXT DEFAULT 'Financiere'
            CHECK (distribution_type IN ('Financiere','Alimentaire','Medicale','Fournitures','Autre')),
        distribution_date DATE DEFAULT CURRENT_DATE,
        notes             TEXT DEFAULT '',
        FOREIGN KEY (family_id) REFERENCES family(id) ON DELETE CASCADE
    )""")

    conn.commit()
    conn.close()
    _migrate()


def _migrate():
    """Ajoute les colonnes manquantes si base existante."""
    conn = connect()
    c = conn.cursor()
    cols_family = [
        ("spouse_name",       "TEXT DEFAULT ''"),
        ("rent_amount",       "REAL DEFAULT 0"),
        ("marital_status",    "TEXT DEFAULT 'Marie'"),
        ("chronic_diseases",  "TEXT DEFAULT ''"),
        ("housing_surface",   "REAL DEFAULT 0"),
        ("housing_rooms",     "INTEGER DEFAULT 1"),
        ("housing_condition", "TEXT DEFAULT 'Bon'"),
        ("income_sources",    "TEXT DEFAULT ''"),
        ("total_members",     "INTEGER DEFAULT 1"),
        ("distribution_type", "TEXT DEFAULT 'Financiere'"),
    ]
    for col, dtype in cols_family:
        try:
            c.execute(f"ALTER TABLE family ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass

    cols_child = [
        ("is_orphan",            "TEXT DEFAULT 'Non'"),
        ("school_level",         "TEXT DEFAULT ''"),
        ("school_name",          "TEXT DEFAULT ''"),
        ("school_results",       "TEXT DEFAULT ''"),
        ("dropout_risk",         "TEXT DEFAULT 'Non'"),
        ("disease_type",         "TEXT DEFAULT ''"),
        ("allergies",            "TEXT DEFAULT ''"),
        ("needs_medical_follow", "TEXT DEFAULT 'Non'"),
        ("vaccines_up_to_date",  "TEXT DEFAULT 'Oui'"),
        ("specific_needs",       "TEXT DEFAULT ''"),
    ]
    for col, dtype in cols_child:
        try:
            c.execute(f"ALTER TABLE child ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass

    try:
        c.execute("ALTER TABLE donation ADD COLUMN notes TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE distribution ADD COLUMN distribution_type TEXT DEFAULT 'Financiere'")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════
#  FAMILY
# ══════════════════════════════════════════════════════
def add_family(head_name, spouse_name, phone, address, postal_account,
               monthly_income, rent_amount, employment_status, income_sources,
               marital_status, total_members, social_status,
               health_status, chronic_diseases,
               is_renting, housing_type, housing_surface,
               housing_rooms, housing_condition):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO family (
            head_name, spouse_name, phone, address, postal_account,
            monthly_income, rent_amount, employment_status, income_sources,
            marital_status, total_members, social_status,
            health_status, chronic_diseases,
            is_renting, housing_type, housing_surface,
            housing_rooms, housing_condition
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (head_name, spouse_name, phone, address, postal_account,
          monthly_income, rent_amount, employment_status, income_sources,
          marital_status, total_members, social_status,
          health_status, chronic_diseases,
          is_renting, housing_type, housing_surface,
          housing_rooms, housing_condition))
    conn.commit()
    fid = cur.lastrowid
    conn.close()
    return fid


def update_family(fid, head_name, spouse_name, phone, address, postal_account,
                  monthly_income, rent_amount, employment_status, income_sources,
                  marital_status, total_members, social_status,
                  health_status, chronic_diseases,
                  is_renting, housing_type, housing_surface,
                  housing_rooms, housing_condition):
    conn = connect()
    conn.execute("""
        UPDATE family SET
            head_name=?, spouse_name=?, phone=?, address=?, postal_account=?,
            monthly_income=?, rent_amount=?, employment_status=?, income_sources=?,
            marital_status=?, total_members=?, social_status=?,
            health_status=?, chronic_diseases=?,
            is_renting=?, housing_type=?, housing_surface=?,
            housing_rooms=?, housing_condition=?
        WHERE id=?
    """, (head_name, spouse_name, phone, address, postal_account,
          monthly_income, rent_amount, employment_status, income_sources,
          marital_status, total_members, social_status,
          health_status, chronic_diseases,
          is_renting, housing_type, housing_surface,
          housing_rooms, housing_condition, fid))
    conn.commit()
    conn.close()


def delete_family(fid):
    conn = connect()
    conn.execute("DELETE FROM family WHERE id=?", (fid,))
    conn.commit()
    conn.close()


def get_all_families():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM family ORDER BY head_name")
    data = cur.fetchall()
    conn.close()
    return data


def get_family_by_id(fid):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM family WHERE id=?", (fid,))
    row = cur.fetchone()
    conn.close()
    return row


def search_families(query):
    conn = connect()
    cur = conn.cursor()
    q = f"%{query}%"
    cur.execute("""
        SELECT * FROM family
        WHERE head_name LIKE ? OR spouse_name LIKE ?
           OR phone LIKE ? OR address LIKE ?
    """, (q, q, q, q))
    data = cur.fetchall()
    conn.close()
    return data


# ══════════════════════════════════════════════════════
#  CHILD
# ══════════════════════════════════════════════════════
def add_child(family_id, name, date_of_birth, gender, is_orphan,
              school_status, school_level, school_name, school_results, dropout_risk,
              health_status, disease_type, allergies, needs_medical_follow,
              vaccines_up_to_date, specific_needs):
    conn = connect()
    conn.execute("""
        INSERT INTO child (
            family_id, name, date_of_birth, gender, is_orphan,
            school_status, school_level, school_name, school_results, dropout_risk,
            health_status, disease_type, allergies, needs_medical_follow,
            vaccines_up_to_date, specific_needs
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (family_id, name, date_of_birth, gender, is_orphan,
          school_status, school_level, school_name, school_results, dropout_risk,
          health_status, disease_type, allergies, needs_medical_follow,
          vaccines_up_to_date, specific_needs))
    conn.commit()
    conn.close()


def update_child(child_id, name, date_of_birth, gender, is_orphan,
                 school_status, school_level, school_name, school_results, dropout_risk,
                 health_status, disease_type, allergies, needs_medical_follow,
                 vaccines_up_to_date, specific_needs):
    conn = connect()
    conn.execute("""
        UPDATE child SET
            name=?, date_of_birth=?, gender=?, is_orphan=?,
            school_status=?, school_level=?, school_name=?, school_results=?, dropout_risk=?,
            health_status=?, disease_type=?, allergies=?, needs_medical_follow=?,
            vaccines_up_to_date=?, specific_needs=?
        WHERE id=?
    """, (name, date_of_birth, gender, is_orphan,
          school_status, school_level, school_name, school_results, dropout_risk,
          health_status, disease_type, allergies, needs_medical_follow,
          vaccines_up_to_date, specific_needs, child_id))
    conn.commit()
    conn.close()


def delete_child(child_id):
    conn = connect()
    conn.execute("DELETE FROM child WHERE id=?", (child_id,))
    conn.commit()
    conn.close()


def get_children_by_family(family_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM child WHERE family_id=? ORDER BY name", (family_id,))
    data = cur.fetchall()
    conn.close()
    return data


# ══════════════════════════════════════════════════════
#  DONOR
# ══════════════════════════════════════════════════════
def add_donor(full_name, phone, email):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO donor (full_name,phone,email) VALUES (?,?,?)",
                (full_name, phone, email))
    conn.commit()
    did = cur.lastrowid
    conn.close()
    return did


def get_all_donors():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM donor ORDER BY full_name")
    data = cur.fetchall()
    conn.close()
    return data


def delete_donor(did):
    conn = connect()
    conn.execute("DELETE FROM donor WHERE id=?", (did,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════
#  DONATION
# ══════════════════════════════════════════════════════
def add_donation(donor_id, amount, donation_type, notes=""):
    conn = connect()
    conn.execute("""
        INSERT INTO donation (donor_id, amount, donation_type, notes)
        VALUES (?,?,?,?)
    """, (donor_id, amount, donation_type, notes))
    conn.commit()
    conn.close()


def get_all_donations():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT d.id, dn.full_name, d.amount, d.donation_type, d.donation_date, d.notes
        FROM donation d JOIN donor dn ON d.donor_id=dn.id
        ORDER BY d.donation_date DESC
    """)
    data = cur.fetchall()
    conn.close()
    return data


def get_total_donations():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(amount),0) FROM donation")
    t = cur.fetchone()[0]
    conn.close()
    return t


def delete_donation(did):
    conn = connect()
    conn.execute("DELETE FROM donation WHERE id=?", (did,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════
#  DISTRIBUTION
# ══════════════════════════════════════════════════════
def add_distribution(family_id, amount, distribution_type, notes):
    conn = connect()
    conn.execute("""
        INSERT INTO distribution (family_id, amount, distribution_type, notes)
        VALUES (?,?,?,?)
    """, (family_id, amount, distribution_type, notes))
    conn.commit()
    conn.close()


def get_all_distributions():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT dist.id, f.head_name, dist.amount, dist.distribution_type,
               dist.distribution_date, dist.notes
        FROM distribution dist JOIN family f ON dist.family_id=f.id
        ORDER BY dist.distribution_date DESC
    """)
    data = cur.fetchall()
    conn.close()
    return data


def get_distributions_by_family(family_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM distribution WHERE family_id=?
        ORDER BY distribution_date DESC
    """, (family_id,))
    data = cur.fetchall()
    conn.close()
    return data


def get_total_distributions():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(amount),0) FROM distribution")
    t = cur.fetchone()[0]
    conn.close()
    return t


def delete_distribution(did):
    conn = connect()
    conn.execute("DELETE FROM distribution WHERE id=?", (did,))
    conn.commit()
    conn.close()


def get_balance():
    return get_total_donations() - get_total_distributions()


# ══════════════════════════════════════════════════════
#  STATS
# ══════════════════════════════════════════════════════
def get_stats():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM family");   nb_f = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM child");    nb_c = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM donor");    nb_d = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM donation"); nb_n = cur.fetchone()[0]
    conn.close()
    return {
        "families":  nb_f, "children":  nb_c,
        "donors":    nb_d, "donations": nb_n,
        "total_in":  get_total_donations(),
        "total_out": get_total_distributions(),
        "balance":   get_balance()
    }


# ══════════════════════════════════════════════════════
#  SAUVEGARDE
# ══════════════════════════════════════════════════════
def backup_database():
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(backup_dir, f"charity_{ts}.db")
    shutil.copy2(DB_NAME, dest)
    return dest