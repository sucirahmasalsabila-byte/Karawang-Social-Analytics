import time
from datetime import datetime

from collector_manager import collect_all
from pipeline import run_pipeline


# ==========================================
# INTERVAL MONITORING
# ==========================================

INTERVAL_SECONDS = 60 * 60 * 6
# 6 jam sekali


def main():

    print("=" * 50)
    print("SCHEDULER MONITORING DIMULAI")
    print("=" * 50)

    while True:

        print()
        print(
            "Siklus monitoring:",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        try:

            # ======================================
            # 1. AMBIL DATA BARU
            # ======================================

            print()
            print("1. Mengambil data baru...")

            jumlah_data_baru = collect_all()


            # ======================================
            # 2. ANALISIS DATA BARU
            # ======================================

            print()
            print("2. Menjalankan analisis...")

            run_pipeline()


            # ======================================
            # HASIL
            # ======================================

            print()
            print(
                "Total data baru ditemukan:",
                jumlah_data_baru
            )

        except Exception as e:

            print()
            print(
                "ERROR SCHEDULER:",
                e
            )


        # ==========================================
        # TUNGGU SIKLUS BERIKUTNYA
        # ==========================================

        jam = INTERVAL_SECONDS // 3600

        print()
        print(
            f"Menunggu {jam} jam "
            "untuk pengecekan berikutnya..."
        )

        time.sleep(
            INTERVAL_SECONDS
        )


if __name__ == "__main__":
    main()