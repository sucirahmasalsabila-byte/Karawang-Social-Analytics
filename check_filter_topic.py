from database import get_connection


TOPIC = "Sekolah"


conn = get_connection()
cursor = conn.cursor()


print("=" * 70)
print("CEK FILTER TOPIK:", TOPIC)
print("=" * 70)


# =========================================================
# KOMENTAR BERDASARKAN TOPIK
# =========================================================

cursor.execute(
    """
    SELECT
        c.id,
        c.comment_id,
        c.post_id,
        c.platform,
        c.text,
        c.sentiment,
        c.topic,
        c.tanggal,
        p.topic AS post_topic,
        p.caption

    FROM comments c

    LEFT JOIN posts p
        ON c.post_id = p.post_id

    WHERE LOWER(TRIM(c.topic))
        = LOWER(TRIM(?))

    ORDER BY c.id DESC
    """,
    (
        TOPIC,
    )
)


rows = cursor.fetchall()


print()
print(
    "Jumlah komentar topik",
    TOPIC,
    ":",
    len(rows)
)


for row in rows:

    print()
    print("-" * 70)

    print(
        "ID:",
        row[0]
    )

    print(
        "Platform:",
        row[3]
    )

    print(
        "Topik Komentar:",
        row[6]
    )

    print(
        "Topik Post:",
        row[8]
    )

    print(
        "Tanggal:",
        row[7]
    )

    print(
        "Komentar:",
        row[4]
    )

    print(
        "Post:",
        (row[9] or "")[:200]
    )


conn.close()