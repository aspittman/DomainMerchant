from services.domain_scorer import base_name


HIGH_VALUE_KEYWORDS = [
    "tech", "ai", "health", "legal", "finance", "loan",
    "plumbing", "roof", "hvac", "solar", "clinic",
    "dent", "law", "medical", "marketing", "agency"
]

LOW_QUALITY_PATTERNS = [
    "123", "xyz", "test", "demo", "temp", "app", "site"
]


def get_mock_seo_metrics(domain: str) -> dict:
    """
    Simulates SEO metrics in a more realistic way than fixed values.
    This is still fake data, but it's useful for testing scoring logic.
    """
    name = base_name(domain)

    domain_authority = 5
    referring_domains = 0
    backlinks = 0
    spam_score = 4

    # Slight reward for cleaner, shorter domains
    if len(name) <= 8:
        domain_authority += 8
        referring_domains += 6
        backlinks += 30
    elif len(name) <= 12:
        domain_authority += 5
        referring_domains += 4
        backlinks += 20
    elif len(name) <= 16:
        domain_authority += 2
        referring_domains += 2
        backlinks += 10
    else:
        spam_score += 1

    # Commercial keywords often correlate with domains that might
    # have had some real-world use or link history
    keyword_hits = sum(1 for word in HIGH_VALUE_KEYWORDS if word in name)
    if keyword_hits == 1:
        domain_authority += 5
        referring_domains += 8
        backlinks += 60
    elif keyword_hits >= 2:
        domain_authority += 10
        referring_domains += 15
        backlinks += 120

    # Penalties for junky patterns
    if "-" in name:
        spam_score += 2
        domain_authority -= 2

    if any(char.isdigit() for char in name):
        spam_score += 2
        referring_domains -= 1

    for pattern in LOW_QUALITY_PATTERNS:
        if pattern in name:
            spam_score += 2
            domain_authority -= 3
            referring_domains -= 2
            backlinks -= 10

    # Personal-name-like domains usually have weak resale SEO value
    # unless tied to a known brand/person, so lower their profile
    if len(name) > 10 and name.isalpha() and keyword_hits == 0:
        domain_authority -= 3
        referring_domains -= 2

    # Keep values in sane ranges
    domain_authority = max(0, domain_authority)
    referring_domains = max(0, referring_domains)
    backlinks = max(0, backlinks)
    spam_score = max(0, min(spam_score, 20))

    return {
        "domain_authority": domain_authority,
        "referring_domains": referring_domains,
        "backlinks": backlinks,
        "spam_score": spam_score
    }


def passes_seo_filter(metrics: dict) -> bool:
    da = metrics.get("domain_authority", 0)
    ref_domains = metrics.get("referring_domains", 0)
    spam = metrics.get("spam_score", 100)

    return da >= 12 and ref_domains >= 6 and spam <= 6