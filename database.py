import sqlite3
import os

DB_PATH = os.path.join("data", "monitoring.db")


def get_connection():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    return conn


def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")

    columns = cursor.fetchall()

    for column in columns:
        if column[1] == column_name:
            return True

    return False


def add_column_if_not_exists(
    cursor,
    table_name,
    column_name,
    column_definition
):
    if not column_exists(
        cursor,
        table_name,
        column_name
    ):

        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {column_definition}
            """
        )


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()


    # ==========================
    # TABEL USERS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        role TEXT NOT NULL DEFAULT 'admin',

        created_at TEXT

    )
    """)


    # ==========================
    # TABEL SESSION LOGIN
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_sessions (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER NOT NULL,

        token_hash TEXT UNIQUE NOT NULL,

        created_at TEXT NOT NULL,

        last_activity TEXT NOT NULL,

        expires_at TEXT NOT NULL,

        FOREIGN KEY (user_id)
        REFERENCES users(id)

    )
    """)


    # ==========================
    # TABEL POSTINGAN
    # ==========================

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

    # ==========================
    # TAMBAH KOLOM BARU
    # ==========================

    add_column_if_not_exists(
        cursor,
        "posts",
        "first_seen_at",
        "TEXT"
    )

    add_column_if_not_exists(
        cursor,
        "posts",
        "last_checked_at",
        "TEXT"
    )

    add_column_if_not_exists(
        cursor,
        "posts",
        "collection_type",
        "TEXT"
    )

    add_column_if_not_exists(
        cursor,
        "posts",
        "source_query",
        "TEXT"
    )


    # ==========================
    # TABEL KOMENTAR
    # ==========================

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

    add_column_if_not_exists(
        cursor,
        "comments",
        "first_seen_at",
        "TEXT"
    )

    add_column_if_not_exists(
        cursor,
        "comments",
        "collection_type",
        "TEXT"
    )

    add_column_if_not_exists(
        cursor,
        "comments",
        "url",
        "TEXT"
    )


    # ==========================
    # HISTORY ENGAGEMENT
    # ==========================

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


    # ==========================
    # STATUS COLLECTOR
    # ==========================

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


    conn.commit()
    conn.close()


if __name__ == "__main__":

    create_tables()

    print("Database berhasil diperbarui.")