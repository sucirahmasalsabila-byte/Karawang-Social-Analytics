import os
import sys
import time
from datetime import datetime

import requests
from dotenv import load_dotenv


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(PROJECT_ROOT)


from database import get_connection, create_tables


# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

APIFY_TOKEN = os.getenv(
    "APIFY_API_TOKEN"
)

ACTOR_ID = os.getenv(
    "APIFY_TIKTOK_COMMENTS_ACTOR_ID"
)


# =========================================================
# SETTING
# =========================================================

BASE_URL = "https://api.apify.com/v2"

MAX_POSTS_PER_RUN = 10
MAX_COMMENTS_PER_POST = 50

POLL_SECONDS = 5
MAX_WAIT_SECONDS = 300


# =========================================================
# VALIDASI
# =========================================================

def check_config():

    if not APIFY_TOKEN:

        raise RuntimeError(
            "APIFY_API_TOKEN belum ada di .env"
        )

    if not ACTOR_ID:

        raise RuntimeError(
            "APIFY_TIKTOK_COMMENTS_ACTOR_ID "
            "belum ada di .env"
        )


# =========================================================
# HEADER
# =========================================================

def headers():

    return {
        "Authorization":
            f"Bearer {APIFY_TOKEN}",

        "Content-Type":
            "application/json"
    }


# =========================================================
# HELPER
# =========================================================

def safe_text(value):

    if value is None:
        return ""

    return str(value)


def safe_int(value):

    try:

        if value is None:
            return 0

        return int(
            float(value)
        )

    except Exception:

        return 0


# =========================================================
# AMBIL POST TIKTOK DARI DATABASE
# =========================================================

