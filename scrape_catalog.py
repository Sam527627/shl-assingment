"""
Scrape Individual Test Solutions from SHL product catalog.
We hit the paginated catalog with type=1 (Individual Test Solutions only).
"""
import requests
import json
import time
from bs4 import BeautifulSoup

BASE = "https://www.shl.com"
CATALOG_URL = f"{BASE}/products/product-catalog/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

def fetch_page(start=0):
    params = {
        "start": start,
        "type": "1",   # Individual Test Solutions
        "f": "1",
    }
    r = requests.get(CATALOG_URL, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def parse_products(html):
    soup = BeautifulSoup(html, "html.parser")
    products = []
    
    # SHL catalog uses a table with class "custom-table" or rows with product data
    rows = soup.select("tr.js-row") or soup.select("table tbody tr")
    
    for row in rows:
        # Product name in <td> with an anchor
        name_cell = row.select_one("td.custom-table__title a, td a[href*='product-catalog']")
        if not name_cell:
            continue
        
        name = name_cell.get_text(strip=True)
        url = name_cell.get("href", "")
        if url and not url.startswith("http"):
            url = BASE + url
        
        # Test type codes (A=Ability, B=Biodata, C=Competency, D=Development,
        # E=Assessment Exercises, K=Knowledge & Skills, M=Multimedia,
        # P=Personality & Preference, S=Simulations)
        type_cells = row.select("td span.catalogue__circle, td.custom-table__type span")
        test_types = [c.get_text(strip=True) for c in type_cells if c.get_text(strip=True)]
        
        # Remote / supervised flags
        remote = bool(row.select_one("td:nth-child(3) .catalogue__check, td[data-label='Remote Testing'] .icon--check"))
        adaptive = bool(row.select_one("td:nth-child(4) .catalogue__check, td[data-label='Adaptive/IRT'] .icon--check"))
        
        if name and url:
            products.append({
                "name": name,
                "url": url,
                "test_types": test_types,
                "remote_testing": remote,
                "adaptive": adaptive,
            })
    
    return products


def scrape_all():
    all_products = []
    start = 0
    step = 12  # SHL shows 12 per page
    
    while True:
        print(f"  Fetching start={start}...")
        html = fetch_page(start)
        products = parse_products(html)
        
        if not products:
            break
        
        all_products.extend(products)
        print(f"  Got {len(products)} products (total so far: {len(all_products)})")
        
        # Check if there's a next page
        soup = BeautifulSoup(html, "html.parser")
        next_btn = soup.select_one("a[rel='next'], .pagination__next:not(.disabled), a.next")
        if not next_btn:
            # Also check if fewer results than page size → last page
            if len(products) < step:
                break
            # Try next page anyway
        
        start += step
        time.sleep(0.5)
        
        if start > 500:  # safety cap
            break
    
    return all_products


if __name__ == "__main__":
    print("Scraping SHL catalog (Individual Test Solutions)...")
    products = scrape_all()
    
    # Deduplicate by URL
    seen = set()
    unique = []
    for p in products:
        if p["url"] not in seen:
            seen.add(p["url"])
            unique.append(p)
    
    print(f"\nTotal unique products: {len(unique)}")
    
    with open("catalog.json", "w") as f:
        json.dump(unique, f, indent=2)
    
    print("Saved to catalog.json")
    for p in unique[:5]:
        print(f"  - {p['name']} | {p['url']} | types={p['test_types']}")
