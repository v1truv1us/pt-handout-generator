import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urljoin, urlparse
from config import EXERCISES, BUILD_DIR, CANDIDATES_FILE


def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def extract_image_candidates(html, base_url):
    soup = BeautifulSoup(html, "lxml")
    candidates = []

    for img in soup.find_all("img"):
        src = (
            img.get("src")
            or img.get("data-src")
            or img.get("data-lazy-src")
            or img.get("data-original")
        )
        if not src:
            continue

        src = urljoin(base_url, src)
        if not src.startswith(("http://", "https://")):
            continue

        srcset = img.get("srcset")
        if srcset:
            srcset_urls = [s.strip().split()[0] for s in srcset.split(",") if s.strip()]
            for s in srcset_urls:
                full_url = urljoin(base_url, s)
                if full_url not in [c["url"] for c in candidates]:
                    candidates.append(
                        {
                            "url": full_url,
                            "alt": img.get("alt", ""),
                            "width": img.get("width"),
                            "height": img.get("height"),
                        }
                    )

        if src not in [c["url"] for c in candidates]:
            candidates.append(
                {
                    "url": src,
                    "alt": img.get("alt", ""),
                    "width": img.get("width"),
                    "height": img.get("height"),
                }
            )

    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        url = urljoin(base_url, og_image["content"])
        if url not in [c["url"] for c in candidates]:
            candidates.append({"url": url, "alt": "", "width": None, "height": None})

    return candidates


def score_candidate(candidate, exercise_name):
    score = 0
    url = candidate["url"].lower()
    alt = candidate["alt"].lower()

    exercise_keywords = exercise_name.lower().split()
    for keyword in exercise_keywords:
        if keyword in alt:
            score += 20
        if keyword in url:
            score += 10

    good_patterns = ["exercise", "workout", "fitness", "how-to", "demo", "tutorial"]
    for pattern in good_patterns:
        if pattern in url or pattern in alt:
            score += 5

    bad_patterns = [
        "logo",
        "icon",
        "avatar",
        "banner",
        "header",
        "footer",
        "ad",
        "sponsor",
    ]
    for pattern in bad_patterns:
        if pattern in url or pattern in alt:
            score -= 30

    width = candidate.get("width")
    height = candidate.get("height")
    if width and height:
        try:
            w = int(width)
            h = int(height)
            if 200 <= w <= 800 and 150 <= h <= 600:
                score += 15
            elif w < 100 or h < 100:
                score -= 20
        except (ValueError, TypeError):
            pass

    if any(ext in url for ext in [".jpg", ".jpeg", ".png", ".webp"]):
        score += 5

    return max(score, 0)


def get_image_dimensions(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < 5000:
            return None, None
        return None, None
    except:
        return None, None


def discover_images():
    os.makedirs(BUILD_DIR, exist_ok=True)
    results = []

    for exercise in EXERCISES:
        print(f"Discovering images for: {exercise['name']}")
        try:
            html = fetch_page(exercise["source_url"])
            candidates = extract_image_candidates(html, exercise["source_url"])

            for c in candidates:
                c["score"] = score_candidate(c, exercise["name"])

            candidates.sort(key=lambda x: x["score"], reverse=True)
            top_candidates = candidates[:10]

            results.append(
                {
                    "id": exercise["id"],
                    "name": exercise["name"],
                    "source_page": exercise["source_url"],
                    "reps": exercise["reps"],
                    "candidates": top_candidates,
                }
            )
            print(f"  Found {len(top_candidates)} candidates")

        except Exception as e:
            print(f"  Error: {e}")
            results.append(
                {
                    "id": exercise["id"],
                    "name": exercise["name"],
                    "source_page": exercise["source_url"],
                    "reps": exercise["reps"],
                    "candidates": [],
                    "error": str(e),
                }
            )

    with open(CANDIDATES_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nCandidates saved to {CANDIDATES_FILE}")
    return results
