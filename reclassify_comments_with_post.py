from database import get_connection
from topic_classifier import (
    classify_topic,
    classify_comment_with_context,
    is_relevant_post
)


def main():

    conn = get_connection()
    cursor = conn.cursor()

    print("=" * 70)
    print("REKLASIFIKASI POST + KOMENTAR")
    print("=" * 70)

    # =====================================================
    # 1. REKLASIFIKASI POST
    # =====================================================

    cursor.execute("""
        SELECT
            id,
            post_id,
            caption
        FROM posts
    """)

    posts = cursor.fetchall()

    post_relevan = 0
    post_tidak_relevan = 0

    for row in posts:

        row_id = row[0]
        caption = row[2] or ""

        relevan = is_relevant_post(
            caption
        )

        if relevan:

            topic = classify_topic(
                caption
            )

            post_relevan += 1

        else:

            # Konten non-monitoring ditandai Lainnya
            topic = "Lainnya"

            post_tidak_relevan += 1

        cursor.execute("""
            UPDATE posts
            SET topic = ?
            WHERE id = ?
        """, (
            topic,
            row_id
        ))


    # =====================================================
    # SIMPAN PERUBAHAN POST DULU
    # =====================================================

    conn.commit()


    # =====================================================
    # 2. REKLASIFIKASI KOMENTAR
    # =====================================================

    cursor.execute("""
        SELECT
            c.id,
            c.text,
            c.post_id,
            p.caption,
            p.topic

        FROM comments c

        LEFT JOIN posts p
        ON c.post_id = p.post_id
    """)

    rows = cursor.fetchall()

    total_komentar = 0
    komentar_relevan = 0
    komentar_tidak_relevan = 0
    topik_dari_teks = 0
    topik_dari_post = 0
    tetap_lainnya = 0


    for row in rows:

        comment_id = row[0]

        comment_text = (
            row[1]
            or ""
        )

        post_caption = (
            row[3]
            or ""
        )

        post_topic = (
            row[4]
            or "Lainnya"
        )

        total_komentar += 1


        # =================================================
        # CEK APAKAH POST INDUK RELEVAN
        # =================================================

        if not is_relevant_post(
            post_caption
        ):

            final_topic = "Lainnya"

            komentar_tidak_relevan += 1

        else:

            komentar_relevan += 1

            direct_topic = classify_topic(
                comment_text
            )

            final_topic = (
                classify_comment_with_context(
                    comment_text,
                    post_caption,
                    post_topic
                )
            )


            if direct_topic != "Lainnya":

                topik_dari_teks += 1

            elif final_topic != "Lainnya":

                topik_dari_post += 1

            else:

                tetap_lainnya += 1


        cursor.execute("""
            UPDATE comments
            SET topic = ?
            WHERE id = ?
        """, (
            final_topic,
            comment_id
        ))


    conn.commit()
    conn.close()


    # =====================================================
    # HASIL
    # =====================================================

    print()
    print("POSTINGAN")
    print("-" * 70)

    print(
        "Post relevan:",
        post_relevan
    )

    print(
        "Post tidak relevan:",
        post_tidak_relevan
    )


    print()
    print("KOMENTAR")
    print("-" * 70)

    print(
        "Total komentar:",
        total_komentar
    )

    print(
        "Komentar dari post relevan:",
        komentar_relevan
    )

    print(
        "Komentar dari post tidak relevan:",
        komentar_tidak_relevan
    )

    print(
        "Topik dari teks komentar:",
        topik_dari_teks
    )

    print(
        "Topik mengikuti post:",
        topik_dari_post
    )

    print(
        "Tetap Lainnya pada post relevan:",
        tetap_lainnya
    )

    print()
    print("=" * 70)
    print("SELESAI")
    print("=" * 70)


if __name__ == "__main__":
    main()