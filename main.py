from data.db import init_db, upsert_domain_result
from services.domain_finder import get_expired_domains
from services.availability_checker import check_domain_availability
from strategies.basic_strategy import evaluate_domain
from services.alerts import send_sms

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
    domains = get_expired_domains()

    print(f"Found {len(domains)} domains\n")

    buy_candidates = []
    review_domains = []
    skipped_domains = []
    taken_domains = []
    unknown_domains = []

    for domain in domains:
        result = evaluate_domain(domain)
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

        if action == "BUY_CANDIDATE" and result["availability"]["available"]:
            send_sms(f"BUY: {result['domain']} | Score: {result['score']}")

    buy_candidates.sort(key=lambda x: x["score"], reverse=True)
    review_domains.sort(key=lambda x: x["score"], reverse=True)
    skipped_domains.sort(key=lambda x: x["score"], reverse=True)
    taken_domains.sort(key=lambda x: x["score"], reverse=True)
    unknown_domains.sort(key=lambda x: x["score"], reverse=True)

    print("=== BUY CANDIDATES ===")
    for result in buy_candidates:
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