"""
MedEasy — SQLite Database Layer

Tables:
  users   — registered user accounts
  reports — saved analysis history per user
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "medeasy.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS reports (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER REFERENCES users(id) ON DELETE CASCADE,
            uploaded_at    TEXT    DEFAULT (datetime('now')),
            report_type    TEXT,
            patient_name   TEXT,
            patient_age    TEXT,
            patient_gender TEXT,
            overall_status TEXT,
            total_tests    INTEGER DEFAULT 0,
            normal_count   INTEGER DEFAULT 0,
            abnormal_count INTEGER DEFAULT 0,
            language       TEXT    DEFAULT 'English',
            raw_text       TEXT,
            result_json    TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_reports_user ON reports(user_id);
        CREATE INDEX IF NOT EXISTS idx_users_email  ON users(email);
    """)
    conn.commit()
    conn.close()
    print("[DB] Initialized:", DB_PATH)


# ── USER OPERATIONS ──────────────────────────────────────────

def create_user(name, email, password_hash):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, password_hash) VALUES (?,?,?)",
                    (name, email, password_hash))
        conn.commit()
        return {"id": cur.lastrowid, "name": name, "email": email, "status": "created"}
    except sqlite3.IntegrityError:
        return {"status": "email_exists"}
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    conn = get_conn()
    row = conn.execute("SELECT id,name,email,created_at FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user(user_id, name=None, email=None, password_hash=None):
    conn = get_conn()
    if name:
        conn.execute("UPDATE users SET name=? WHERE id=?", (name, user_id))
    if email:
        conn.execute("UPDATE users SET email=? WHERE id=?", (email, user_id))
    if password_hash:
        conn.execute("UPDATE users SET password_hash=? WHERE id=?", (password_hash, user_id))
    conn.commit()
    conn.close()


def delete_user(user_id):
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


# ── REPORT OPERATIONS ─────────────────────────────────────────

def save_report(user_id, result, raw_text=""):
    patient = result.get("patient", {})
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reports
          (user_id, report_type, patient_name, patient_age, patient_gender,
           overall_status, total_tests, normal_count, abnormal_count,
           language, raw_text, result_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        user_id,
        result.get("report_type", ""),
        patient.get("name", ""),
        patient.get("age", ""),
        patient.get("gender", ""),
        result.get("status_key", ""),
        result.get("total_tests", 0),
        result.get("normal_count", 0),
        result.get("abnormal_count", 0),
        result.get("language", "English"),
        raw_text[:3000],
        json.dumps(result),
    ))
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def get_user_reports(user_id, limit=20):
    conn = get_conn()
    rows = conn.execute("""
        SELECT id, uploaded_at, report_type, patient_name, overall_status,
               total_tests, normal_count, abnormal_count, language
        FROM reports WHERE user_id=?
        ORDER BY uploaded_at DESC LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_report_by_id(report_id, user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM reports WHERE id=? AND user_id=?",
                       (report_id, user_id)).fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    if data.get("result_json"):
        data["result"] = json.loads(data["result_json"])
    return data


def delete_report(report_id, user_id):
    conn = get_conn()
    conn.execute("DELETE FROM reports WHERE id=? AND user_id=?", (report_id, user_id))
    conn.commit()
    conn.close()


def get_report_stats(user_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT COUNT(*) as total, SUM(abnormal_count) as total_abnormal
        FROM reports WHERE user_id=?
    """, (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else {"total": 0, "total_abnormal": 0}
