import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")

# Dataset yang BARUSAN berhasil
DATASET_ID = "JONrbWzOsDVk6ULVP"

url = (
    f"https://api.apify.com/v2/datasets/"
    f"{DATASET_ID}/items"
)

response = requests.get(
    url,
    headers={
        "Authorization": f"Bearer {APIFY_TOKEN}"
    },
    params={
        "clean": "true",
        "format": "json",
        "limit": 3
    },
    timeout=60
)

print("=" * 70)
print("CEK STRUKTUR KOMENTAR APIFY")
print("=" * 70)

print("HTTP:", response.status_code)

if response.status_code != 200:
    print(response.text)
    raise SystemExit()

records = response.json()

print("Jumlah contoh:", len(records))
print()

for nomor, item in enumerate(records, start=1):

    print("=" * 70)
    print("KOMENTAR", nomor)
    print("=" * 70)

    print("FIELD YANG TERSEDIA:")
    print(list(item.keys()))

    print()
    print("ISI DATA:")
    print(
        json.dumps(
            item,
            indent=2,
            ensure_ascii=False
        )
    )

    print()