import requests
import json
import time
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import quote
from PIL import Image, ImageDraw
from io import BytesIO
from PIL import Image, UnidentifiedImageError

# -------------------------
# CONFIG
# -------------------------

_USED_IMAGE_URLS = set()
_USED_DOMAINS = set()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

IMG_DIR = Path("assets/images")
IMG_DIR.mkdir(parents=True, exist_ok=True)

# Reuse HTTP connections (prevents SSL timeout issues)
_SESSION = requests.Session()
_SESSION.headers.update(HEADERS)

# -------------------------
# DOMAIN QUALITY TIERS
# -------------------------

TIER_1 = [
    "geeksforgeeks.org",
    "tutorialspoint.com",
    "javatpoint.com",
    "programiz.com",
    "w3schools.com",
]

TIER_2 = [
    "educative.io",
    "freecodecamp.org",
    "medium.com",
    "stackexchange.com",
]


def _download_and_validate_image(url: str) -> Image.Image | None:
    try:
        r = _SESSION.get(url, timeout=25)
        if r.status_code != 200:
            return None

        content_type = r.headers.get("Content-Type", "").lower()
        if "html" in content_type:
            return None

        data = r.content
        if len(data) < 10_000:  # reject tiny thumbnails / broken images
            return None

        img = Image.open(BytesIO(data))

        # 🔑 THIS is the key — actually decode pixels
        img.load()
        
        w, h = img.size
        if w < 500 or h < 300:
            return None

        # Normalize format (fixes WEBP / progressive JPG issues)
        return img.convert("RGB")

    except Exception:
        return None


# -------------------------
# MAIN IMAGE FETCHER
# -------------------------

def fetch_image(query: str, index: int) -> str:
    search_url = (
        "https://www.bing.com/images/search?q="
        + quote(query + " diagram")
        + "&form=HDRSC2"
    )

    BAD_KEYWORDS = [
        "dreamstime", "shutterstock", "istock",
        "getty", "adobe", "pngtree", "stock"
    ]

    DIAGRAM_TERMS = [
        "diagram", "representation", "working",
        "push", "pop", "lifo", "top", "operation"
    ]

    BANNER_TERMS = [
        "course", "tutorial", "lecture", "interview",
        "illustration", "cartoon"
    ]

    for attempt in range(3):
        try:
            r = _SESSION.get(search_url, timeout=20)
            r.raise_for_status()

            soup = BeautifulSoup(r.text, "html.parser")

            tier1, tier2, tier3 = [], [], []

            for a in soup.select("a.iusc"):
                meta = a.get("m")
                if not meta:
                    continue

                try:
                    data = json.loads(meta)
                    img_url = data.get("murl")
                except Exception:
                    continue

                if not img_url or img_url in _USED_IMAGE_URLS:
                    continue

                img_l = img_url.lower()

                if not img_l.endswith((".png", ".jpg", ".jpeg", ".webp")):
                    continue

                # Reject obvious stock images early
                if any(bad in img_l for bad in BAD_KEYWORDS):
                    continue

                # -------------------------
                # SOFT SCORING
                # -------------------------
                score = 0

                is_tier1 = any(d in img_l for d in TIER_1)
                is_tier2 = any(d in img_l for d in TIER_2)

                if is_tier1:
                    score += 12
                elif is_tier2:
                    score += 7
                else:
                    score += 3

                for kw in query.lower().split():
                    if kw in img_l:
                        score += 3

                if img_l.endswith(".png"):
                    score += 2

                if any(t in img_l for t in DIAGRAM_TERMS):
                    score += 5

                if any(t in img_l for t in BANNER_TERMS):
                    score -= 4

                try:
                    domain = img_l.split("/")[2]
                except Exception:
                    domain = ""

                if domain in _USED_DOMAINS:
                    score -= 3

                entry = (score, img_url, domain)

                if is_tier1:
                    tier1.append(entry)
                elif is_tier2:
                    tier2.append(entry)
                else:
                    tier3.append(entry)

            # -------------------------
            # TRY TIERS IN ORDER
            # -------------------------
            for tier_name, candidates in [
                ("TIER-1", tier1),
                ("TIER-2", tier2),
                ("TIER-3", tier3),
            ]:
                if not candidates:
                    continue

                print(f"🔍 Trying {tier_name} images ({len(candidates)})")

                candidates.sort(reverse=True, key=lambda x: x[0])

                for score, img_url, domain in candidates:
                    img = _download_and_validate_image(img_url)
                    _USED_IMAGE_URLS.add(img_url)

                    if img is None:
                        continue

                    # -------------------------
                    # DIAGRAM HEURISTICS (SAFE)
                    # -------------------------
                    w, h = img.size
                    if w < 500 or h < 300:
                        continue  # icon / UI junk

                    # Prefer light backgrounds (diagrams)
                    gray = img.resize((40, 40)).convert("L")
                    avg = sum(gray.getdata()) / (40 * 40)
                    if avg < 140:
                        score -= 4  # dark illustration penalty

                    _USED_DOMAINS.add(domain)

                    out_path = IMG_DIR / f"slide_{index}.jpg"
                    img.save(out_path, format="JPEG", quality=95)

                    print(f"🖼️ Selected from {tier_name}: {out_path}")
                    return str(out_path)

            raise RuntimeError("No suitable images in any tier")

        except Exception:
            wait = 2 ** attempt
            print(f"⚠️ Image fetch failed (attempt {attempt+1}), retrying in {wait}s...")
            time.sleep(wait)

    return _create_placeholder(index, query)

# -------------------------
# PLACEHOLDER IMAGE
# -------------------------

def _create_placeholder(index: int, query: str) -> str:
    img = Image.new("RGB", (1280, 720), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    text = f"No image found\n{query}"
    draw.multiline_text((100, 300), text, fill=(220, 220, 220))

    out = IMG_DIR / f"slide_{index}.jpg"
    img.save(out)

    print(f"🧱 Placeholder used: {out}")
    return str(out)
