from database import get_connection


conn = get_connection()
cursor = conn.cursor()

print("=" * 70)
print("CONTOH KOMENTAR TOPIK LAINNYA")
print("=" * 70)

cursor.execute("""
SELECT
    id,
    platform,
    text,
    sentiment
FROM comments
WHERE topic = 'Lainnya'
ORDER BY id DESC
LIMIT 100
""")

rows = cursor.fetchall()

print("Jumlah contoh:", len(rows))
print()

for row in rows:

    comment_id = row[0]
    platform = row[1]
    text = row[2]
    sentiment = row[3]

    print("-" * 70)

    print("ID:", comment_id)
    print("Platform:", platform)
    print("Sentimen:", sentiment)
    print("Komentar:", text)

conn.close()