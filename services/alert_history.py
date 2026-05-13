import json
import os

ALERT_HISTORY_FILE = "alerted_domains.json"


def load_alerted_domains():
    if not os.path.exists(ALERT_HISTORY_FILE):
        return set()

    try:
        with open(ALERT_HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_alerted_domains(domains):
    with open(ALERT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(domains)), f, indent=2)


def already_alerted(domain):
    alerted = load_alerted_domains()
    return domain.lower() in alerted


def mark_alerted(domain):
    alerted = load_alerted_domains()
    alerted.add(domain.lower())
    save_alerted_domains(alerted)