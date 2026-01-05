import json
from playwright.sync_api import sync_playwright

URLS = [
    "https://marketplace.nvidia.com/pl-pl/consumer/graphics-cards/nvidia-geforce-rtx-5090/",
    "https://marketplace.nvidia.com/pl-pl/consumer/graphics-cards/geforce-rtx-3050-ventus-2x-xs-oc-8gb-gddr6/"
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

def main():
    results = []
    in_stock_urls = []

    for url in URLS:
        text = fetch_visible_text_firefox(url)
        available, reason = classify(text)
        results.append({"url": url, "available": available, "reason": reason})
        if available is True:
            in_stock_urls.append(url)

    # Print JSON for logs
    print(json.dumps({"results": results, "in_stock_urls": in_stock_urls}, ensure_ascii=False))

    # Write a simple file the workflow can read
    with open("in_stock_urls.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(in_stock_urls) + ("\n" if in_stock_urls else ""))

if __name__ == "__main__":
    main()
