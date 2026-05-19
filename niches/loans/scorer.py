from services.domain_scorer import (
    base_name,
    tld,
    has_trademark_risk,
    has_hyphen,
    has_numbers,
    looks_like_gibberish,
    looks_typo_like,
    low_trust_token_count,
)

from niches.loans.config import (
    CORE_LOAN_TERMS,
    HIGH_VALUE_LOAN_TYPES,
    BUYER_INTENT_WORDS,
    TRUST_WORDS,
    WEAK_OR_SPAMMY_WORDS,
    LOCATIONS,
)


def find_hits(name, terms):
    return [term for term in terms if term in name]


def score_domain(domain: str, metrics: dict = None) -> dict:
    name = base_name(domain)

    loan_hits = find_hits(name, CORE_LOAN_TERMS)
    type_hits = find_hits(name, HIGH_VALUE_LOAN_TYPES)
    intent_hits = find_hits(name, BUYER_INTENT_WORDS)
    trust_hits = find_hits(name, TRUST_WORDS)
    location_hits = find_hits(name, LOCATIONS)
    spam_hits = find_hits(name, WEAK_OR_SPAMMY_WORDS)

    score = 0

    if has_trademark_risk(name):
        return {
            "domain": domain,
            "brand_score": -150,
            "seo_score": 0,
            "final_score": -150,
            "score": -150,
            "resale_likelihood_score": 0,
            "trademark_risk": True,
            "obvious_buyer": False,
            "buyer_terms": [],
            "action_terms": [],
            "category": "TRADEMARK_RISK",
        }

    # Hard requirement: it must clearly be a loan/funding/finance name
    if not loan_hits and not trust_hits:
        score -= 120

    for term in loan_hits:
        score += CORE_LOAN_TERMS[term]

    for term in type_hits:
        score += HIGH_VALUE_LOAN_TYPES[term]

    for term in intent_hits:
        score += BUYER_INTENT_WORDS[term]

    for term in trust_hits:
        score += TRUST_WORDS[term]

    if location_hits:
        score += 25

    # Best combos
    if type_hits and loan_hits and intent_hits:
        score += 45

    if type_hits and trust_hits:
        score += 35

    if location_hits and type_hits:
        score += 30

    if location_hits and loan_hits:
        score += 25

    if "smallbusiness" in type_hits:
        score += 20

    if "commercial" in type_hits:
        score += 18

    if "equipment" in type_hits:
        score += 15

    # Penalties
    if spam_hits:
        score -= 80

    if len(name) > 28:
        score -= 45
    elif len(name) > 24:
        score -= 30
    elif len(name) > 20:
        score -= 12
    elif 12 <= len(name) <= 20:
        score += 10

    if has_hyphen(name):
        score -= 30

    if has_numbers(name):
        score -= 35

    if looks_like_gibberish(name) or looks_typo_like(name):
        score -= 50

    if low_trust_token_count(name) > 0:
        score -= 60

    if tld(domain) != "com":
        score -= 35

    obvious_buyer = bool(
        loan_hits
        and (
            type_hits
            or intent_hits
            or location_hits
            or trust_hits
        )
    )

    if not obvious_buyer:
        score = min(score, 55)

    resale_score = max(0, min(100, int(score * 0.65)))

    if score >= 115:
        category = "HIGH_INTENT_LOAN_DOMAIN"
    elif score >= 85:
        category = "REVIEWABLE_LOAN_DOMAIN"
    else:
        category = "WEAK_OR_GENERIC_LOAN_DOMAIN"

    return {
        "domain": domain,
        "brand_score": score,
        "seo_score": 0,
        "final_score": score,
        "score": score,
        "resale_likelihood_score": resale_score,
        "trademark_risk": False,
        "obvious_buyer": obvious_buyer,
        "buyer_terms": loan_hits + type_hits + trust_hits + location_hits,
        "action_terms": intent_hits,
        "category": category,
        "low_price": 49,
        "target_price": 299 if score < 115 else 599,
        "stretch_price": 799 if score < 115 else 1299,
    }