from database import get_connection
from topic_classifier import classify_topic


def main():

    conn = get_connection()
    cursor = conn.cursor()

    print("=" * 60)
    print("REKLASIFIKASI TOPIK")
    print("=" * 60)

    # ==========================================
    # POSTINGAN
    # ==========================================

    cursor.execute("""
        SELECT id, caption
        FROM posts
    """)

    posts = cursor.fetchall()

    jumlah_post = 0

    for post_id, caption in posts:

        topic = classify_topic(
            caption or ""
        )

        cursor.execute("""
            UPDATE posts
            SET topic = ?
            WHERE id = ?
        """, (
            topic,
            post_id
        ))

        jumlah_post += 1


    # ==========================================
    # KOMENTAR
    # ==========================================

    cursor.execute("""
        SELECT id, text
        FROM comments
    """)

    comments = cursor.fetchall()

    jumlah_comment = 0

    for comment_id, text in comments:

        topic = classify_topic(
            text or ""
        )

        cursor.execute("""
            UPDATE comments
            SET topic = ?
            WHERE id = ?
        """, (
            topic,
            comment_id
        ))

        jumlah_comment += 1


    conn.commit()
    conn.close()

    print()
    print(
        "Postingan diklasifikasi ulang:",
        jumlah_post
    )

    print(
        "Komentar diklasifikasi ulang:",
        jumlah_comment
    )

    print()
    print("=" * 60)
    print("SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    main()