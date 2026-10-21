
import os
import re
import sqlite3


DB_PATH = os.path.join("data", "monitoring.db")


# =========================================================
# PILIH DATABASE
# Supabase jika URL tersedia, SQLite untuk penggunaan lokal
# =========================================================

def get_supabase_db_url():
    url = os.getenv("SUPABASE_DB_URL", "").strip()

    if not url:
        try:
            import streamlit as st
            url = str(
                st.secrets.get("SUPABASE_DB_URL", "")
            ).strip()
        except Exception:
            url = ""

    return url


def use_supabase():
    return bool(get_supabase_db_url())


# =========================================================
# ADAPTER POSTGRESQL AGAR KODE LAMA TETAP BISA DIGUNAKAN
# =========================================================

class PostgresCursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, params=None):
        query = sql.strip()
        query_lower = query.lower()

        # Ubah placeholder SQLite (?) menjadi PostgreSQL (%s)
        query = query.replace("?", "%s")

        # Dukungan SQL lama dari aplikasi
        query = re.sub(
            r"datetime\s*\(\s*'now'\s*\)",
            "CURRENT_TIMESTAMP",
            query,
            flags=re.IGNORECASE
        )

        # INSERT OR IGNORE -> INSERT ... ON CONFLICT DO NOTHING
        ignore_insert = bool(
            re.match(r"INSERT\s+OR\s+IGNORE\s+INTO\b",
                     query, flags=re.IGNORECASE)
        )

        if ignore_insert:
            query = re.sub(
                r"INSERT\s+OR\s+IGNORE\s+INTO\b",
                "INSERT INTO",
                query,
                count=1,
                flags=re.IGNORECASE
            )

            if not re.search(
                r"\bON\s+CONFLICT\b",
                query,
                flags=re.IGNORECASE
            ):
                query = query.rstrip().rstrip(";")
                query += " ON CONFLICT DO NOTHING"

        self._cursor.execute(query, params)
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    @property
    def description(self):
        return self._cursor.description

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def close(self):
        self._cursor.close()


class PostgresConnection:
    def __init__(self, connection):
        self._connection = connection

    def cursor(self):
        return PostgresCursor(self._connection.cursor())

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()


# =========================================================
# KONEKSI DATABASE
# =========================================================

def get_connection():
    url = get_supabase_db_url()

    if url:
        try:
            import psycopg
        except ImportError as e:
            raise RuntimeError(
                "Paket psycopg belum terpasang. "
                "Tambahkan psycopg[binary] ke requirements.txt."
            ) from e

        connection = psycopg.connect(
            url,
            connect_timeout=15
        )
        return PostgresConnection(connection)

    # Fallback SQLite untuk penggunaan lokal
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


# =========================================================
# PEMERIKSAAN KOLOM
# =========================================================

def column_exists(cursor, table_name, column_name):
    if use_supabase():
        cursor.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = ?
              AND column_name = ?
            LIMIT 1
            """,
            (table_name, column_name)
        )
        return cursor.fetchone() is not None

    cursor.execute(f"PRAGMA table_info({table_name})")
    return any(
        column[1] == column_name
        for column in cursor.fetchall()
    )


def add_column_if_not_exists(
    cursor,
    table_name,
    column_name,
    column_definition
):
    if column_exists(cursor, table_name, column_name):
        return

    if use_supabase():
        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN IF NOT EXISTS
            {column_name} {column_definition}
            """
        )
    else:
        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {column_definition}
            """
        )


# =========================================================
# PEMBUATAN TABEL
# Tidak menghapus atau mengosongkan tabel yang sudah ada
# =========================================================

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        if use_supabase():
            # Tabel autentikasi aplikasi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS login_sessions (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(id),
                    token_hash TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    post_id TEXT UNIQUE,
                    platform TEXT,
                    caption TEXT,
                    tanggal TEXT,
                    hashtag TEXT,
                    url TEXT,
                    likes BIGINT DEFAULT 0,
                    comments_count BIGINT DEFAULT 0,
                    views BIGINT DEFAULT 0,
                    shares BIGINT DEFAULT 0,
                    sentiment TEXT,
                    topic TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    comment_id TEXT UNIQUE,
                    post_id TEXT,
                    platform TEXT,
                    text TEXT,
                    tanggal TEXT,
                    sentiment TEXT,
                    topic TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS engagement_history (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    post_id TEXT,
                    checked_at TEXT,
                    likes BIGINT DEFAULT 0,
                    comments BIGINT DEFAULT 0,
                    views BIGINT DEFAULT 0,
                    shares BIGINT DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collector_status (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    platform TEXT,
                    query TEXT,
                    last_checked_at TEXT,
                    last_post_date TEXT,
                    status TEXT
                )
            """)

        else:
            # Skema SQLite untuk penggunaan lokal
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'admin',
                    created_at TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS login_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token_hash TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT UNIQUE,
                    platform TEXT,
                    caption TEXT,
                    tanggal TEXT,
                    hashtag TEXT,
                    url TEXT,
                    likes INTEGER DEFAULT 0,
                    comments_count INTEGER DEFAULT 0,
                    views INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    sentiment TEXT,
                    topic TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    comment_id TEXT UNIQUE,
                    post_id TEXT,
                    platform TEXT,
                    text TEXT,
                    tanggal TEXT,
                    sentiment TEXT,
                    topic TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS engagement_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT,
                    checked_at TEXT,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    views INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS collector_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT,
                    query TEXT,
                    last_checked_at TEXT,
                    last_post_date TEXT,
                    status TEXT
                )
            """)

        # Tambahkan kolom yang mungkin belum ada.
        # Kolom yang sudah ada tidak diubah.
        columns_to_add = [
            ("posts", "first_seen_at", "TEXT"),
            ("posts", "last_checked_at", "TEXT"),
            ("posts", "collection_type", "TEXT"),
            ("posts", "source_query", "TEXT"),
            ("comments", "first_seen_at", "TEXT"),
            ("comments", "collection_type", "TEXT"),
            ("comments", "url", "TEXT"),
        ]

        for table_name, column_name, definition in columns_to_add:
            add_column_if_not_exists(
                cursor,
                table_name,
                column_name,
                definition
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    create_tables()
    print(
        "Database berhasil diperiksa dan disiapkan. "
        f"Backend: {'Supabase' if use_supabase() else 'SQLite'}"
    )
