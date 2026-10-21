from database import get_connection


conn = get_connection()
cursor = conn.cursor()

print("=" * 60)
print("STRUKTUR TABEL COMMENTS")
print("=" * 60)

cursor.execute(
    "PRAGMA table_info(comments)"
)

columns = cursor.fetchall()

for column in columns:
    print(column)

conn.close()