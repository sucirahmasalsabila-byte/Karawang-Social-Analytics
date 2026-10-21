from database import get_connection, create_tables
from watchlist import HASHTAGS, TOPICS, START_DATE

create_tables()

print("================================")
print("MONITORING MEDIA SOSIAL KARAWANG")
print("================================")

print()
print("Tanggal awal pengambilan:")
print(START_DATE)

print()
print("Hashtag yang dipantau:")

for hashtag in HASHTAGS:
    print("#" + hashtag)

print()
print("Topik yang dipantau:")

for topic in TOPICS:
    print("-", topic)


conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name
""")

tables = cursor.fetchall()

conn.close()

print()
print("Tabel database:")

for table in tables:
    print("-", table[0])

print()
print("Setup berhasil.")