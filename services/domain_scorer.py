VOWELS = "aeiou"

COMMERCIAL_KEYWORDS = [
    "ai", "tech", "health", "legal", "pay", "data",
    "media", "home", "glass", "dent", "clinic", "solar",
    "finance", "loan", "plumbing", "roof", "hvac", "law",
    "medical", "marketing", "agency", "studio", "labs",
    "tools", "app", "cloud", "crm", "repair", "cleaning",
    "software", "solutions"
]

WEAK_PATTERNS = [
    "xyz", "123", "app", "online", "site", "test", "demo", "abc"
]

LOW_TRUST_TOKENS = [
    "bet", "vip", "slot", "casino", "888", "777"
]

RARE_LETTERS = set("qxzjv")

BUSINESS_WORDS = [
    "domain", "domains", "web", "media", "digital", "marketing",
    "sales", "partner", "studio", "labs", "cleaning", "logistics",
    "design", "health", "legal", "clinic", "agency", "solutions",
    "tools", "software", "cloud", "finance", "repair", "plumbing"
]

LOW_TRUST_PATTERNS = [
    "apk", "mod", "crypto", "eth", "raid", "bet", "vip"
]

def decide_action(result):
    availability = result.get("availability", {})
    available = availability.get("available")

    final_score = result["score"]
    brand_score = result["brand_score"]

    if available is False:
        return "TAKEN"

    if available is True:
        if final_score >= 80 and brand_score >= 45:
            return "BUY_CANDIDATE"
        elif final_score >= 40 and brand_score >= 15:
            return "REVIEW"
        else:
            return "SKIP"

    return "UNKNOWN"

def low_trust_pattern_count(name: str) -> int:
    return sum(1 for pattern in LOW_TRUST_PATTERNS if pattern in name)


def looks_typo_like(name: str) -> bool:
    suspicious_chunks = [
        "firmyk", "analitiks", "recaptio", "destinatoins",
        "bestmod", "modapk", "coursenow", "gto", "cs2"
    ]
    return any(chunk in name for chunk in suspicious_chunks)

def base_name(domain: str) -> str:
    return domain.split(".")[0].lower()


def has_numbers(name: str) -> bool:
    return any(c.isdigit() for c in name)


def has_hyphen(name: str) -> bool:
    return "-" in name


def vowel_ratio(name: str) -> float:
    letters = [c for c in name if c.isalpha()]
    if not letters:
        return 0.0
    vowel_count = sum(1 for c in letters if c in VOWELS)
    return vowel_count / len(letters)


def count_keyword_hits(name: str) -> int:
    return sum(1 for word in COMMERCIAL_KEYWORDS if word in name)


def has_commercial_keyword(name: str) -> bool:
    return count_keyword_hits(name) > 0


def business_word_count(name: str) -> int:
    return sum(1 for word in BUSINESS_WORDS if word in name)


def low_trust_token_count(name: str) -> int:
    return sum(1 for token in LOW_TRUST_TOKENS if token in name)


def rare_letter_count(name: str) -> int:
    return sum(1 for c in name if c in RARE_LETTERS)


def looks_like_gibberish(name: str) -> bool:
    if len(name) <= 6:
        rare_count = rare_letter_count(name)
        vr = vowel_ratio(name)

        if rare_count >= 3:
            return True

        if vr < 0.25:
            return True

    return False


def looks_like_personal_name(name: str) -> bool:
    if has_commercial_keyword(name):
        return False

    if has_numbers(name) or has_hyphen(name):
        return False

    if 8 <= len(name) <= 14 and name.isalpha():
        return True

    return False


def has_repetitive_chunks(name: str) -> bool:
    for i in range(len(name) - 2):
        chunk = name[i:i + 2]
        if name.count(chunk) >= 3:
            return True
    return False


def awkward_consonant_clusters(name: str) -> int:
    clusters = 0
    current = 0

    for c in name:
        if c.isalpha() and c not in VOWELS:
            current += 1
            if current >= 4:
                clusters += 1
        else:
            current = 0

    return clusters


def length_score(name: str) -> int:
    length = len(name)

    if length <= 6:
        return 25
    elif length <= 8:
        return 20
    elif length <= 10:
        return 10
    elif length <= 12:
        return 0
    elif length <= 15:
        return -10
    else:
        return -25

def awkward_keyword_mashup_penalty(name: str) -> int:
    suspicious_fragments = [
        "lawsfirm", "firmyk", "analitik", "recaptio",
        "destinatoi", "bestmod", "coursenow"
    ]

    if any(fragment in name for fragment in suspicious_fragments):
        return -25

    return 0

