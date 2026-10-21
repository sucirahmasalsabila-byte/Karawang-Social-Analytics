import os
import sys
from datetime import datetime, timezone

import instaloader
from dotenv import load_dotenv

# =========================================================
# AGAR FILE DI FOLDER collectors BISA MEMBACA FILE UTAMA
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(PROJECT_ROOT)

from database import get_connection, create_tables
from watchlist import HASHTAGS, START_DATE


# =========================================================
# LOAD .ENV
# =========================================================

load_dotenv()

IG_USERNAME = os.getenv("IG_USERNAME")


# =========================================================
# KONVERSI TANGGAL
# =========================================================

START_DATE_OBJECT = datetime.strptime(
    START_DATE,
    "%Y-%m-%d"
).replace(tzinfo=timezone.utc)


# =========================================================
# INSTALOADER
# =========================================================

L = instaloader.Instaloader(
    download_pictures=False,
    download_videos=False,
    download_video_thumbnails=False,
    save_metadata=False,
    compress_json=False
)


# =========================================================
# LOGIN DARI SESSION
# =========================================================

def load_instagram_session():

    if not IG_USERNAME:
        print(
            "ERROR: IG_USERNAME belum ada di file .env"
        )
        return False

    try:

        L.load_session_from_file(
            IG_USERNAME
        )

        print(
            f"Session Instagram berhasil dimuat: "
            f"{IG_USERNAME}"
        )

        return True

    except Exception as e:

        print()
        print(
            "Session Instagram belum ditemukan."
        )

        print(
            "Login Instagram dulu melalui terminal."
        )

        print()
        print(
            f"Jalankan: instaloader -l {IG_USERNAME}"
        )

        print()
        print(
            "Detail:",
            e
        )

        return False


# =========================================================
# CEK POST SUDAH ADA
# =========================================================

def post_exists(post_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM posts
        WHERE post_id = ?
        """,
        (post_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


# =========================================================
# SIMPAN POSTINGAN BARU
# =========================================================

def save_new_post(
    post,
    hashtag
):

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().isoformat()

    post_id = "IG_" + post.shortcode

    caption = (
        post.caption
        if post.caption
        else ""
    )

    post_date = post.date_utc.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    url = (
        "https://www.instagram.com/p/"
        + post.shortcode
        + "/"
    )

    cursor.execute(
        """
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
            topic,

            first_seen_at,
            last_checked_at,
            collection_type,
            source_query

        )

        VALUES (
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?,
            ?, ?, ?, ?
        )
        """,

        (

            post_id,
            "Instagram",
            caption,
            post_date,
            "#" + hashtag,
            url,

            post.likes,
            post.comments,
            0,
            0,

            None,
            None,

            now,
            now,
            "historical_backfill",
            "#" + hashtag

        )
    )

    conn.commit()
    conn.close()

    print(
        "TERSIMPAN:",
        post.shortcode
    )


# =========================================================
# UPDATE POST YANG SUDAH ADA
# =========================================================

def update_existing_post(
    post
):

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().isoformat()

    post_id = "IG_" + post.shortcode

    cursor.execute(
        """
        UPDATE posts

        SET
            likes = ?,
            comments_count = ?,
            last_checked_at = ?

        WHERE post_id = ?
        """,

        (
            post.likes,
            post.comments,
            now,
            post_id
        )
    )


    # SIMPAN HISTORY ENGAGEMENT

    cursor.execute(
        """
        INSERT INTO engagement_history (

            post_id,
            checked_at,
            likes,
            comments,
            views,
            shares

        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,

        (
            post_id,
            now,
            post.likes,
            post.comments,
            0,
            0
        )
    )

    conn.commit()
    conn.close()

    print(
        "UPDATE:",
        post.shortcode,
        "| komentar:",
        post.comments
    )


# =========================================================
# PROSES SATU HASHTAG
# =========================================================

def collect_hashtag(hashtag_name):

    print()
    print("=" * 60)

    print(
        "HASHTAG:",
        "#" + hashtag_name
    )

    print("=" * 60)

    try:

        hashtag = instaloader.Hashtag.from_name(
            L.context,
            hashtag_name
        )

    except Exception as e:

        print(
            "Gagal membuka hashtag:",
            e
        )

        return


    jumlah_dicek = 0
    jumlah_baru = 0


    try:

        posts = hashtag.get_posts()

        for post in posts:

            jumlah_dicek += 1

            # ==============================================
            # FILTER MULAI JULI 2026
            # ==============================================

            if post.date_utc < START_DATE_OBJECT:
                continue


            post_id = (
                "IG_"
                + post.shortcode
            )


            print()
            print(
                "Tanggal:",
                post.date_utc
            )

            print(
                "ID:",
                post.shortcode
            )


            # ==============================================
            # POST BARU
            # ==============================================

            if not post_exists(
                post_id
            ):

                save_new_post(
                    post,
                    hashtag_name
                )

                jumlah_baru += 1


            # ==============================================
            # POST SUDAH ADA
            # UPDATE ENGAGEMENT
            # ==============================================

            else:

                update_existing_post(
                    post
                )


    except Exception as e:

        print()
        print(
            "ERROR ketika membaca postingan:"
        )

        print(e)


    print()
    print(
        "Jumlah dicek:",
        jumlah_dicek
    )

    print(
        "Posting baru:",
        jumlah_baru
    )


# =========================================================
# MAIN
# =========================================================

def main():

    create_tables()

    print()
    print(
        "========================================"
    )

    print(
        "INSTAGRAM COLLECTOR"
    )

    print(
        "========================================"
    )

    print(
        "Tanggal awal:",
        START_DATE
    )


    if not load_instagram_session():

        return


    for hashtag in HASHTAGS:

        collect_hashtag(
            hashtag
        )


    print()
    print(
        "========================================"
    )

    print(
        "COLLECTOR INSTAGRAM SELESAI"
    )

    print(
        "========================================"
    )


if __name__ == "__main__":

    main()