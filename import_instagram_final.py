import os
import re
import hashlib
import sqlite3
import pandas as pd

from database import get_connection, create_tables


# =========================================================
# FILE
# =========================================================

FILE_POSTINGAN = os.path.join(
    "dataset",
    "instagram_postingan.csv"
)

FILE_KOMENTAR = os.path.join(
    "dataset",
    "instagram_komentar.csv"
)


# =========================================================
# HELPER
# =========================================================

def safe_text(value):

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    return str(value).strip()


def safe_number(value):

    try:
        number = pd.to_numeric(
            value,
            errors="coerce"
        )

        if pd.isna(number):
            return 0

        return int(number)

    except Exception:
        return 0


def cari_kolom(df, candidates):

    for column in candidates:

        if column in df.columns:
            return column

    return None


def ambil_shortcode(url):

    url = safe_text(url)

    if not url:
        return ""

    match = re.search(
        r"instagram\.com/"
        r"(?:p|reel|reels)/"
        r"([^/?#]+)",
        url,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return ""


def buat_comment_id(
    post_id,
    username,
    text,
    index
):

    raw = (
        f"{post_id}|"
        f"{username}|"
        f"{text}|"
        f"{index}"
    )

    digest = hashlib.md5(
        raw.encode(
            "utf-8",
            errors="ignore"
        )
    ).hexdigest()

    return (
        "IG_COMMENT_"
        + digest
    )


def normalisasi_tanggal(value):

    value = safe_text(value)

    if not value:
        return ""

    try:

        dt = pd.to_datetime(
            value,
            errors="coerce",
            utc=True
        )

        if pd.isna(dt):
            return value

        return (
            dt.tz_convert(None)
            .strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

    except Exception:

        return value


# =========================================================
# CREATE DATABASE
# =========================================================

create_tables()


# =========================================================
# BACA POSTINGAN
# =========================================================

print()
print("=" * 60)
print("IMPORT INSTAGRAM KE DATABASE")
print("=" * 60)

posts = pd.read_csv(
    FILE_POSTINGAN,
    low_memory=False
)

comments = pd.read_csv(
    FILE_KOMENTAR,
    low_memory=False
)


print()
print(
    "Jumlah postingan CSV:",
    len(posts)
)

print(
    "Jumlah komentar CSV :",
    len(comments)
)


# =========================================================
# DETEKSI KOLOM POSTINGAN
# =========================================================

post_id_col = cari_kolom(
    posts,
    [
        "shortCode",
        "shortcode",
        "post_id",
        "postId",
        "id"
    ]
)

caption_col = cari_kolom(
    posts,
    [
        "caption",
        "text",
        "description"
    ]
)

tanggal_col = cari_kolom(
    posts,
    [
        "timestamp",
        "tanggal",
        "date",
        "createdAt",
        "createTime"
    ]
)

sentiment_col = cari_kolom(
    posts,
    [
        "sentimen",
        "sentiment"
    ]
)

topic_col = cari_kolom(
    posts,
    [
        "topik",
        "topic"
    ]
)

url_col = cari_kolom(
    posts,
    [
        "url",
        "postUrl",
        "inputUrl"
    ]
)

hashtag_col = cari_kolom(
    posts,
    [
        "sumber_hashtag",
        "hashtag",
        "query"
    ]
)

likes_col = cari_kolom(
    posts,
    [
        "likesCount",
        "likes",
        "likeCount",
        "diggCount"
    ]
)

comments_count_col = cari_kolom(
    posts,
    [
        "commentsCount",
        "comments_count",
        "commentCount"
    ]
)

views_col = cari_kolom(
    posts,
    [
        "views",
        "viewCount",
        "playCount"
    ]
)

shares_col = cari_kolom(
    posts,
    [
        "shares",
        "shareCount",
        "sharesCount"
    ]
)


# =========================================================
# VALIDASI POSTINGAN
# =========================================================

required_post = {
    "caption": caption_col,
    "sentiment": sentiment_col,
    "topic": topic_col
}


missing_post = [
    name
    for name, column in required_post.items()
    if column is None
]


if missing_post:

    print()
    print(
        "ERROR - Kolom postingan tidak ditemukan:"
    )

    print(
        missing_post
    )

    print()
    print(
        "Kolom CSV postingan:"
    )

    print(
        posts.columns.tolist()
    )

    raise SystemExit()


# =========================================================
# DETEKSI KOLOM KOMENTAR
# =========================================================

comment_text_col = cari_kolom(
    comments,
    [
        "text",
        "komentar",
        "comment",
        "commentText"
    ]
)

comment_username_col = cari_kolom(
    comments,
    [
        "username",
        "ownerUsername",
        "userName",
        "author",
        "commenterUsername"
    ]
)

comment_sentiment_col = cari_kolom(
    comments,
    [
        "sentimen",
        "sentiment"
    ]
)

comment_topic_col = cari_kolom(
    comments,
    [
        "topik",
        "topic"
    ]
)

comment_date_col = cari_kolom(
    comments,
    [
        "timestamp",
        "tanggal",
        "date",
        "createdAt",
        "createTime"
    ]
)

comment_id_col = cari_kolom(
    comments,
    [
        "comment_id",
        "commentId",
        "id"
    ]
)


# =========================================================
# CARI POST ID PADA KOMENTAR
# =========================================================

comment_post_id_col = cari_kolom(
    comments,
    [
        "post_id",
        "postId",
        "postShortCode",
        "post_shortcode",
        "shortCode_postingan",
        "shortcode_postingan",
        "shortCode",
        "shortcode"
    ]
)


comment_post_url_col = cari_kolom(
    comments,
    [
        "postUrl",
        "post_url",
        "url_postingan",
        "inputUrl",
        "url"
    ]
)


# =========================================================
# VALIDASI KOMENTAR
# =========================================================

required_comment = {
    "text": comment_text_col,
    "sentiment": comment_sentiment_col,
    "topic": comment_topic_col
}


missing_comment = [
    name
    for name, column in required_comment.items()
    if column is None
]


if missing_comment:

    print()
    print(
        "ERROR - Kolom komentar tidak ditemukan:"
    )

    print(
        missing_comment
    )

    print()
    print(
        "Kolom CSV komentar:"
    )

    print(
        comments.columns.tolist()
    )

    raise SystemExit()


# =========================================================
# DATABASE
# =========================================================

conn = get_connection()
cursor = conn.cursor()


# =========================================================
# HAPUS DATA INSTAGRAM LAMA SAJA
# =========================================================
#
# TikTok TIDAK disentuh.
# Ini supaya import bisa dijalankan ulang tanpa duplikat.
# =========================================================

cursor.execute(
    """
    DELETE FROM comments
    WHERE platform = ?
    """,
    (
        "Instagram",
    )
)

hapus_comments = cursor.rowcount


cursor.execute(
    """
    DELETE FROM posts
    WHERE platform = ?
    """,
    (
        "Instagram",
    )
)

hapus_posts = cursor.rowcount


print()
print("=" * 60)
print("BERSIHKAN DATA INSTAGRAM LAMA")
print("=" * 60)

print(
    "Postingan Instagram lama dihapus:",
    hapus_posts
)

print(
    "Komentar Instagram lama dihapus :",
    hapus_comments
)


# =========================================================
# IMPORT POSTINGAN
# =========================================================

print()
print("=" * 60)
print("IMPORT POSTINGAN INSTAGRAM")
print("=" * 60)


jumlah_post_masuk = 0
jumlah_post_gagal = 0


post_id_set = set()


for index, row in posts.iterrows():

    url = (
        safe_text(
            row[url_col]
        )
        if url_col
        else ""
    )


    post_id = ""

    if post_id_col:

        post_id = safe_text(
            row[post_id_col]
        )


    if not post_id:

        post_id = ambil_shortcode(
            url
        )


    if not post_id:

        post_id = (
            "IG_POST_"
            + str(index + 1)
        )


    post_id_set.add(
        post_id
    )


    caption = safe_text(
        row[caption_col]
    )


    tanggal = (
        normalisasi_tanggal(
            row[tanggal_col]
        )
        if tanggal_col
        else ""
    )


    sentiment = safe_text(
        row[sentiment_col]
    )


    topic = safe_text(
        row[topic_col]
    )


    hashtag = (
        safe_text(
            row[hashtag_col]
        )
        if hashtag_col
        else ""
    )


    likes = (
        safe_number(
            row[likes_col]
        )
        if likes_col
        else 0
    )


    comments_count = (
        safe_number(
            row[comments_count_col]
        )
        if comments_count_col
        else 0
    )


    views = (
        safe_number(
            row[views_col]
        )
        if views_col
        else 0
    )


    shares = (
        safe_number(
            row[shares_col]
        )
        if shares_col
        else 0
    )


    try:

        cursor.execute(
            """
            INSERT INTO posts (
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
                topic,
                collection_type,
                source_query
            )
            VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?
            )
            """,
            (
                post_id,
                "Instagram",
                caption,
                tanggal,
                hashtag,
                url,
                likes,
                comments_count,
                views,
                shares,
                sentiment,
                topic,
                "final_import",
                hashtag
            )
        )

        jumlah_post_masuk += 1

    except Exception as error:

        jumlah_post_gagal += 1

        print(
            "GAGAL POST:",
            post_id,
            "|",
            error
        )


conn.commit()


print()
print(
    "Postingan berhasil masuk:",
    jumlah_post_masuk
)

print(
    "Postingan gagal         :",
    jumlah_post_gagal
)


# =========================================================
# IMPORT KOMENTAR
# =========================================================

print()
print("=" * 60)
print("IMPORT KOMENTAR INSTAGRAM")
print("=" * 60)


jumlah_comment_masuk = 0
jumlah_comment_gagal = 0
jumlah_comment_tanpa_post = 0


for index, row in comments.iterrows():

    text = safe_text(
        row[comment_text_col]
    )


    username = (
        safe_text(
            row[comment_username_col]
        )
        if comment_username_col
        else ""
    )


    sentiment = safe_text(
        row[comment_sentiment_col]
    )


    topic = safe_text(
        row[comment_topic_col]
    )


    tanggal = (
        normalisasi_tanggal(
            row[comment_date_col]
        )
        if comment_date_col
        else ""
    )


    # =====================================================
    # POST ID KOMENTAR
    # =====================================================

    post_id = ""


    if comment_post_id_col:

        post_id = safe_text(
            row[comment_post_id_col]
        )


    # Jika kolom post_id ternyata URL,
    # ambil shortcode-nya.
    if (
        post_id.startswith(
            "http://"
        )
        or post_id.startswith(
            "https://"
        )
    ):

        shortcode = ambil_shortcode(
            post_id
        )

        if shortcode:
            post_id = shortcode


    # Fallback ambil dari URL postingan
    if (
        not post_id
        and comment_post_url_col
    ):

        post_url = safe_text(
            row[
                comment_post_url_col
            ]
        )

        post_id = ambil_shortcode(
            post_url
        )


    # =====================================================
    # COMMENT ID
    # =====================================================

    comment_id = ""

    if comment_id_col:

        comment_id = safe_text(
            row[comment_id_col]
        )


    if not comment_id:

        comment_id = buat_comment_id(
            post_id,
            username,
            text,
            index
        )


    # =====================================================
    # VALIDASI HUBUNGAN KE POST
    # =====================================================

    if post_id not in post_id_set:

        jumlah_comment_tanpa_post += 1

        # Tetap kita simpan jika punya post_id,
        # supaya tidak kehilangan hasil analisis.
        # Tetapi akan dilaporkan di akhir.


    try:

        cursor.execute(
            """
            INSERT INTO comments (
                comment_id,
                post_id,
                platform,
                text,
                tanggal,
                sentiment,
                topic,
                collection_type
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                comment_id,
                post_id,
                "Instagram",
                text,
                tanggal,
                sentiment,
                topic,
                "final_import"
            )
        )

        jumlah_comment_masuk += 1

    except Exception as error:

        jumlah_comment_gagal += 1

        print(
            "GAGAL COMMENT:",
            comment_id,
            "|",
            error
        )


conn.commit()


print()
print(
    "Komentar berhasil masuk:",
    jumlah_comment_masuk
)

print(
    "Komentar gagal         :",
    jumlah_comment_gagal
)

print(
    "Komentar post_id tidak cocok:",
    jumlah_comment_tanpa_post
)


# =========================================================
# VALIDASI DATABASE
# =========================================================

print()
print("=" * 60)
print("VALIDASI DATABASE")
print("=" * 60)


cursor.execute(
    """
    SELECT COUNT(*)
    FROM posts
    WHERE platform = 'Instagram'
    """
)

jumlah_post_db = (
    cursor.fetchone()[0]
)


cursor.execute(
    """
    SELECT COUNT(*)
    FROM comments
    WHERE platform = 'Instagram'
    """
)

jumlah_comment_db = (
    cursor.fetchone()[0]
)


cursor.execute(
    """
    SELECT sentiment, COUNT(*)
    FROM posts
    WHERE platform = 'Instagram'
    GROUP BY sentiment
    ORDER BY COUNT(*) DESC
    """
)

sentimen_posts = (
    cursor.fetchall()
)


cursor.execute(
    """
    SELECT topic, COUNT(*)
    FROM posts
    WHERE platform = 'Instagram'
    GROUP BY topic
    ORDER BY COUNT(*) DESC
    """
)

topik_posts = (
    cursor.fetchall()
)


cursor.execute(
    """
    SELECT sentiment, COUNT(*)
    FROM comments
    WHERE platform = 'Instagram'
    GROUP BY sentiment
    ORDER BY COUNT(*) DESC
    """
)

sentimen_comments = (
    cursor.fetchall()
)


print()
print(
    "Total postingan Instagram database:",
    jumlah_post_db
)

print(
    "Total komentar Instagram database :",
    jumlah_comment_db
)


print()
print(
    "Sentimen postingan:"
)

for nama, jumlah in sentimen_posts:

    print(
        "-",
        nama,
        ":",
        jumlah
    )


print()
print(
    "Topik postingan:"
)

for nama, jumlah in topik_posts:

    print(
        "-",
        nama,
        ":",
        jumlah
    )


print()
print(
    "Sentimen komentar:"
)

for nama, jumlah in sentimen_comments:

    print(
        "-",
        nama,
        ":",
        jumlah
    )


# =========================================================
# CEK TIKTOK TETAP ADA
# =========================================================

cursor.execute(
    """
    SELECT COUNT(*)
    FROM posts
    WHERE platform = 'TikTok'
    """
)

jumlah_tiktok_posts = (
    cursor.fetchone()[0]
)


cursor.execute(
    """
    SELECT COUNT(*)
    FROM comments
    WHERE platform = 'TikTok'
    """
)

jumlah_tiktok_comments = (
    cursor.fetchone()[0]
)


print()
print("=" * 60)
print("CEK DATA TIKTOK")
print("=" * 60)

print(
    "Postingan TikTok tetap ada:",
    jumlah_tiktok_posts
)

print(
    "Komentar TikTok tetap ada :",
    jumlah_tiktok_comments
)


conn.close()


# =========================================================
# HASIL
# =========================================================

print()
print("=" * 60)
print("IMPORT SELESAI")
print("=" * 60)


if (
    jumlah_post_db == len(posts)
    and
    jumlah_comment_db == len(comments)
):

    print(
        "OK - Semua data Instagram berhasil "
        "masuk ke database."
    )

else:

    print(
        "PERLU CEK - Jumlah data database "
        "berbeda dengan CSV."
    )


print()
print(
    "JANGAN jalankan analyze_database.py."
)

print(
    "Sentimen dan topik Instagram tetap "
    "menggunakan hasil final dari CSV."
)