def commercial_intent_score(name: str) -> int:
    hits = count_keyword_hits(name)

    if hits == 1:
        return 20
    elif hits >= 2:
        return 30
    return 0


def looks_like_real_business(name: str) -> bool:
    if any(pattern in name for pattern in ["123", "xyz", "abc", "test", "demo"]):
        return False

    if len(name) < 4:
        return False

    return True


def business_usability_score(name: str) -> int:
    return 10 if looks_like_real_business(name) else -20


def unclear_phrase_penalty(name: str) -> int:
    if len(name) > 12 and not has_commercial_keyword(name):
        return -15
    return 0


def consonant_cluster_penalty(name: str) -> int:
    max_cluster = 0
    current = 0

    for c in name:
        if c.isalpha() and c not in VOWELS:
            current += 1
            max_cluster = max(max_cluster, current)
        else:
            current = 0

    if max_cluster >= 5:
        return -30
    elif max_cluster >= 4:
        return -15

    return 0


def score_brand(domain: str) -> int:
    score = 0
    name = base_name(domain)

    # Length
    score += length_score(name)

    # Clean formatting
    if not has_hyphen(name):
        score += 10
    else:
        score -= 20

    if not has_numbers(name):
        score += 10
    else:
        score -= 20

    if not has_numbers(name):
        score += 10
    else:
        score -= 35

    score -= low_trust_pattern_count(name) * 12

    if looks_typo_like(name):
        score -= 20

    if looks_like_personal_name(name):
        score -= 45

    score += awkward_keyword_mashup_penalty(name)
    
    # Commercial usefulness
    score += commercial_intent_score(name)

    # Business-word bonus
    business_hits = business_word_count(name)
    if business_hits == 1:
        score += 8
    elif business_hits >= 2:
        score += 14

    # Business usability
    score += business_usability_score(name)

    # Low-trust token penalty
    low_trust_hits = low_trust_token_count(name)
    score -= low_trust_hits * 15

    # Phrase clarity penalty
    score += unclear_phrase_penalty(name)

    # Pronounceability approximation
    vr = vowel_ratio(name)
    if 0.30 <= vr <= 0.62:
        score += 12
    else:
        score -= 10

    # Extra penalty for very short but hard-to-pronounce names
    if len(name) <= 6 and vr < 0.25:
        score -= 15

    # Penalize short gibberish-like strings
    if looks_like_gibberish(name):
        score -= 25

    # Penalize names with almost no vowel support
    if vr < 0.20:
        score -= 10

    # Penalize likely personal-name domains
    if looks_like_personal_name(name):
        score -= 45

    # Repetition penalty
    if has_repetitive_chunks(name):
        score -= 10

    # Consonant cluster penalty
    score += consonant_cluster_penalty(name)

    # Awkward cluster penalty
    clusters = awkward_consonant_clusters(name)
    score -= clusters * 8

    # Weak/generic suffix pattern penalty
    for pattern in WEAK_PATTERNS:
        if pattern in name and len(name) > 8:
            score -= 6

    return score


def score_seo(metrics: dict) -> int:
    score = 0

    da = metrics.get("domain_authority", 0)
    ref_domains = metrics.get("referring_domains", 0)
    backlinks = metrics.get("backlinks", 0)
    spam = metrics.get("spam_score", 100)

    # Domain authority
    if da >= 40:
        score += 30
    elif da >= 30:
        score += 24
    elif da >= 20:
        score += 16
    elif da >= 15:
        score += 10
    elif da >= 10:
        score += 4

    # Referring domains
    if ref_domains >= 100:
        score += 35
    elif ref_domains >= 50:
        score += 28
    elif ref_domains >= 25:
        score += 20
    elif ref_domains >= 10:
        score += 12
    elif ref_domains >= 5:
        score += 5

    # Backlinks matter, but less than referring domains
    if backlinks >= 1000:
        score += 12
    elif backlinks >= 250:
        score += 8
    elif backlinks >= 100:
        score += 5
    elif backlinks >= 25:
        score += 2

    # Spam penalties
    if spam <= 2:
        score += 10
    elif spam <= 5:
        score += 5
    elif spam <= 10:
        score -= 10
    else:
        score -= 30

    return score


def score_domain(domain: str, metrics: dict) -> dict:
    brand_score = score_brand(domain)
    seo_score = score_seo(metrics)
    final_score = brand_score + seo_score

    return {
        "brand_score": brand_score,
        "seo_score": seo_score,
        "final_score": final_score
    }