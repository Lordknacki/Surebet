# scrapers/odds_api.py
import os
import requests

# 👉 En local tu peux laisser la clé en dur le temps de tester
API_KEY = os.getenv("ODDS_API_KEY", "b810457ba299479dfbdfb647b2a408ae")

BASE_URL = "https://api.the-odds-api.com/v4/sports/upcoming/odds/"

PARAMS = {
    "regions": "eu",   # comme dans ton URL
    "markets": "h2h",  # 1N2 (head-to-head)
    "apiKey": API_KEY,
}


def scrape():
    """
    Récupère toutes les cotes H2H à venir en Europe
    via The Odds API, filtre sur le football/soccer,
    et renvoie une liste au format attendu par surebet_engine.detect_surebets().
    """
    try:
        res = requests.get(BASE_URL, params=PARAMS, timeout=10)
    except Exception as e:
        print(f"[OddsAPI] Erreur de requête : {e}")
        return []

    if res.status_code != 200:
        print(f"[OddsAPI] Statut HTTP inattendu : {res.status_code} / {res.text[:200]}")
        return []

    events = res.json()
    results = []

    for ev in events:
        sport_key = ev.get("sport_key", "")
        # ⚽ On garde seulement les sports de type soccer/football
        if "soccer" not in sport_key and "football" not in sport_key:
            continue

        home = ev.get("home_team")
        away = ev.get("away_team")
        if not home or not away:
            continue

        match_name = f"{home} - {away}"

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

                    # On mappe home/draw/away en 1 / N / 2
                    if name == home:
                        odds_map["1"] = float(price)
                    elif name == away:
                        odds_map["2"] = float(price)
                    elif name.lower() in ("draw", "nul", "tie"):
                        odds_map["N"] = float(price)

                # On ne garde que si on a les 3 issues
                if len(odds_map) == 3:
                    results.append(
                        {
                            "bookmaker": bm_name,
                            "match": match_name,
                            "odds": odds_map,
                        }
                    )

    print(f"[OddsAPI] Matchs récupérés : {len(results)}")
    return results
