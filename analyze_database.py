from database import get_connection, create_tables
from sentiment import classify_sentiment
from topic_classifier import classify_topic
from engagement import (
    calculate_engagement_score,
    classify_engagement
)

create_tables()


def analyze_posts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, caption, likes, comments_count, views, shares
        FROM posts
    """)

    posts = cursor.fetchall()

    for row in posts:
        (
            row_id,
            caption,
            likes,
            comments,
            views,
            shares
        ) = row

        sentiment = classify_sentiment(caption)
        topic = classify_topic(caption)

        score = calculate_engagement_score(
            likes,
            comments,
            views,
            shares
        )

        status = classify_engagement(score)

        cursor.execute("""
            UPDATE posts
            SET sentiment = ?,
                topic = ?
            WHERE id = ?
        """, (
            sentiment,
            topic,
            row_id
        ))

        print(
            "POST:",
            row_id,
            "|",
            sentiment,
            "|",
            topic,
            "|",
            status,
            "| score:",
            score
        )

    conn.commit()
    conn.close()


def analyze_comments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, text
        FROM comments
    """)

    comments = cursor.fetchall()

    for row in comments:
        row_id, text = row

        sentiment = classify_sentiment(text)
        topic = classify_topic(text)

        cursor.execute("""
            UPDATE comments
            SET sentiment = ?,
                topic = ?
            WHERE id = ?
        """, (
            sentiment,
            topic,
            row_id
        ))

        print(
            "COMMENT:",
            row_id,
            "|",
            sentiment,
            "|",
            topic
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("Mulai analisis database...")

    analyze_posts()
    analyze_comments()

    print("Analisis selesai.")