def get_tiktok_posts():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            post_id,
            url

        FROM posts

        WHERE platform = 'TikTok'
          AND url IS NOT NULL
          AND TRIM(url) != ''
          AND topic IS NOT NULL
          AND topic != 'Lainnya'

        ORDER BY id DESC

        LIMIT ?
        """,
        (
            MAX_POSTS_PER_RUN,
        )
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


# =========================================================
# JALANKAN ACTOR KOMENTAR
# =========================================================

def start_actor(posts):

    post_urls = []

    for post_id, url in posts:

        if url:

            post_urls.append({
                "url": url
            })


    input_data = {

        "postUrls":
            post_urls,

        "maxCommentsPerPost":
            MAX_COMMENTS_PER_POST,

        "includeReplies":
            False
    }


    url = (
        f"{BASE_URL}/acts/"
        f"{ACTOR_ID}/runs"
    )


    print()
    print(
        "Menjalankan TikTok Comments Actor..."
    )


    response = requests.post(
        url,
        headers=headers(),
        json=input_data,
        timeout=60
    )


    if response.status_code not in [
        200,
        201,
        202
    ]:

        raise RuntimeError(
            f"Gagal menjalankan Actor "
            f"{response.status_code}: "
            f"{response.text}"
        )


    data = response.json().get(
        "data",
        {}
    )


    run_id = data.get(
        "id"
    )


    if not run_id:

        raise RuntimeError(
            "Run ID tidak ditemukan."
        )


    print(
        "Run ID:",
        run_id
    )


    return run_id


# =========================================================
# TUNGGU ACTOR SELESAI
# =========================================================

def wait_for_run(run_id):

    url = (
        f"{BASE_URL}/actor-runs/"
        f"{run_id}"
    )


    waited = 0


    while waited < MAX_WAIT_SECONDS:

        response = requests.get(
            url,
            headers=headers(),
            timeout=30
        )


        if response.status_code != 200:

            raise RuntimeError(
                f"Gagal cek run "
                f"{response.status_code}: "
                f"{response.text}"
            )


        data = response.json().get(
            "data",
            {}
        )


        status = data.get(
            "status"
        )


        print(
            "Status:",
            status
        )


        if status == "SUCCEEDED":

            dataset_id = data.get(
                "defaultDatasetId"
            )


            if not dataset_id:

                raise RuntimeError(
                    "Dataset ID tidak ditemukan."
                )


            print(
                "Dataset ID:",
                dataset_id
            )


            return dataset_id


        if status in [
            "FAILED",
            "ABORTED",
            "TIMED-OUT"
        ]:

            raise RuntimeError(
                f"Actor berhenti "
                f"dengan status {status}"
            )


        time.sleep(
            POLL_SECONDS
        )

        waited += POLL_SECONDS


    raise TimeoutError(
        "Actor belum selesai "
        "setelah 5 menit."
    )


# =========================================================
# AMBIL DATASET HASIL ACTOR
# =========================================================

def get_dataset_items(
    dataset_id
):

    url = (
        f"{BASE_URL}/datasets/"
        f"{dataset_id}/items"
    )


    response = requests.get(
        url,
        headers=headers(),
        params={
            "clean":
                "true",

            "format":
                "json"
        },
        timeout=60
    )


    if response.status_code != 200:

        raise RuntimeError(
            f"Gagal mengambil dataset "
            f"{response.status_code}: "
            f"{response.text}"
        )


    records = response.json()


    if not isinstance(
        records,
        list
    ):

        raise RuntimeError(
            "Format hasil komentar "
            "bukan list."
        )


    return records


# =========================================================
# SIMPAN KOMENTAR
# =========================================================

def save_comments(records):

    create_tables()

    conn = get_connection()
    cursor = conn.cursor()

    baru = 0
    update = 0
    gagal = 0


    for item in records:

        try:

            if not isinstance(
                item,
                dict
            ):

                continue


            # =====================================
            # COMMENT ID
            # =====================================

            raw_comment_id = safe_text(
                item.get(
                    "commentId",
                    ""
                )
            ).strip()


            if not raw_comment_id:

                gagal += 1
                continue


            comment_id = (
                "TTC_"
                + raw_comment_id
            )


            # =====================================
            # TEXT KOMENTAR
            # =====================================

            text = safe_text(
                item.get(
                    "text",
                    ""
                )
            ).strip()


            if not text:

                gagal += 1
                continue


            # =====================================
            # VIDEO ID / POST ID
            # =====================================

            video_id = safe_text(
                item.get(
                    "videoId",
                    ""
                )
            ).strip()


            if not video_id:

                gagal += 1
                continue


            post_id = (
                "TT_"
                + video_id
            )


            # =====================================
            # PASTIKAN POST ADA DI DATABASE
            # =====================================

            cursor.execute(
                """
                SELECT id
                FROM posts
                WHERE post_id = ?
                """,
                (
                    post_id,
                )
            )


            post_exists = (
                cursor.fetchone()
            )


            if not post_exists:

                print(
                    "POST TIDAK DITEMUKAN:",
                    post_id
                )

                gagal += 1
                continue


            # =====================================
            # DATA KOMENTAR
            # =====================================

            tanggal = safe_text(
                item.get(
                    "createTime",
                    ""
                )
            )


            username = safe_text(
                item.get(
                    "username",
                    ""
                )
            )


            likes = safe_int(
                item.get(
                    "likeCount",
                    0
                )
            )


            # =====================================
            # CEK DUPLIKAT
            # =====================================

            cursor.execute(
                """
                SELECT id
                FROM comments
                WHERE comment_id = ?
                """,
                (
                    comment_id,
                )
            )


            existing = (
                cursor.fetchone()
            )


            # =====================================
            # UPDATE KOMENTAR
            # =====================================

            if existing:

                cursor.execute(
                    """
                    UPDATE comments

                    SET
                        post_id = ?,
                        text = ?,
                        tanggal = ?,
                        username = ?,
                        likes = ?

                    WHERE comment_id = ?
                    """,
                    (
                        post_id,
                        text,
                        tanggal,
                        username,
                        likes,
                        comment_id
                    )
                )


                update += 1


            # =====================================
            # INSERT KOMENTAR BARU
            # =====================================

            else:

                cursor.execute(
                    """
                    INSERT INTO comments (

                        comment_id,
                        post_id,
                        platform,
                        text,
                        tanggal,
                        username,
                        likes,
                        sentiment,
                        topic
                    )

                    VALUES (
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?
                    )
                    """,
                    (
                        comment_id,
                        post_id,
                        "TikTok",
                        text,
                        tanggal,
                        username,
                        likes,
                        None,
                        None
                    )
                )


                baru += 1


        except Exception as e:

            gagal += 1

            print(
                "ERROR COMMENT:",
                e
            )


    conn.commit()
    conn.close()


    print()
    print("=" * 50)
    print("HASIL TIKTOK COMMENTS")
    print("=" * 50)

    print(
        "Komentar baru:",
        baru
    )

    print(
        "Komentar update:",
        update
    )

    print(
        "Komentar gagal:",
        gagal
    )


    return baru


# =========================================================
# COLLECTOR UTAMA
# =========================================================

def collect_tiktok_comments():

    print()
    print("=" * 50)
    print("TIKTOK COMMENTS COLLECTOR")
    print("=" * 50)


    check_config()


    posts = get_tiktok_posts()


    if not posts:

        print(
            "Tidak ada URL post TikTok."
        )

        return 0


    print(
        "Post yang akan dicek:",
        len(posts)
    )


    run_id = start_actor(
        posts
    )


    dataset_id = wait_for_run(
        run_id
    )


    records = get_dataset_items(
        dataset_id
    )


    print(
        "Jumlah komentar diterima:",
        len(records)
    )


    return save_comments(
        records
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    collect_tiktok_comments()