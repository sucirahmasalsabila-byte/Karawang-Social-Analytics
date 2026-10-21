import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("APIFY_API_TOKEN")
ACTOR_ID = os.getenv("APIFY_TIKTOK_ACTOR_ID")

BASE_URL = "https://api.apify.com/v2"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}


# Ambil run terakhir Actor
url_runs = (
    f"{BASE_URL}/acts/"
    f"{ACTOR_ID}/runs"
)

response = requests.get(
    url_runs,
    headers=headers,
    params={
        "limit": 1,
        "desc": 1
    },
    timeout=30
)

response.raise_for_status()

runs = response.json()["data"]["items"]

if not runs:
    print("Tidak ada run ditemukan.")
    raise SystemExit

run = runs[0]

dataset_id = run["defaultDatasetId"]

print("Run ID:", run["id"])
print("Dataset ID:", dataset_id)


# Ambil SATU record saja
url_dataset = (
    f"{BASE_URL}/datasets/"
    f"{dataset_id}/items"
)

response = requests.get(
    url_dataset,
    headers=headers,
    params={
        "clean": "true",
        "format": "json",
        "limit": 1
    },
    timeout=30
)

response.raise_for_status()

items = response.json()

if not items:
    print("Dataset kosong.")
    raise SystemExit

item = items[0]

print()
print("=" * 70)
print("FIELD YANG DIKEMBALIKAN APIFY")
print("=" * 70)

for key, value in item.items():

    if isinstance(value, dict):

        print()
        print(f"{key} = DICTIONARY")

        for subkey, subvalue in value.items():

            print(
                f"   {subkey}: {subvalue}"
            )

    else:

        print(
            f"{key}: {value}"
        )