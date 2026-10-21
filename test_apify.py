import os
import requests

from dotenv import load_dotenv


load_dotenv()


TOKEN = os.getenv(
    "APIFY_API_TOKEN"
)

ACTOR_ID = os.getenv(
    "APIFY_TIKTOK_ACTOR_ID"
)


print("=" * 50)
print("TEST KONEKSI APIFY")
print("=" * 50)


if not TOKEN:

    print(
        "ERROR: APIFY_API_TOKEN tidak ditemukan."
    )

    raise SystemExit


if not ACTOR_ID:

    print(
        "ERROR: APIFY_TIKTOK_ACTOR_ID tidak ditemukan."
    )

    raise SystemExit


url = (
    "https://api.apify.com/v2/acts/"
    + ACTOR_ID
)


headers = {
    "Authorization":
        f"Bearer {TOKEN}"
}


try:

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )


    print(
        "HTTP Status:",
        response.status_code
    )


    if response.status_code == 200:

        data = response.json()

        actor = data.get(
            "data",
            {}
        )

        print()
        print(
            "KONEKSI APIFY BERHASIL"
        )

        print(
            "Actor:",
            actor.get(
                "name"
            )
        )

        print(
            "Username:",
            actor.get(
                "username"
            )
        )


    else:

        print()
        print(
            "KONEKSI GAGAL"
        )

        print(
            response.text
        )


except Exception as e:

    print(
        "ERROR:",
        e
    )