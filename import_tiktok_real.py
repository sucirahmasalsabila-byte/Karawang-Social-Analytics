import pandas as pd

from database import get_connection, create_tables


CSV_FILE = "dataset/tiktok.csv"


def safe_int(value):
    try:
        if pd.isna(value):
            return 0

        return int(float(value))

    except:
        return 0


def safe_text(value):
    if pd.isna(value):
        return ""

    return str(value)


def import_tiktok():

    create_tables()

    print("=" * 60)
    print("IMPORT DATA TIKTOK ASLI")
    print("=" * 60)

    print("Membaca dataset TikTok...")

    df = pd.read_csv(
        CSV_FILE,
        low_memory=False
    )

    print(
        "Jumlah data CSV:",
        len(df)
    )

    conn = get_connection()
    cursor = conn.cursor()

    jumlah_baru = 0
    jumlah_update = 0
    jumlah_gagal = 0


    for index, row in df.iterrows():

        try:

            # ==========================================
            # ID VIDEO
            # ==========================================

            raw_id = safe_text(
                row.get("id", "")
            ).strip()

            if raw_id == "":
                jumlah_gagal += 1
                continue

            post_id = "TT_" + raw_id


            # ==========================================
            # DATA POSTINGAN
            # ==========================================

            caption = safe_text(
                row.get("text", "")
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


            # ==========================================
            # ENGAGEMENT
            # ==========================================

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


            # ==========================================
            # CEK SUDAH ADA ATAU BELUM
            # ==========================================

            cursor.execute(
                """
                SELECT id
                FROM posts
                WHERE post_id = ?
                """,
                (post_id,)
            )

            existing = cursor.fetchone()


            # ==========================================
            # UPDATE JIKA SUDAH ADA
            # ==========================================

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

                jumlah_update += 1


            # ==========================================
            # INSERT JIKA BELUM ADA
            # ==========================================

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

                jumlah_baru += 1


            # ==========================================
            # SIMPAN ENGAGEMENT HISTORY
            # ==========================================

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


            # ==========================================
            # PROGRESS
            # ==========================================

            if (index + 1) % 25 == 0:

                print(
                    f"Memproses "
                    f"{index + 1}/{len(df)}"
                )


        except Exception as e:

            jumlah_gagal += 1

            print(
                f"ERROR baris {index + 1}:",
                e
            )


    # ==============================================
    # SIMPAN
    # ==============================================

    conn.commit()
    conn.close()


    print()
    print("=" * 60)
    print("IMPORT TIKTOK SELESAI")
    print("=" * 60)

    print(
        "Posting baru :",
        jumlah_baru
    )

    print(
        "Posting update:",
        jumlah_update
    )

    print(
        "Data gagal   :",
        jumlah_gagal
    )

    print(
        "Total CSV    :",
        len(df)
    )

    print("=" * 60)


if __name__ == "__main__":
    import_tiktok()