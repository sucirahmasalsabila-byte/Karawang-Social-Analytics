from database import get_connection
from pipeline import run_pipeline


conn = get_connection()
cursor = conn.cursor()


cursor.execute("""
INSERT OR IGNORE INTO comments (
    comment_id,
    post_id,
    platform,
    text,
    tanggal,
    sentiment,
    topic
)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    "TEST_AUTO_001",
    "TT002",
    "TikTok",
    "Pak jalan di Karawang rusak parah tolong segera diperbaiki",
    "2026-08-26",
    None,
    None
))


conn.commit()
conn.close()


print("Data baru masuk.")

run_pipeline()