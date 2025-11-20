# scrapers/odds_api.py
import os
import requests

# En prod / sur GitHub Actions : ODDS_API_KEY doit être dans les secrets
API_KEY = os.getenv("ODDS_API_KEY", "b810457ba299479dfbdfb647b2a408ae")

# On cible directement le football (soccer)
BASE_URL = "https://api.the-odds-api.com/v4/sports/soccer/odds/"

# On demande un max de régions (donc un max de bookmakers)
PARAMS = {
    "regions": "eu,uk,us,au",   # Europe, UK, USA, Australie
    "markets": "h2h",           # 1X2 / head-to-head
    "oddsFormat": "decimal",
    "apiKey": API_KEY,
}


def scrape():
    """
    Récupère un maximum de matchs de football avec leurs cotes 1N2
    via The Odds API, sur plusieurs régions (eu, uk, us, au),
    et renvoie une liste d'objets au format :
    {
        "bookmaker": "...",
        "match": "Home - Away",
        "event_type": "Soccer - UEFA Champions League",
        "odds": {"1": x.xx, "N": y.yy, "2": z.zz}
    }
    utilisable directement par surebet_engine.detect_surebets().
    """
    try:
        res = requests.get(BASE_URL, params=PARAMS, timeout=15)
    except Exception as e:
        print(f"[OddsAPI] Erreur de requête : {e}")
        return []

    if res.status_code != 200:
        print(f"[OddsAPI] Statut HTTP inattendu : {res.status_code}")
        print(res.text[:500])
        return []

    events = res.json()
    results = []

    print(f"[OddsAPI] Évènements renvoyés par l'API : {len(events)}")

    for ev in events:
        sport_key = ev.get("sport_key", "")
        # Par sécurité : on ne garde que les trucs soccer
        if not sport_key.startswith("soccer"):
            continue

        home = ev.get("home_team")
        away = ev.get("away_team")
        if not home or not away:
            continue

        match_name = f"{home} - {away}"
        event_type = ev.get("sport_title", "")  # ex : "Soccer - UEFA Champions League"

        bookmakers = ev.get("bookmakers", [])

        for bm in bookmakers:
            bm_name = bm.get("title") or bm.get("key")

            for market in bm.get("markets", []):
                if market.get("key") != "h2h":
                    continue

                odds_map = {}
                outcomes = market.get("outcomes", [])

                for outcome in outcomes:
                    name = outcome.get("name")
                    price = outcome.get("price")
                    if name is None or price is None:
                        continue

                    # On mappe : home → 1, away → 2, draw → N
                    if name == home:
                        odds_map["1"] = float(price)
                    elif name == away:
                        odds_map["2"] = float(price)
                    elif str(name).lower() in ("draw", "nul", "tie"):
                        odds_map["N"] = float(price)

                # On ne garde que les cotes où il y a bien 1, N, 2
                if set(odds_map.keys()) == {"1", "N", "2"}:
                    results.append(
                        {
                            "bookmaker": bm_name,
                            "match": match_name,
                            "event_type": event_type,
                            "odds": odds_map,
                        }
                    )

    print(f"[OddsAPI] Offres exploitables (1N2 complètes) : {len(results)}")
    return results
