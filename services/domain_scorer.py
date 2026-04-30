VOWELS = "aeiou"

MONEY_NICHES = {
    "mortgage": 60,
    "loan": 55,
    "insurance": 55,
    "law": 50,
    "legal": 50,
    "attorney": 50,
    "lawyer": 50,
    "plumbing": 48,
    "roofer": 48,
    "roofing": 48,
    "roof": 45,
    "hvac": 45,
    "dental": 42,
    "dentist": 42,
    "clinic": 40,
    "therapy": 38,
    "therapist": 38,
    "hosting": 38,
    "tax": 38,
    "accounting": 38,
    "cleaning": 35,
    "repair": 35,
    "solar": 35,
    "pest": 34,
    "garage": 32,
    "painting": 32,
    "movers": 32,
    "nails": 28,
    "salon": 28,
    "beauty": 25,
}

BUYER_ACTION_WORDS = [
    "pros", "pro", "experts", "expert", "quotes", "quote",
    "help", "broker", "service", "services", "near", "local",
    "best", "top", "fast", "trusted", "affordable", "rates"
]

WEAK_STARTUP_WORDS = {
    "tech", "data", "nova", "labs", "cloud", "ai", "app", "studio"
}

LOW_TRUST_TOKENS = [
    "bet", "vip", "slot", "casino", "888", "777", "apk", "mod",
    "raid", "eth", "crypto", "nft", "hack", "cheat", "gamble",
    "roulette", "kratom", "covid"
]

TRADEMARK_RISK_TERMS = [
    "google", "youtube", "facebook", "instagram", "whatsapp", "meta",
    "apple", "iphone", "ipad", "macbook", "microsoft", "windows",
    "openai", "chatgpt", "tesla", "amazon", "aws", "netflix",
    "spotify", "tiktok", "adobe", "vmware", "paypal", "stripe",
    "shopify", "uber", "lyft", "airbnb", "canva", "semrush",
    "ahrefs", "nvidia", "samsung", "xbox", "playstation"
]

WEAK_PATTERNS = [
    "xyz", "123", "online", "site", "test", "demo", "abc"
]

RARE_LETTERS = set("qxzjv")


def base_name(domain: str) -> str:
    return domain.split(".")[0].lower().strip()


def tld(domain: str) -> str:
    parts = domain.lower().strip().split(".")
    return parts[-1] if len(parts) > 1 else ""


def has_numbers(name: str) -> bool:
    return any(c.isdigit() for c in name)


def has_hyphen(name: str) -> bool:
    return "-" in name


def vowel_ratio(name: str) -> float:
    letters = [c for c in name if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c in VOWELS) / len(letters)


def rare_letter_count(name: str) -> int:
    return sum(1 for c in name if c in RARE_LETTERS)


def has_trademark_risk(name: str) -> bool:
    return any(term in name for term in TRADEMARK_RISK_TERMS)


def low_trust_token_count(name: str) -> int:
    return sum(1 for token in LOW_TRUST_TOKENS if token in name)


def money_niche_hits(name: str) -> list[str]:
    return [term for term in MONEY_NICHES if term in name]


def action_word_hits(name: str) -> list[str]:
    return [term for term in BUYER_ACTION_WORDS if term in name]


def weak_startup_hits(name: str) -> list[str]:
    return [term for term in WEAK_STARTUP_WORDS if term in name]


def has_obvious_outreach_angle(name: str) -> bool:
    return len(money_niche_hits(name)) > 0


def looks_like_gibberish(name: str) -> bool:
    vr = vowel_ratio(name)
    rare_count = rare_letter_count(name)

    if len(name) <= 6 and vr < 0.28:
        return True

    if len(name) <= 8 and rare_count >= 3:
        return True

    if len(name) <= 8 and rare_count >= 2 and vr < 0.34:
        return True

    return False


def looks_like_personal_name(name: str) -> bool:
    if has_obvious_outreach_angle(name):
        return False

    if has_numbers(name) or has_hyphen(name):
        return False

    return 8 <= len(name) <= 15 and name.isalpha()


def has_repetitive_chunks(name: str) -> bool:
    for i in range(len(name) - 2):
        chunk = name[i:i + 2]
        if name.count(chunk) >= 3:
            return True
    return False


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
        return -35
    if max_cluster >= 4:
        return -18
    return 0


