from database import get_connection, create_tables

create_tables()

conn = get_connection()
cursor = conn.cursor()

posts = [
    (
        "IG001",
        "Instagram",
        "Perbaikan jalan Karawang Timur mulai dilakukan",
        "2026-08-20",
        "#bupatikarawang",
        "https://instagram.com/post/ig001",
        1200,
        320,
        0,
        0,
        "Positif",
        "Jalan Karawang Timur"
    ),
    (
        "IG002",
        "Instagram",
        "Warga mengeluhkan kondisi saluran air",
        "2026-08-21",
        "#karawanghariini",
        "https://instagram.com/post/ig002",
        950,
        780,
        0,
        0,
        "Negatif",
        "Saluran"
    ),
    (
        "TT001",
        "TikTok",
        "Program MBG di sekolah Karawang",
        "2026-08-22",
        "#karawangmaju",
        "https://tiktok.com/video/tt001",
        15000,
        2500,
        180000,
        1200,
        "Netral",
        "MBG"
    ),
    (
        "TT002",
        "TikTok",
        "Keluhan jalan rusak di Karawang",
        "2026-08-23",
        "#infokarawang",
        "https://tiktok.com/video/tt002",
        27000,
        5100,
        420000,
        3500,
        "Negatif",
        "Jalan"
    )
]

cursor.executemany("""
INSERT OR IGNORE INTO posts (
    post_id,
    platform,
    caption,
    tanggal,
    hashtag,
    url,
    likes,
    comments_count,
    views,
    shares,
    sentiment,
    topic
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", posts)


comments = [
    (
        "C001",
        "IG001",
        "Instagram",
        "Bagus akhirnya jalannya diperbaiki",
        "2026-08-20",
        "Positif",
        "Jalan Karawang Timur"
    ),
    (
        "C002",
        "IG001",
        "Instagram",
        "Semoga cepat selesai",
        "2026-08-20",
        "Positif",
        "Jalan Karawang Timur"
    ),
    (
        "C003",
        "IG002",
        "Instagram",
        "Salurannya mampet terus pak",
        "2026-08-21",
        "Negatif",
        "Saluran"
    ),
    (
        "C004",
        "IG002",
        "Instagram",
        "Kalau hujan langsung banjir",
        "2026-08-21",
        "Negatif",
        "Saluran"
    ),
    (
        "C005",
        "TT001",
        "TikTok",
        "MBG di sekolah saya sudah bagus",
        "2026-08-22",
        "Positif",
        "MBG"
    ),
    (
        "C006",
        "TT001",
        "TikTok",
        "Di sekolah saya belum dapat",
        "2026-08-22",
        "Negatif",
        "MBG"
    ),
    (
        "C007",
        "TT002",
        "TikTok",
        "Jalannya rusak parah",
        "2026-08-23",
        "Negatif",
        "Jalan"
    ),
    (
        "C008",
        "TT002",
        "TikTok",
        "Tolong segera diperbaiki pak",
        "2026-08-23",
        "Negatif",
        "Jalan"
    ),
    (
        "C009",
        "TT002",
        "TikTok",
        "Semoga cepat ditangani",
        "2026-08-23",
        "Netral",
        "Jalan"
    )
]

cursor.executemany("""
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
""", comments)


engagement = [
    ("TT002", "2026-08-23 08:00", 10000, 1000, 100000, 700),
    ("TT002", "2026-08-23 14:00", 18000, 2700, 240000, 1700),
    ("TT002", "2026-08-23 20:00", 27000, 5100, 420000, 3500),

    ("TT001", "2026-08-22 08:00", 7000, 800, 70000, 400),
    ("TT001", "2026-08-22 20:00", 15000, 2500, 180000, 1200)
]

cursor.executemany("""
INSERT INTO engagement_history (
    post_id,
    checked_at,
    likes,
    comments,
    views,
    shares
)
VALUES (?, ?, ?, ?, ?, ?)
""", engagement)

conn.commit()
conn.close()

print("Data contoh berhasil dimasukkan.")