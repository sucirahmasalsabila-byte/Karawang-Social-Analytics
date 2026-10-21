from database import get_connection


conn = get_connection()
cursor = conn.cursor()

print("=" * 60)
print("CEK JUMLAH KOMENTAR")
print("=" * 60)

cursor.execute("""
SELECT COUNT(*)
FROM comments
""")

total = cursor.fetchone()[0]

print("Total komentar di database:", total)


cursor.execute("""
SELECT platform, COUNT(*)
FROM comments
GROUP BY platform
""")

print()
print("Per platform:")

for row in cursor.fetchall():
    print(row)


cursor.execute("""
SELECT MIN(tanggal), MAX(tanggal)
FROM comments
""")

min_tanggal, max_tanggal = cursor.fetchone()

print()
print("Tanggal komentar paling awal:", min_tanggal)
print("Tanggal komentar paling akhir:", max_tanggal)


cursor.execute("""
SELECT topic, COUNT(*)
FROM comments
GROUP BY topic
ORDER BY COUNT(*) DESC
""")

print()
print("Per topik:")

for row in cursor.fetchall():
    print(row)


conn.close()