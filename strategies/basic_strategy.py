from services.domain_scorer import score_domain
from services.seo_filter import get_mock_seo_metrics


def evaluate_domain(domain):
    metrics = get_mock_seo_metrics(domain)
    scores = score_domain(domain, metrics)

    return {
        "domain": domain,
        "brand_score": scores["brand_score"],
        "seo_score": scores["seo_score"],
        "score": scores["final_score"],
        "metrics": metrics
    }