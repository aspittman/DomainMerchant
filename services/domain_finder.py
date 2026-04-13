import re
import requests
from bs4 import BeautifulSoup


DOMAIN_PATTERN = re.compile(r"\b[a-zA-Z0-9-]+\.(?:com|net|org|io|co)\b")


def clean_domain_text(text):
    match = DOMAIN_PATTERN.search(text)
    if match:
        return match.group(0).lower()
    return None


def get_expired_domains():
    url = "https://www.expireddomains.net/deleted-com-domains/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    print("HTTP status:", response.status_code)
    print("Page length:", len(response.text))

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table tbody tr")

    print("Rows found:", len(rows))

    domains = []
    seen = set()

    for row in rows:
        row_text = row.get_text(" ", strip=True)
        domain = clean_domain_text(row_text)

        if domain and domain not in seen:
            seen.add(domain)
            domains.append(domain)

        if len(domains) >= 25:
            break

    return domains