from datetime import datetime

# ==========================================
# IMPORT COLLECTOR
# ==========================================

from collectors.instagram import main as collect_instagram
from collectors.tiktok import run_backfill as collect_tiktok


def collect_all():

    print()
    print("=" * 50)
    print("MEMULAI PENGAMBILAN DATA")
    print("=" * 50)

    print(
        "Waktu:",
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    jumlah_instagram = 0
    jumlah_tiktok = 0


    # ==========================================
    # INSTAGRAM
    # ==========================================

    print()
    print("INSTAGRAM")
    print("-" * 50)

    try:

        hasil_instagram = collect_instagram()

        if isinstance(hasil_instagram, int):
            jumlah_instagram = hasil_instagram

    except Exception as e:

        print()
        print(
            "Instagram ERROR:",
            e
        )


    # ==========================================
    # TIKTOK
    # ==========================================

    print()
    print("TIKTOK")
    print("-" * 50)

    try:

        hasil_tiktok = collect_tiktok()

        if isinstance(hasil_tiktok, int):
            jumlah_tiktok = hasil_tiktok

    except Exception as e:

        print()
        print(
            "TikTok ERROR:",
            e
        )


    # ==========================================
    # HASIL
    # ==========================================

    print()
    print("=" * 50)

    print(
        "Data Instagram baru:",
        jumlah_instagram
    )

    print(
        "Data TikTok baru:",
        jumlah_tiktok
    )

    print("=" * 50)
    print("PENGAMBILAN DATA SELESAI")
    print("=" * 50)

    return (
        jumlah_instagram
        + jumlah_tiktok
    )


if __name__ == "__main__":
    collect_all()