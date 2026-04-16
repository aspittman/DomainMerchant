import re
import requests
from bs4 import BeautifulSoup


DOMAIN_PATTERN = re.compile(r"\b[a-zA-Z0-9-]+\.(?:com|net|org|io|co)\b")


def clean_domain_text(text):
    match = DOMAIN_PATTERN.search(text)
    if match:
        return match.group(0).lower()
    return None


def _fetch_domains_from_page(url: str, limit: int = 25):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table tbody tr")

    domains = []
    seen = set()

    for row in rows:
        row_text = row.get_text(" ", strip=True)
        domain = clean_domain_text(row_text)

        if domain and domain not in seen:
            seen.add(domain)
            domains.append(domain)

        if len(domains) >= limit:
            break

    return domains, response


def get_deleted_domains(limit: int = 25):
    url = "https://www.expireddomains.net/deleted-com-domains/"
    domains, response = _fetch_domains_from_page(url, limit=limit)

    print(f"[deleted] HTTP status: {response.status_code}")
    print(f"[deleted] Page length: {len(response.text)}")
    print(f"[deleted] Domains found: {len(domains)}")

    return [{"domain": d, "source": "deleted_com"} for d in domains]


def get_godaddy_closeout_domains(limit: int = 25):
    url = "https://www.expireddomains.net/godaddy-closeout-domains/"
    domains, response = _fetch_domains_from_page(url, limit=limit)

    print(f"[closeout] HTTP status: {response.status_code}")
    print(f"[closeout] Page length: {len(response.text)}")
    print(f"[closeout] Domains found: {len(domains)}")

    return [{"domain": d, "source": "godaddy_closeout"} for d in domains]


def dedupe_candidates(candidates):
    seen = set()
    deduped = []

    for item in candidates:
        domain = item["domain"]
        if domain not in seen:
            seen.add(domain)
            deduped.append(item)

    return deduped


def get_all_candidate_domains():
    candidates = []
    candidates.extend(get_deleted_domains(limit=25))
    candidates.extend(get_godaddy_closeout_domains(limit=25))
    return dedupe_candidates(candidates)