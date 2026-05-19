from data.db import init_db, upsert_domain_result
from services.availability_checker import check_domain_availability
from services.email_alerts import send_email_alert
from services.alert_history import already_alerted, mark_alerted

from niches.loans.config import MAX_ALERTS, BUY_THRESHOLD, REVIEW_THRESHOLD
from niches.loans.patterns import generate_domains
from niches.loans.scorer import score_domain


def decide_action(result):
    availability = result.get("availability", {})
    available = availability.get("available")

    score = result.get("score", 0)
    resale = result.get("resale_likelihood_score", 0)
    obvious_buyer = result.get("obvious_buyer", False)
    trademark_risk = result.get("trademark_risk", False)

    if available is False:
        return "TAKEN"

    if trademark_risk:
        return "SKIP"

    if available is True:
        if obvious_buyer and score >= BUY_THRESHOLD and resale >= 60:
            return "BUY_CANDIDATE"

        if obvious_buyer and score >= REVIEW_THRESHOLD:
            return "REVIEW"

        return "SKIP"

    return "UNKNOWN"


def print_result(result):
    availability = result.get("availability", {})
    available = availability.get("available")

    if available is True:
        status = "AVAILABLE"
    elif available is False:
        status = "TAKEN"
    else:
        status = "UNKNOWN"

    print(
        f"{result['domain']} | "
        f"Score: {result['score']} | "
        f"Resale: {result.get('resale_likelihood_score')} | "
        f"Category: {result.get('category')} | "
        f"Status: {status} | "
        f"Action: {result.get('action')}"
    )


def run():
    init_db()

    candidates = generate_domains()

    print(f"Found {len(candidates)} loan candidate domains\n")

    buy_candidates = []
    review_domains = []
    skipped_domains = []
    taken_domains = []
    unknown_domains = []

    for domain in candidates:
        result = score_domain(domain)
        result["source"] = "loans_niche"
        result["availability"] = check_domain_availability(domain)

        action = decide_action(result)
        result["action"] = action

        upsert_domain_result(result)

        if action == "BUY_CANDIDATE":
            buy_candidates.append(result)
        elif action == "REVIEW":
            review_domains.append(result)
        elif action == "SKIP":
            skipped_domains.append(result)
        elif action == "TAKEN":
            taken_domains.append(result)
        else:
            unknown_domains.append(result)

    buy_candidates.sort(key=lambda x: x["score"], reverse=True)
    review_domains.sort(key=lambda x: x["score"], reverse=True)

    print("=== LOAN BUY CANDIDATES ===")
    for result in buy_candidates:
        print_result(result)

    print("\n=== REVIEW MANUALLY ===")
    for result in review_domains[:25]:
        print_result(result)

    alerts_sent = 0

    for result in buy_candidates:
        if alerts_sent >= MAX_ALERTS:
            break

        domain = result["domain"]

        if already_alerted(domain):
            print(f"Already alerted for {domain}, skipping email")
            continue

        subject = f"Loan Domain Buy Candidate: {domain}"

        body = f"""
Domain: {domain}
Score: {result['score']}
Resale Score: {result.get('resale_likelihood_score')}
Category: {result.get('category')}
Buyer Terms: {result.get('buyer_terms')}
Action Terms: {result.get('action_terms')}
Target Price: ${result.get('target_price')}
Stretch Price: ${result.get('stretch_price')}
Availability: {result.get('availability')}
Source: loans_niche
"""

        send_email_alert(subject, body)
        mark_alerted(domain)
        alerts_sent += 1


if __name__ == "__main__":
    run()