def looks_typo_like(name: str) -> bool:
    suspicious_chunks = [
        "firmyk", "analitiks", "recaptio", "destinatoins",
        "bestmod", "modapk", "coursenow", "shooop",
        "kechains", "destinatoi", "malorca"
    ]
    return any(chunk in name for chunk in suspicious_chunks)


def length_score(name: str) -> int:
    length = len(name)

    if length <= 6:
        return 4
    if length <= 10:
        return 10
    if length <= 14:
        return 8
    if length <= 18:
        return -5
    if length <= 22:
        return -18
    return -35


def money_niche_score(name: str) -> int:
    hits = money_niche_hits(name)
    if not hits:
        return 0

    best = max(MONEY_NICHES[h] for h in hits)
    extra = min(12, (len(hits) - 1) * 6)
    return best + extra


def buyer_pattern_score(name: str) -> int:
    score = 0
    niche_hits = money_niche_hits(name)
    action_hits = action_word_hits(name)

    if niche_hits:
        score += 20

    if niche_hits and action_hits:
        score += 25

    if "near" in name and niche_hits:
        score += 12

    if any(w in name for w in ["best", "top", "trusted"]) and niche_hits:
        score += 10

    if any(w in name for w in ["broker", "quotes", "rates"]) and any(n in name for n in ["loan", "mortgage", "insurance", "hosting"]):
        score += 16

    return score


def startup_brandable_penalty(name: str) -> int:
    hits = weak_startup_hits(name)

    if not hits:
        return 0

    # Vague startup words should not become buy candidates by themselves.
    if not has_obvious_outreach_angle(name):
        return -35 if len(hits) >= 2 else -22

    return -8


def formatting_score(name: str) -> int:
    score = 0

    if has_hyphen(name):
        # Hyphens are usually bad, but tolerable for exact money niches.
        score -= 16 if has_obvious_outreach_angle(name) else 28
    else:
        score += 6

    if has_numbers(name):
        score -= 30
    else:
        score += 6

    return score


def trust_penalty(name: str) -> int:
    penalty = 0
    penalty -= low_trust_token_count(name) * 25

    for pattern in WEAK_PATTERNS:
        if pattern in name and len(name) > 8:
            penalty -= 10

    if looks_typo_like(name):
        penalty -= 35

    if looks_like_gibberish(name):
        penalty -= 45

    if looks_like_personal_name(name):
        penalty -= 25

    if has_repetitive_chunks(name):
        penalty -= 12

    penalty += consonant_cluster_penalty(name)

    return penalty


def readability_score(name: str) -> int:
    vr = vowel_ratio(name)

    if 0.30 <= vr <= 0.62:
        score = 8
    else:
        score = -8

    if vr < 0.22:
        score -= 14

    if len(name) > 18:
        score -= 8

    return score


def score_brand(domain: str) -> int:
    name = base_name(domain)

    if has_trademark_risk(name):
        return -150

    score = 0

    # Priority: buyer clarity and money niche.
    score += money_niche_score(name)
    score += buyer_pattern_score(name)

    # Normal domain quality.
    score += length_score(name)
    score += formatting_score(name)
    score += readability_score(name)

    # Penalize names that only sound tech/startup-ish without a buyer.
    score += startup_brandable_penalty(name)

    # Penalties.
    score += trust_penalty(name)

    # Hard cap for domains without obvious buyer.
    # They can be REVIEW, but should almost never become BUY_CANDIDATE.
    if not has_obvious_outreach_angle(name):
        score = min(score, 45)

    # Extra caution for non-.com domains unless very strong.
    if tld(domain) != "com":
        score -= 20

    return score


def score_seo(metrics: dict) -> int:
    score = 0

    da = metrics.get("domain_authority", 0)
    ref_domains = metrics.get("referring_domains", 0)
    backlinks = metrics.get("backlinks", 0)
    spam = metrics.get("spam_score", 100)

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

    if backlinks >= 1000:
        score += 12
    elif backlinks >= 250:
        score += 8
    elif backlinks >= 100:
        score += 5
    elif backlinks >= 25:
        score += 2

    if spam <= 2:
        score += 10
    elif spam <= 5:
        score += 5
    elif spam <= 10:
        score -= 10
    else:
        score -= 30

    # Since your SEO is mock/free for now, cap its influence.
    return max(-30, min(30, score))


