import os
import requests
from dotenv import load_dotenv

from collectors.tiktok_comments import save_comments


load_dotenv()

APIFY_TOKEN = os.getenv(
    "APIFY_API_TOKEN"
)

DATASET_ID = "JONrbWzOsDVk6ULVP"


url = (
    "https://api.apify.com/v2/"
    f"datasets/{DATASET_ID}/items"
)


response = requests.get(
    url,
    headers={
        "Authorization":
            f"Bearer {APIFY_TOKEN}"
    },
    params={
        "clean": "true",
        "format": "json"
    },
    timeout=60
)


response.raise_for_status()

records = response.json()


print(
    "Komentar dari Apify:",
    len(records)
)


save_comments(
    records
)