import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

URLS = [
    "https://marketplace.nvidia.com/pl-pl/consumer/graphics-cards/nvidia-geforce-rtx-5090/",
    # add more URLs here:
    # "https://marketplace.nvidia.com/pl-pl/consumer/graphics-cards/geforce-rtx-5070-twin-x2-oc-12gb-gddr7-dlss4/",
]

OUT_OF_STOCK_PHRASES = [
    "towar wyprzedany",
    "wyprzedane",
    "brak w magazynie",
    "niedostępny",
    "sold out",
    "out of stock",
]

IN_STOCK_PHRASES = [
    "kup teraz",
    "dodaj do koszyka",
    "add to cart",
    "buy now",
]

STATE_PATH = Path(os.environ.get("STATE_PATH", ".state/state.json"))

def fetch_visible_text_firefox(url: str) -> str:
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        text = page.inner_text("body")
        browser.close()
    return text.lower()

def classify(text_lower: str):
    if any(x in text_lower for x in OUT_OF_STOCK_PHRASES):
        return False, "out_of_stock_phrase"
    if any(x in text_lower for x in IN_STOCK_PHRASES):
        return True, "in_stock_phrase"
    return None, "unknown_state"

def load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    prev = load_state()  # {url: true/false/None}

    results = []
    became_in_stock = []  # URLs that changed from not-true -> true

    for url in URLS:
        text = fetch_visible_text_firefox(url)
        available, reason = classify(text)

        results.append({"url": url, "available": available, "reason": reason})

        old = prev.get(url)
        if available is True and old is not True:
            became_in_stock.append(url)

        prev[url] = available

    save_state(prev)

    # Print results for logs
    print(json.dumps({"results": results, "became_in_stock": became_in_stock}, ensure_ascii=False, indent=2))

    # Write a small flag file for the workflow step to read
    flag_path = Path(os.environ.get("FLAG_PATH", ".state/in_stock_urls.txt"))
    flag_path.parent.mkdir(parents=True, exist_ok=True)
    flag_path.write_text("\n".join(became_in_stock) + ("\n" if became_in_stock else ""), encoding="utf-8")

if __name__ == "__main__":
    main()