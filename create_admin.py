from datetime import datetime

from database import (
    create_tables,
    get_connection
)


create_tables()


USERNAME = "diskominfo"

PASSWORD_HASH = (
    "$2a$12$XAV0P8eNbkb8RmDniszqxOSKo6w7sCksR."
    "XgyJRE7GLy/pB9aXUZO"
)

ROLE = "admin"


conn = get_connection()
cursor = conn.cursor()


cursor.execute(
    """
    INSERT INTO users (
        username,
        password,
        role,
        created_at
    )
    VALUES (?, ?, ?, ?)

    ON CONFLICT(username)
    DO UPDATE SET
        password = excluded.password,
        role = excluded.role
    """,
    (
        USERNAME,
        PASSWORD_HASH,
        ROLE,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )
)


conn.commit()
conn.close()


print("Admin berhasil disimpan ke database.")
print(f"Username : {USERNAME}")
print(f"Role     : {ROLE}")