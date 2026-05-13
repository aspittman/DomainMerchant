from services.domain_scorer import score_domain


def evaluate_domain(domain):
    scores = score_domain(domain)

    return {
        "domain": domain,
        "brand_score": scores["brand_score"],
        "seo_score": 0,
        "score": scores["final_score"],
        "resale_likelihood_score": scores["resale_likelihood_score"],
        "low_price": scores["low_price"],
        "target_price": scores["target_price"],
        "stretch_price": scores["stretch_price"],
        "trademark_risk": scores["trademark_risk"],
        "obvious_buyer": scores["obvious_buyer"],
        "buyer_terms": scores["buyer_terms"],
        "action_terms": scores["action_terms"],
        "category": scores["category"],
        "metrics": {
            "source": "seo_disabled"
        }
    }