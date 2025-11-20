# surebet_engine.py
from collections import defaultdict

def normalize_name(name):
    return name.lower().replace(" ", "").replace("-", "")

def detect_surebets(odds_list):
    grouped = defaultdict(list)
    for item in odds_list:
        match_key = normalize_name(item['match'])
        grouped[match_key].append(item)

    surebets = []
    for match, offers in grouped.items():
        best = {"1": (None, 0), "N": (None, 0), "2": (None, 0)}
        for offer in offers:
            for key in best.keys():
                val = offer['odds'].get(key)
                if val and val > best[key][1]:
                    best[key] = (offer['bookmaker'], val)
        if all(best[k][1] for k in best):
            inv_sum = sum(1 / best[k][1] for k in best)
            if inv_sum < 1:
                total = 100
                stakes = {k: round((1 / best[k][1]) / inv_sum * total, 2) for k in best}
                profit = round(total / inv_sum - total, 2)
                surebets.append({
                    "match": match,
                    "outcomes": {
                        k: {
                            "bookmaker": best[k][0],
                            "odd": best[k][1],
                            "stake": stakes[k]
                        } for k in best
                    },
                    "profit_percent": round(profit, 2)
                })
    return surebets
