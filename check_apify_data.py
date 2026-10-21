from database import get_connection


conn = get_connection()
cursor = conn.cursor()


cursor.execute("""
SELECT
    post_id,
    caption,
    likes,
    comments_count,
    views,
    shares
FROM posts
WHERE platform = 'TikTok'
ORDER BY id DESC
LIMIT 10
""")


rows = cursor.fetchall()

conn.close()


print("=" * 70)
print("CEK DATA TIKTOK TERBARU")
print("=" * 70)


for row in rows:

    (
        post_id,
        caption,
        likes,
        comments,
        views,
        shares
    ) = row

    print()
    print("ID:", post_id)
    print("Caption:", caption[:100] if caption else "")
    print("Likes:", likes)
    print("Comments:", comments)
    print("Views:", views)
    print("Shares:", shares)
    print("-" * 70)