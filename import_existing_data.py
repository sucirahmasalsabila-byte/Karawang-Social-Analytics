import pandas as pd

from database import get_connection, create_tables


TIKTOK_FILE = "dataset/tiktok.csv"
INSTAGRAM_FILE = "dataset/instagram.csv"


# =========================================================
# HELPER
# =========================================================

def safe_text(value):

    if pd.isna(value):
        return ""

    return str(value)


def safe_int(value):

    try:

        if pd.isna(value):
            return 0

        return int(float(value))

    except Exception:

        return 0


# =========================================================
# IMPORT TIKTOK
# =========================================================

def import_tiktok():

    print()
    print("=" * 60)
    print("IMPORT DATA TIKTOK")
    print("=" * 60)

    df = pd.read_csv(
        TIKTOK_FILE,
        low_memory=False
    )

    print(
        "Jumlah data TikTok:",
        len(df)
    )

    conn = get_connection()
    cursor = conn.cursor()

    baru = 0
    update = 0
    gagal = 0


    for index, row in df.iterrows():

        try:

            raw_id = safe_text(
                row.get("id", "")
            ).strip()

            if raw_id == "":
                gagal += 1
                continue

            post_id = "TT_" + raw_id


            caption = safe_text(
                row.get(
                    "text",
                    ""
                )
            )


            tanggal = safe_text(
                row.get(
                    "createTimeISO",
                    ""
                )
            )


            hashtag = safe_text(
                row.get(
                    "searchHashtag/name",
                    ""
                )
            )


            url = safe_text(
                row.get(
                    "webVideoUrl",
                    ""
                )
            )


            likes = safe_int(
                row.get(
                    "diggCount",
                    0
                )
            )


            comments_count = safe_int(
                row.get(
                    "commentCount",
                    0
                )
            )


            views = safe_int(
                row.get(
                    "playCount",
                    0
                )
            )


            shares = safe_int(
                row.get(
                    "shareCount",
                    0
                )
            )


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

            existing = cursor.fetchone()


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
                        last_checked_at =
                            CURRENT_TIMESTAMP

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
                        post_id
                    )
                )

                update += 1


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
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP,
                        ?, ?
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

                        "historical_backfill",
                        hashtag
                    )
                )

                baru += 1


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

                VALUES (
                    ?,
                    CURRENT_TIMESTAMP,
                    ?,
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    post_id,
                    likes,
                    comments_count,
                    views,
                    shares
                )
            )


            if (
                index + 1
            ) % 50 == 0:

                print(
                    f"TikTok "
                    f"{index + 1}/{len(df)}"
                )


        except Exception as e:

            gagal += 1

            print(
                f"TikTok ERROR baris "
                f"{index + 1}:",
                e
            )


    conn.commit()
    conn.close()


    print()
    print(
        "TikTok baru  :",
        baru
    )

    print(
        "TikTok update:",
        update
    )

    print(
        "TikTok gagal :",
        gagal
    )


# =========================================================
# IMPORT INSTAGRAM
# =========================================================

def import_instagram():

    print()
    print("=" * 60)
    print("IMPORT DATA INSTAGRAM")
    print("=" * 60)

    df = pd.read_csv(
        INSTAGRAM_FILE,
        low_memory=False
    )

    print(
        "Jumlah data Instagram:",
        len(df)
    )

    conn = get_connection()
    cursor = conn.cursor()

    baru = 0
    update = 0
    gagal = 0


    for index, row in df.iterrows():

        try:

            shortcode = safe_text(
                row.get(
                    "shortCode",
                    ""
                )
            ).strip()


            if shortcode == "":
                gagal += 1
                continue


            post_id = (
                "IG_"
                + shortcode
            )


            caption = safe_text(
                row.get(
                    "caption",
                    ""
                )
            )


            tanggal = safe_text(
                row.get(
                    "tanggal",
                    ""
                )
            )


            url = safe_text(
                row.get(
                    "postUrl",
                    ""
                )
            )


            akun = safe_text(
                row.get(
                    "akun",
                    ""
                )
            )


            likes = safe_int(
                row.get(
                    "likesCount",
                    0
                )
            )


            comments_count = safe_int(
                row.get(
                    "commentsCount",
                    0
                )
            )


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

            existing = cursor.fetchone()


            if existing:

                cursor.execute(
                    """
                    UPDATE posts

                    SET
                        caption = ?,
                        tanggal = ?,
                        url = ?,
                        likes = ?,
                        comments_count = ?,
                        last_checked_at =
                            CURRENT_TIMESTAMP

                    WHERE post_id = ?
                    """,
                    (
                        caption,
                        tanggal,
                        url,
                        likes,
                        comments_count,
                        post_id
                    )
                )

                update += 1


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
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP,
                        ?, ?
                    )
                    """,
                    (
                        post_id,
                        "Instagram",
                        caption,
                        tanggal,
                        "",
                        url,

                        likes,
                        comments_count,
                        0,
                        0,

                        None,
                        None,

                        "historical_backfill",
                        akun
                    )
                )

                baru += 1


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

                VALUES (
                    ?,
                    CURRENT_TIMESTAMP,
                    ?,
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    post_id,
                    likes,
                    comments_count,
                    0,
                    0
                )
            )


        except Exception as e:

            gagal += 1

            print(
                f"Instagram ERROR baris "
                f"{index + 1}:",
                e
            )


    conn.commit()
    conn.close()


    print()
    print(
        "Instagram baru  :",
        baru
    )

    print(
        "Instagram update:",
        update
    )

    print(
        "Instagram gagal :",
        gagal
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
        "IMPORT DATA HISTORIS"
    )

    print(
        "========================================"
    )


    import_tiktok()

    import_instagram()


    print()
    print(
        "========================================"
    )

    print(
        "IMPORT SELESAI"
    )

    print(
        "========================================"
    )


if __name__ == "__main__":

    main()