import asyncio
import os

from dotenv import load_dotenv
from TikTokApi import TikTokApi


load_dotenv()

MS_TOKEN = os.getenv("MS_TOKEN")


async def main():

    if not MS_TOKEN:
        print("ERROR: MS_TOKEN tidak ditemukan di file .env")
        return

    print("Mencoba koneksi ke TikTok...")

    async with TikTokApi() as api:

        await api.create_sessions(
        ms_tokens=[MS_TOKEN],
        num_sessions=1,
        sleep_after=5,
        browser="webkit",
        headless=False,
        timeout=120000
)

        print("Koneksi berhasil.")
        print("Mencoba mengambil video dari #bupatikarawang")
        print()

        hashtag = api.hashtag(
            name="bupatikarawang"
        )

        jumlah = 0

        async for video in hashtag.videos(count=10):

            jumlah += 1

            data = video.as_dict

            stats = (
                data.get("statsV2")
                or data.get("stats")
                or {}
            )

            print("=" * 60)

            print("VIDEO", jumlah)

            print(
                "ID:",
                data.get("id", "")
            )

            print(
                "Caption:",
                data.get("desc", "")
            )

            print(
                "Tanggal:",
                data.get("createTime", "")
            )

            print(
                "Views:",
                stats.get("playCount", 0)
            )

            print(
                "Likes:",
                stats.get("diggCount", 0)
            )

            print(
                "Komentar:",
                stats.get("commentCount", 0)
            )

            print(
                "Share:",
                stats.get("shareCount", 0)
            )

        print()
        print("=" * 60)
        print(
            "Total video yang berhasil dibaca:",
            jumlah
        )


if __name__ == "__main__":
    asyncio.run(main())