import requests

from config import NAMESILO_API_KEY

NAMESILO_API_URL = "https://www.namesilo.com/api/checkRegisterAvailability"


def namesilo_configured() -> bool:
    return bool(NAMESILO_API_KEY and "your_" not in NAMESILO_API_KEY.lower())


def check_domain_availability(domain: str) -> dict:
    if not namesilo_configured():
        return {
            "domain": domain,
            "available": None,
            "is_premium": None,
            "premium_registration_price": None,
            "registration_price": None,
            "renew_price": None,
            "error": "NameSilo API not configured",
        }

    params = {
        "version": "1",
        "type": "json",
        "key": NAMESILO_API_KEY,
        "domains": domain,
    }

    try:
        response = requests.get(NAMESILO_API_URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        reply = data.get("reply", {})
        code = str(reply.get("code", ""))
        detail = reply.get("detail", "")

        if code != "300":
            return {
                "domain": domain,
                "available": None,
                "is_premium": None,
                "premium_registration_price": None,
                "registration_price": None,
                "renew_price": None,
                "error": f"NameSilo API error {code}: {detail}",
            }

        # AVAILABLE CASE
        available_section = reply.get("available")
        if isinstance(available_section, dict):
            domain_info = available_section.get("domain")

            # Case: dict with domain details
            if isinstance(domain_info, dict):
                returned_domain = str(domain_info.get("domain", "")).lower()
                if returned_domain == domain.lower():
                    premium_flag = domain_info.get("premium", 0)

                    return {
                        "domain": domain,
                        "available": True,
                        "is_premium": str(premium_flag) == "1",
                        "premium_registration_price": None,
                        "registration_price": domain_info.get("price"),
                        "renew_price": domain_info.get("renew"),
                        "error": None,
                    }

            # Case: plain string
            if isinstance(domain_info, str) and domain_info.lower() == domain.lower():
                return {
                    "domain": domain,
                    "available": True,
                    "is_premium": None,
                    "premium_registration_price": None,
                    "registration_price": None,
                    "renew_price": None,
                    "error": None,
                }

        # UNAVAILABLE CASE
        unavailable_section = reply.get("unavailable")
        if isinstance(unavailable_section, dict):
            domain_info = unavailable_section.get("domain")

            if isinstance(domain_info, str) and domain_info.lower() == domain.lower():
                return {
                    "domain": domain,
                    "available": False,
                    "is_premium": None,
                    "premium_registration_price": None,
                    "registration_price": None,
                    "renew_price": None,
                    "error": None,
                }

            if isinstance(domain_info, dict):
                returned_domain = str(domain_info.get("domain", "")).lower()
                if returned_domain == domain.lower():
                    return {
                        "domain": domain,
                        "available": False,
                        "is_premium": None,
                        "premium_registration_price": None,
                        "registration_price": None,
                        "renew_price": None,
                        "error": None,
                    }

        return {
            "domain": domain,
            "available": None,
            "is_premium": None,
            "premium_registration_price": None,
            "registration_price": None,
            "renew_price": None,
            "error": f"Could not parse NameSilo availability response: {data}",
        }

    except requests.RequestException as exc:
        return {
            "domain": domain,
            "available": None,
            "is_premium": None,
            "premium_registration_price": None,
            "registration_price": None,
            "renew_price": None,
            "error": f"HTTP error: {exc}",
        }
    except ValueError as exc:
        return {
            "domain": domain,
            "available": None,
            "is_premium": None,
            "premium_registration_price": None,
            "registration_price": None,
            "renew_price": None,
            "error": f"JSON parse error: {exc}",
        }