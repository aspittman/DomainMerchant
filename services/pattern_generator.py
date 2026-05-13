# services/pattern_generator.py

LOCAL_SERVICE_NICHES = {
    "plumbing": ["plumbingpros", "plumbers", "plumbingquotes", "plumbingrepair"],
    "roofing": ["roofingpros", "roofers", "roofingquotes", "roofrepair"],
    "hvac": ["hvacpros", "hvacrepair", "hvacservice", "heatingcooling"],
    "cleaning": ["cleaningpros", "cleaningservices", "cleaners"],
    "pest": ["pestcontrol", "pestpros", "exterminators"],
    "dental": ["dentist", "dentalcare", "dentalpros"],
}

FINANCE_NICHES = {
    "mortgage": ["mortgagerates", "mortgageexperts", "mortgagequotes", "mortgagebroker"],
    "loan": ["loanexperts", "loanquotes", "loanbroker", "loanhelp"],
    "insurance": ["insurancerates", "insurancequotes", "insuranceexperts"],
    "tax": ["taxhelp", "taxexperts", "taxpros"],
}

STATE_TERMS = [
    "utah", "arizona", "colorado", "nevada", "texas", "florida",
    "california", "oregon", "washington", "idaho", "montana",
    "georgia", "tennessee", "carolina", "ohio", "michigan",
]

CITY_TERMS = [
    "phoenix", "denver", "vegas", "saltlake", "provo", "orem",
    "boise", "austin", "dallas", "houston", "orlando", "tampa",
    "miami", "atlanta", "nashville", "charlotte", "columbus",
    "detroit", "portland", "seattle", "spokane", "reno", "tucson",
    "mesa", "scottsdale", "gilbert", "tempe", "aurora", "boulder",
]

NATIONAL_PREFIXES = ["top", "best", "fast", "local"]
NATIONAL_SUFFIXES = {
    "plumbing": ["quotes", "pros", "services", "repair"],
    "roofing": ["quotes", "pros", "repair", "contractors"],
    "hvac": ["pros", "repair", "service", "experts"],
    "mortgage": ["rates", "quotes", "experts", "broker"],
    "loan": ["quotes", "experts", "broker", "help"],
    "insurance": ["rates", "quotes", "experts"],
    "tax": ["help", "experts", "pros"],
}


def generate_local_domains():
    domains = []

    locations = STATE_TERMS + CITY_TERMS

    for location in locations:
        for niche, patterns in LOCAL_SERVICE_NICHES.items():
            for pattern in patterns:
                domains.append(f"{location}{pattern}.com")

    return domains


def generate_national_domains():
    domains = []

    all_niches = list(NATIONAL_SUFFIXES.keys())

    for niche in all_niches:
        suffixes = NATIONAL_SUFFIXES[niche]

        for suffix in suffixes:
            domains.append(f"{niche}{suffix}.com")

        for prefix in NATIONAL_PREFIXES:
            for suffix in suffixes:
                domains.append(f"{prefix}{niche}{suffix}.com")

    return domains


def generate_finance_domains():
    domains = []

    for prefix in NATIONAL_PREFIXES:
        for niche, patterns in FINANCE_NICHES.items():
            for pattern in patterns:
                domains.append(f"{prefix}{pattern}.com")

    for niche, patterns in FINANCE_NICHES.items():
        for pattern in patterns:
            domains.append(f"local{pattern}.com")
            domains.append(f"fast{pattern}.com")

    return domains


def generate_domains(limit=None):
    domains = []

    domains.extend(generate_local_domains())
    domains.extend(generate_national_domains())
    domains.extend(generate_finance_domains())

    # Deduplicate while preserving order
    seen = set()
    clean = []
    for domain in domains:
        if domain not in seen:
            seen.add(domain)
            clean.append(domain)

    if limit:
        return clean[:limit]

    return clean