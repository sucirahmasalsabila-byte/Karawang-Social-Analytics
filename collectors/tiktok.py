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
from watchlist import HASHTAGS


# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

APIFY_TOKEN = os.getenv(
    "APIFY_API_TOKEN"
)

ACTOR_ID = os.getenv(
    "APIFY_TIKTOK_ACTOR_ID"
)


# =========================================================
# SETTING
# =========================================================

VIDEOS_PER_HASHTAG = 10

POLL_SECONDS = 5
MAX_WAIT_SECONDS = 300


# =========================================================
# API URL
# =========================================================

BASE_URL = "https://api.apify.com/v2"


# =========================================================
# VALIDASI CONFIG
# =========================================================

def check_config():

    if not APIFY_TOKEN:

        raise RuntimeError(
            "APIFY_API_TOKEN belum ada di .env"
        )

    if not ACTOR_ID:

        raise RuntimeError(
            "APIFY_TIKTOK_ACTOR_ID belum ada di .env"
        )


# =========================================================
# HEADER API
# =========================================================

def headers():

    return {
        "Authorization":
            f"Bearer {APIFY_TOKEN}",

        "Content-Type":
            "application/json"
    }


# =========================================================
# TRIGGER ACTOR
# =========================================================

def start_actor():

    input_data = {

        "hashtags": HASHTAGS,

        "country": "Indonesia",

        "numberOfVideos": VIDEOS_PER_HASHTAG
    }


    url = (
        f"{BASE_URL}/acts/"
        f"{ACTOR_ID}/runs"
    )


    print()
    print(
        "Menjalankan Actor TikTok Apify..."
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


    result = response.json()

    data = result.get(
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
# TUNGGU RUN SELESAI
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
                f"Gagal cek run: "
                f"{response.status_code} "
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
                    "Dataset ID hasil run "
                    "tidak ditemukan."
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
                f"Actor berhenti dengan "
                f"status {status}"
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
# AMBIL HASIL DATASET
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
            "clean": "true",
            "format": "json"
        },
        timeout=60
    )


    if response.status_code != 200:

        raise RuntimeError(
            f"Gagal mengambil dataset: "
            f"{response.status_code} "
            f"{response.text}"
        )


    data = response.json()


    if not isinstance(
        data,
        list
    ):

        raise RuntimeError(
            "Format dataset Apify "
            "tidak berupa list."
        )


    return data


# =========================================================
# HELPER
# =========================================================

def first_value(
    data,
    *keys,
    default=None
):

    for key in keys:

        if key in data:

            value = data.get(
                key
            )

            if value is not None:

                return value


    return default


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

    except:

        return 0


# =========================================================
# SIMPAN KE DATABASE
# =========================================================

