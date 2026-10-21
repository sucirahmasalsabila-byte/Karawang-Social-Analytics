from database import get_connection


def column_exists(cursor, table_name, column_name):

    cursor.execute(
        f"PRAGMA table_info({table_name})"
    )

    columns = cursor.fetchall()

    return any(
        column[1] == column_name
        for column in columns
    )


def main():

    conn = get_connection()
    cursor = conn.cursor()

    print("=" * 60)
    print("MIGRASI TABEL COMMENTS")
    print("=" * 60)

    if not column_exists(
        cursor,
        "comments",
        "username"
    ):

        cursor.execute(
            """
            ALTER TABLE comments
            ADD COLUMN username TEXT
            """
        )

        print("Kolom username ditambahkan.")

    else:

        print("Kolom username sudah ada.")


    if not column_exists(
        cursor,
        "comments",
        "likes"
    ):

        cursor.execute(
            """
            ALTER TABLE comments
            ADD COLUMN likes INTEGER DEFAULT 0
            """
        )

        print("Kolom likes ditambahkan.")

    else:

        print("Kolom likes sudah ada.")


    conn.commit()
    conn.close()

    print()
    print("MIGRASI SELESAI")


if __name__ == "__main__":
    main()