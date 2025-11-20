# surebet_engine.py
from collections import defaultdict, Counter


def normalize_name(name: str) -> str:
    """Normalise le nom de match pour regrouper les mêmes rencontres."""
    return name.lower().replace(" ", "").replace("-", "")


def detect_surebets(odds_list):
    """
    Analyse toutes les offres :
    - Regroupe par match
    - Prend la meilleure cote pour 1 / N / 2 (tous bookmakers confondus)
    - Calcule le profit théorique en %
    - Indique si c'est un surebet (profit > 0)

    Renvoie une liste de dicts :
    {
      "match": "...",
      "event_type": "...",
      "outcomes": {
        "1": {"bookmaker": "...", "odd": x.xx, "stake": yy.yy},
        "N": {...},
        "2": {...}
      },
      "profit_percent": 2.34,
      "is_surebet": True/False
    }
    """
    grouped = defaultdict(list)
    for item in odds_list:
        match_key = normalize_name(item["match"])
        grouped[match_key].append(item)

    results = []

    for match_key, offers in grouped.items():
        # On récupère un nom de match lisible (le premier)
        match_name = offers[0]["match"]

        # On essaie de déterminer un type d'évènement (titre de sport/compétition)
        event_types = [o.get("event_type") for o in offers if o.get("event_type")]
        event_type = ""
        if event_types:
            event_type = Counter(event_types).most_common(1)[0][0]

        # On cherche la meilleure cote pour 1 / N / 2
        best = {"1": (None, 0.0), "N": (None, 0.0), "2": (None, 0.0)}
        for offer in offers:
            for key in best.keys():
                val = offer["odds"].get(key)
                if val and float(val) > best[key][1]:
                    best[key] = (offer["bookmaker"], float(val))

        # Si on n'a pas les 3 issues, on zappe ce match
        if not all(best[k][1] > 0 for k in best):
            continue

        inv_sum = sum(1.0 / best[k][1] for k in best)
        if inv_sum == 0:
            continue

        # Profit théorique en % (positif = surebet, négatif = marge bookmaker)
        profit_percent = round((1.0 / inv_sum - 1.0) * 100.0, 2)

        # On calcule les mises optimales pour un total de 100€
        total = 100.0
        stakes = {
            k: round((1.0 / best[k][1]) / inv_sum * total, 2)
            for k in best
        }

        is_surebet = profit_percent > 0

        results.append(
            {
                "match": match_name,
                "event_type": event_type,
                "outcomes": {
                    k: {
                        "bookmaker": best[k][0],
                        "odd": best[k][1],
                        "stake": stakes[k],
                    }
                    for k in best
                },
                "profit_percent": profit_percent,
                "is_surebet": is_surebet,
            }
        )

    # Optionnel : trier pour voir les surebets en haut
    results.sort(key=lambda x: x["profit_percent"], reverse=True)
    return results