def score_resale_likelihood(domain: str, brand_score: int, seo_score: int) -> int:
    name = base_name(domain)

    if has_trademark_risk(name):
        return 0

    score = 5

    if has_obvious_outreach_angle(name):
        score += 35
    else:
        score -= 15

    score += max(0, min(35, int(brand_score * 0.35)))
    score += max(0, min(8, int(seo_score * 0.10)))

    if action_word_hits(name) and money_niche_hits(name):
        score += 12

    if 8 <= len(name) <= 18:
        score += 8
    elif len(name) > 22:
        score -= 15

    if has_hyphen(name):
        score -= 8 if has_obvious_outreach_angle(name) else 18

    if has_numbers(name):
        score -= 20

    if looks_like_gibberish(name) or looks_typo_like(name):
        score -= 30

    if low_trust_token_count(name) > 0:
        score -= 35

    if tld(domain) != "com":
        score -= 20

    return max(0, min(100, score))


def estimate_domain_price(domain: str, resale_score: int, brand_score: int, seo_score: int) -> dict:
    name = base_name(domain)

    if has_trademark_risk(name) or low_trust_token_count(name) > 0:
        return {"low_price": 0, "target_price": 0, "stretch_price": 0}

    # Conservative beginner pricing.
    if resale_score >= 80:
        low = 199
        target = 599
        stretch = 1299
    elif resale_score >= 65:
        low = 99
        target = 349
        stretch = 799
    elif resale_score >= 50:
        low = 49
        target = 199
        stretch = 499
    elif resale_score >= 35:
        low = 0
        target = 99
        stretch = 249
    else:
        low = 0
        target = 49
        stretch = 149

    if money_niche_hits(name):
        target = int(target * 1.15)
        stretch = int(stretch * 1.20)

    if action_word_hits(name) and money_niche_hits(name):
        target = int(target * 1.15)
        stretch = int(stretch * 1.15)

    if has_hyphen(name):
        target = int(target * 0.75)
        stretch = int(stretch * 0.75)

    if looks_like_gibberish(name) or looks_typo_like(name) or looks_like_personal_name(name):
        low = int(low * 0.5)
        target = int(target * 0.5)
        stretch = int(stretch * 0.5)

    return {
        "low_price": max(0, low),
        "target_price": max(0, target),
        "stretch_price": max(0, stretch),
    }


def domain_category(domain: str) -> str:
    name = base_name(domain)

    if has_trademark_risk(name):
        return "TRADEMARK_RISK"

    if low_trust_token_count(name) > 0:
        return "LOW_TRUST"

    if money_niche_hits(name) and action_word_hits(name):
        return "MONEY_NICHE_WITH_BUYER_PATTERN"

    if money_niche_hits(name):
        return "MONEY_NICHE"

    if weak_startup_hits(name):
        return "WEAK_STARTUP_BRANDABLE"

    if looks_like_gibberish(name):
        return "GIBBERISH"

    return "GENERAL_REVIEW"


def score_domain(domain: str, metrics: dict) -> dict:
    name = base_name(domain)

    brand_score = score_brand(domain)
    seo_score = score_seo(metrics)
    final_score = brand_score + seo_score
    resale_likelihood = score_resale_likelihood(domain, brand_score, seo_score)
    pricing = estimate_domain_price(domain, resale_likelihood, brand_score, seo_score)

    obvious_buyer = has_obvious_outreach_angle(name)

    return {
        "brand_score": brand_score,
        "seo_score": seo_score,
        "final_score": final_score,
        "resale_likelihood_score": resale_likelihood,
        "low_price": pricing["low_price"],
        "target_price": pricing["target_price"],
        "stretch_price": pricing["stretch_price"],
        "trademark_risk": has_trademark_risk(name),
        "obvious_buyer": obvious_buyer,
        "category": domain_category(domain),
        "buyer_terms": money_niche_hits(name),
        "action_terms": action_word_hits(name),
    }