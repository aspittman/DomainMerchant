from niches.loans.config import (
    CORE_LOAN_TERMS,
    HIGH_VALUE_LOAN_TYPES,
    BUYER_INTENT_WORDS,
    TRUST_WORDS,
    LOCATIONS,
)


def generate_domains(limit=None):
    domains = []

    loan_terms = list(CORE_LOAN_TERMS.keys())
    loan_types = list(HIGH_VALUE_LOAN_TYPES.keys())
    intent_words = list(BUYER_INTENT_WORDS.keys())
    trust_words = list(TRUST_WORDS.keys())

    # Strong exact-intent names:
    # smallbusinessloanquotes.com
    # commercialloanbroker.com
    for loan_type in loan_types:
        for loan_term in loan_terms:
            domains.append(f"{loan_type}{loan_term}.com")

            for intent in intent_words:
                domains.append(f"{loan_type}{loan_term}{intent}.com")
                domains.append(f"{loan_type}{intent}{loan_term}.com")

    # Legit finance-company style:
    # businessfundinggroup.com
    # equipmentcapitalpartners.com
    for loan_type in loan_types:
        for trust in trust_words:
            domains.append(f"{loan_type}{trust}.com")
            domains.append(f"{loan_type}{trust}group.com")
            domains.append(f"{loan_type}{trust}partners.com")
            domains.append(f"{loan_type}{trust}experts.com")

    # Local buyer-intent names:
    # utahbusinessloans.com
    # phoenixcommercialfunding.com
    for location in LOCATIONS:
        domains.append(f"{location}businessloans.com")
        domains.append(f"{location}smallbusinessloans.com")
        domains.append(f"{location}commercialloans.com")
        domains.append(f"{location}businessfunding.com")
        domains.append(f"{location}commercialfunding.com")
        domains.append(f"{location}loanbroker.com")
        domains.append(f"{location}loanbrokers.com")
        domains.append(f"{location}loanquotes.com")
        domains.append(f"{location}fundingexperts.com")

    # A few national high-intent names
    domains.extend([
        "businessloanquotes.com",
        "smallbusinessloanquotes.com",
        "commercialloanquotes.com",
        "equipmentfinancingquotes.com",
        "businessfundingexperts.com",
        "commercialfundingexperts.com",
        "workingcapitalquotes.com",
        "startupfundingexperts.com",
        "bridgefundingexperts.com",
        "equipmentfundingexperts.com",
    ])

    seen = set()
    clean = []

    for domain in domains:
        domain = domain.lower().replace(" ", "").replace("-", "")
        if domain not in seen:
            seen.add(domain)
            clean.append(domain)

    return clean[:limit] if limit else clean