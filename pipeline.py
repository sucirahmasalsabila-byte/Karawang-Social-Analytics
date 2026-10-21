from database import get_connection, create_tables
from sentiment import classify_sentiment
from topic_classifier import classify_topic
from engagement import (
    calculate_engagement_score,
    classify_engagement
)


create_tables()


def analyze_new_posts():

    conn = get_connection()
    cursor = conn.cursor()

    # hanya ambil postingan yang belum dianalisis
    cursor.execute("""
        SELECT
            id,
            caption,
            likes,
            comments_count,
            views,
            shares
        FROM posts
        WHERE sentiment IS NULL
           OR topic IS NULL
    """)

    posts = cursor.fetchall()

    jumlah = 0

    for post in posts:

        (
            row_id,
            caption,
            likes,
            comments,
            views,
            shares
        ) = post

        sentiment = classify_sentiment(
            caption
        )

        topic = classify_topic(
            caption
        )

        engagement_score = calculate_engagement_score(
            likes,
            comments,
            views,
            shares
        )

        engagement_status = classify_engagement(
            engagement_score
        )

        cursor.execute("""
            UPDATE posts
            SET
                sentiment = ?,
                topic = ?
            WHERE id = ?
        """, (
            sentiment,
            topic,
            row_id
        ))

        jumlah += 1

        print(
            f"POST {row_id}"
            f" | {sentiment}"
            f" | {topic}"
            f" | {engagement_status}"
            f" | Score: {engagement_score}"
        )

    conn.commit()
    conn.close()

    return jumlah


def analyze_new_comments():

    conn = get_connection()
    cursor = conn.cursor()

    # hanya komentar yang belum dianalisis
    cursor.execute("""
        SELECT
            id,
            text
        FROM comments
        WHERE sentiment IS NULL
           OR topic IS NULL
    """)

    comments = cursor.fetchall()

    jumlah = 0

    for comment in comments:

        row_id, text = comment

        sentiment = classify_sentiment(
            text
        )

        topic = classify_topic(
            text
        )

        cursor.execute("""
            UPDATE comments
            SET
                sentiment = ?,
                topic = ?
            WHERE id = ?
        """, (
            sentiment,
            topic,
            row_id
        ))

        jumlah += 1

        print(
            f"COMMENT {row_id}"
            f" | {sentiment}"
            f" | {topic}"
        )

    conn.commit()
    conn.close()

    return jumlah


def run_pipeline():

    print()
    print("=" * 50)
    print("MEMULAI PIPELINE ANALISIS")
    print("=" * 50)

    jumlah_posts = analyze_new_posts()
    jumlah_comments = analyze_new_comments()

    print()
    print("Postingan baru dianalisis:", jumlah_posts)
    print("Komentar baru dianalisis:", jumlah_comments)

    print("=" * 50)
    print("PIPELINE SELESAI")
    print("=" * 50)


if __name__ == "__main__":
    run_pipeline()