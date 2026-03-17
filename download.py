import requests
import json
import os
from urllib.parse import urlparse, unquote
from pathlib import Path
from config import SELECTED_FILE, IMAGES_DIR


def get_filename_from_url(url, exercise_id):
    parsed = urlparse(url)
    path = unquote(parsed.path)
    ext = Path(path).suffix or ".jpg"
    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        ext = ".jpg"
    return f"{exercise_id}{ext}"


def download_images():
    if not os.path.exists(SELECTED_FILE):
        print(f"Error: {SELECTED_FILE} not found. Run 'select' first.")
        return None

    os.makedirs(IMAGES_DIR, exist_ok=True)

    with open(SELECTED_FILE, "r") as f:
        selected_data = json.load(f)

    for exercise_id, data in selected_data.items():
        if data.get("local_path") and os.path.exists(data["local_path"]):
            print(f"Skipping {data['name']}: already downloaded")
            continue

        url = data.get("selected_url")
        if not url:
            print(f"Skipping {data['name']}: no URL selected")
            continue

        try:
            print(f"Downloading {data['name']}...")
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            filename = get_filename_from_url(url, exercise_id)
            local_path = os.path.join(IMAGES_DIR, filename)

            with open(local_path, "wb") as f:
                f.write(response.content)

            data["local_path"] = local_path
            print(f"  Saved to {local_path}")

        except Exception as e:
            print(f"  Error downloading: {e}")

    with open(SELECTED_FILE, "w") as f:
        json.dump(selected_data, f, indent=2)

    print(f"\nDownloads complete. Updated {SELECTED_FILE}")
    return selected_data
