from database import get_connection


def show_topic(topic, limit=30):

    conn = get_connection()
    cursor = conn.cursor()

    print()
    print("=" * 70)
    print("TOPIK:", topic)
    print("=" * 70)

    cursor.execute(
        """
        SELECT
            c.id,
            c.text,
            c.sentiment,
            c.post_id,
            p.caption,
            p.topic

        FROM comments c

        LEFT JOIN posts p
        ON c.post_id = p.post_id

        WHERE c.topic = ?

        ORDER BY c.id DESC

        LIMIT ?
        """,
        (
            topic,
            limit
        )
    )

    rows = cursor.fetchall()

    for row in rows:

        print("-" * 70)

        print("ID:", row[0])
        print("Sentimen:", row[2])
        print("Komentar:", row[1])
        print("Topik Post:", row[5])

        caption = row[4] or ""

        print(
            "Post:",
            caption[:180]
        )

    conn.close()


show_topic(
    "Transportasi",
    30
)

show_topic(
    "Kriminalitas",
    30
)

show_topic(
    "Lainnya",
    30
)