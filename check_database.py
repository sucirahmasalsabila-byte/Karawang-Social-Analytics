from database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT COUNT(*)
FROM posts
""")

total_posts = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM posts
WHERE platform = 'TikTok'
""")

total_tiktok = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM posts
WHERE sentiment IS NULL
   OR topic IS NULL
""")

belum_dianalisis = cursor.fetchone()[0]


cursor.execute("""
SELECT
    post_id,
    platform,
    sentiment,
    topic
FROM posts
LIMIT 10
""")

sample = cursor.fetchall()

conn.close()


print("=" * 50)
print("CEK DATABASE")
print("=" * 50)

print("Total postingan:", total_posts)
print("Total TikTok:", total_tiktok)
print("Belum dianalisis:", belum_dianalisis)

print()
print("Contoh data:")

for row in sample:
    print(row)