def save_records(records):

    create_tables()

    conn = get_connection()
    cursor = conn.cursor()

    jumlah_baru = 0
    jumlah_update = 0
    jumlah_gagal = 0

    for item in records:

        try:

            if not isinstance(item, dict):
                continue

            # =====================================
            # ID VIDEO
            # =====================================

            raw_id = safe_text(
                first_value(
                    item,
                    "aweme_id",
                    "Aweme_id",
                    "id",
                    "video_id",
                    default=""
                )
            ).strip()

            url = safe_text(
                first_value(
                    item,
                    "share_url",
                    "webVideoUrl",
                    "web_video_url",
                    "url",
                    "video_url",
                    default=""
                )
            )

            if not raw_id and url:
                raw_id = (
                    url.rstrip("/")
                    .split("/")[-1]
                    .split("?")[0]
                )

            if not raw_id:
                jumlah_gagal += 1
                continue

            post_id = "TT_" + raw_id

            # =====================================
            # CAPTION
            # =====================================

            caption = safe_text(
                first_value(
                    item,
                    "desc",
                    "Desc",
                    "text",
                    "description",
                    "caption",
                    default=""
                )
            )

            # =====================================
            # TANGGAL
            # =====================================

            tanggal = safe_text(
                first_value(
                    item,
                    "create_time",
                    "Create_time",
                    "createTimeISO",
                    "date_posted",
                    default=""
                )
            )

            if tanggal.isdigit():
                try:
                    tanggal = datetime.fromtimestamp(
                        int(tanggal)
                    ).isoformat()
                except Exception:
                    pass

            # =====================================
            # ENGAGEMENT DARI statistics
            # =====================================

            statistics = item.get("statistics", {})

            if not isinstance(statistics, dict):
                statistics = {}

            likes = safe_int(
                statistics.get("digg_count", 0)
            )

            comments_count = safe_int(
                statistics.get("comment_count", 0)
            )

            views = safe_int(
                statistics.get("play_count", 0)
            )

            shares = safe_int(
                statistics.get("share_count", 0)
            )

            if likes == 0:
                likes = safe_int(
                    first_value(
                        item,
                        "digg_count",
                        "diggCount",
                        "likes",
                        "like_count",
                        default=0
                    )
                )

            if comments_count == 0:
                comments_count = safe_int(
                    first_value(
                        item,
                        "comment_count",
                        "commentCount",
                        "comments",
                        default=0
                    )
                )

            if views == 0:
                views = safe_int(
                    first_value(
                        item,
                        "play_count",
                        "playCount",
                        "views",
                        "view_count",
                        default=0
                    )
                )

            if shares == 0:
                shares = safe_int(
                    first_value(
                        item,
                        "share_count",
                        "shareCount",
                        "shares",
                        default=0
                    )
                )

            # =====================================
            # HASHTAG / SOURCE
            # =====================================

            hashtag = safe_text(
                first_value(
                    item,
                    "hashtag",
                    "searchHashtag",
                    "search_hashtag",
                    default=""
                )
            )

            if not hashtag:
                text_extra = item.get("text_extra", [])

                if isinstance(text_extra, list):
                    hashtag_names = []

                    for tag in text_extra:
                        if isinstance(tag, dict):
                            name = tag.get("hashtag_name")
                            if name:
                                hashtag_names.append(name)

                    if hashtag_names:
                        hashtag = "#" + ", #".join(hashtag_names)

            now = datetime.now().isoformat()

            # =====================================
            # CEK POST SUDAH ADA
            # =====================================

            cursor.execute(
                """
                SELECT id
                FROM posts
                WHERE post_id = ?
                """,
                (post_id,)
            )

            existing = cursor.fetchone()

            # =====================================
            # UPDATE
            # =====================================

            if existing:

                cursor.execute(
                    """
                    UPDATE posts
                    SET
                        caption = ?,
                        tanggal = ?,
                        hashtag = ?,
                        url = ?,
                        likes = ?,
                        comments_count = ?,
                        views = ?,
                        shares = ?,
                        last_checked_at = ?
                    WHERE post_id = ?
                    """,
                    (
                        caption,
                        tanggal,
                        hashtag,
                        url,
                        likes,
                        comments_count,
                        views,
                        shares,
                        now,
                        post_id
                    )
                )

                jumlah_update += 1

            # =====================================
            # INSERT
            # =====================================

            else:

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
                        "TikTok",
                        caption,
                        tanggal,
                        hashtag,
                        url,
                        likes,
                        comments_count,
                        views,
                        shares,
                        None,
                        None,
                        now,
                        now,
                        "automatic",
                        "Apify"
                    )
                )

                jumlah_baru += 1

            # =====================================
            # ENGAGEMENT HISTORY
            # =====================================

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
                    likes,
                    comments_count,
                    views,
                    shares
                )
            )

        except Exception as e:

            jumlah_gagal += 1

            print(
                "ERROR RECORD:",
                e
            )

    conn.commit()
    conn.close()

    print()
    print("=" * 50)
    print("HASIL TIKTOK APIFY")
    print("=" * 50)

    print(
        "Posting baru:",
        jumlah_baru
    )

    print(
        "Posting diperbarui:",
        jumlah_update
    )

    print(
        "Record gagal:",
        jumlah_gagal
    )

    return jumlah_baru


# =========================================================
# COLLECTOR UTAMA
# =========================================================

def collect_tiktok():

    print()
    print("=" * 50)
    print("TIKTOK APIFY COLLECTOR")
    print("=" * 50)


    check_config()


    run_id = start_actor()


    dataset_id = wait_for_run(
        run_id
    )


    records = get_dataset_items(
        dataset_id
    )


    print(
        "Jumlah record diterima:",
        len(records)
    )


    jumlah_baru = save_records(
        records
    )


    return jumlah_baru


# =========================================================
# KOMPATIBEL DENGAN collector_manager.py
# =========================================================

def run_backfill():

    return collect_tiktok()


if __name__ == "__main__":

    collect_tiktok()