from data.db import init_db, upsert_domain_result
from services.availability_checker import check_domain_availability
from strategies.basic_strategy import evaluate_domain
#from services.alerts import send_sms
from services.domain_finder import get_all_candidate_domains
from services.email_alerts import send_email_alert
from services.alert_history import already_alerted, mark_alerted

def decide_action(result):
    availability = result.get("availability", {})
    available = availability.get("available")

    final_score = result["score"]
    brand_score = result["brand_score"]
    resale = result.get("resale_likelihood_score", 0)
    obvious_buyer = result.get("obvious_buyer", False)
    trademark_risk = result.get("trademark_risk", False)

    if available is False:
        return "TAKEN"

    if trademark_risk:
        return "SKIP"

    if available is True:
        if obvious_buyer and final_score >= 75 and brand_score >= 45 and resale >= 55:
            return "BUY_CANDIDATE"
        elif obvious_buyer and final_score >= 45 and brand_score >= 35:
            return "REVIEW"
        else:
            return "SKIP"

    return "UNKNOWN"


def print_result(result):
    availability = result.get("availability", {})
    available = availability.get("available")
    is_premium = availability.get("is_premium")
    registration_price = availability.get("registration_price")
    renew_price = availability.get("renew_price")
    error = availability.get("error")

    if available is True:
        status = "AVAILABLE"
    elif available is False:
        status = "NOT AVAILABLE"
    else:
        status = "UNKNOWN"

    action = result.get("action", "UNKNOWN")

    extra = f" | Action: {action}"

    if is_premium is True:
        extra += " | Premium: YES"
    elif is_premium is False:
        extra += " | Premium: NO"

    if registration_price is not None:
        extra += f" | Reg Price: ${registration_price}"

    if renew_price is not None:
        extra += f" | Renew: ${renew_price}"

    if error:
        extra += f" | ERROR: {error}"

    print(
        f"{result['domain']} | "
        f"Brand: {result['brand_score']} | "
        f"SEO: {result['seo_score']} | "
        f"Final: {result['score']} | "
        f"Status: {status}"
        f"{extra}"
    )


def run_bot():
    init_db()
    
    candidates = get_all_candidate_domains()
    print(f"Found {len(candidates)} total candidate domains\n")

    buy_candidates = []
    review_domains = []
    skipped_domains = []
    taken_domains = []
    unknown_domains = []

    for item in candidates:
        domain = item["domain"]
        source = item["source"]

        result = evaluate_domain(domain)
        result["source"] = source
        result["availability"] = check_domain_availability(domain)

        action = decide_action(result)
        result["action"] = action

        upsert_domain_result(result)

        if action == "BUY_CANDIDATE" and result["availability"]["available"]:
            buy_candidates.append(result)

        elif action == "REVIEW":
            review_domains.append(result)

        elif action == "SKIP":
            skipped_domains.append(result)

        elif action == "TAKEN":
            taken_domains.append(result)

        else:
            unknown_domains.append(result)

    # 🔥 Sort AFTER scanning everything
    buy_candidates.sort(key=lambda x: x["score"], reverse=True)
    review_domains.sort(key=lambda x: x["score"], reverse=True)
    skipped_domains.sort(key=lambda x: x["score"], reverse=True)
    taken_domains.sort(key=lambda x: x["score"], reverse=True)
    unknown_domains.sort(key=lambda x: x["score"], reverse=True)

    # 🔥 Only alert top 3
    MAX_ALERTS = 3
    alerts_sent = 0

    for result in buy_candidates:
        domain = result["domain"]

        if already_alerted(domain):
            print(f"Already alerted for {domain}, skipping email")
            continue

        if alerts_sent >= MAX_ALERTS:
            break

        subject = f"🔥 Domain Buy Candidate: {domain}"

        body = f"""
    Domain: {domain}
    Score: {result['score']}
    Brand Score: {result['brand_score']}
    Resale Score: {result.get('resale_likelihood_score')}
    Category: {result.get('category')}
    Buyer Terms: {result.get('buyer_terms')}
    Action Terms: {result.get('action_terms')}

    Registration Price: {result['availability'].get('registration_price')}
    Renewal Price: {result['availability'].get('renew_price')}

    Source: {result.get('source')}
    """

        send_email_alert(subject, body)
        mark_alerted(domain)
        alerts_sent += 1

    # 🔥 Output results
    print("=== BUY CANDIDATES ===")
    for result in buy_candidates:
        if result["score"] >= 85:
            print("🔥 HIGH VALUE DETECTED:", result["domain"])
        print_result(result)

    print("\n=== REVIEW MANUALLY ===")
    for result in review_domains:
        print_result(result)

    print("\n=== SKIP ===")
    for result in skipped_domains:
        print_result(result)

    print("\n=== TAKEN ===")
    for result in taken_domains:
        print_result(result)

    if unknown_domains:
        print("\n=== UNKNOWN ===")
        for result in unknown_domains:
            print_result(result)


if __name__ == "__main__":
    run_bot()