# scrapers/football_api.py
import os
from datetime import date
import requests

# ⚠️ Mets ta clé dans la variable d'environnement FOOTBALL_API_KEY
API_KEY = os.getenv("FOOTBALL_API_KEY", "291a35a2f0a0e05b445851d33bd05ca6")

BASE_URL = "https://v3.football.api-sports.io/odds"


def scrape():
    """
    Récupère les cotes pré-match (1N2) pour tous les matchs du jour
    via API-FOOTBALL, et renvoie une liste d'objets au format:
    {
        "bookmaker": "...",
        "match": "Home - Away",
        "event_type": "Pays - Compétition",
        "odds": {"1": x.xx, "N": y.yy, "2": z.zz}
    }
    utilisable directement par surebet_engine.detect_surebets().
    """
    if not API_KEY:
        print("[API-FOOTBALL] Clé API manquante (FOOTBALL_API_KEY)")
        return []

    today = date.today().isoformat()  # ex: "2025-11-20"

    headers = {
        "x-rapidapi-host": "v3.football.api-sports.io",  # souvent toléré
        "x-apisports-key": API_KEY,
    }

    params = {
        "date": today,          # tous les matchs du jour
        "bet": 1,               # id du bet "Match Winner" (1X2) en général
        # tu peux ajouter "timezone": "Europe/Paris" si besoin
    }

    try:
        res = requests.get(BASE_URL, headers=headers, params=params, timeout=15)
    except Exception as e:
        print(f"[API-FOOTBALL] Erreur de requête : {e}")
        return []

    if res.status_code != 200:
        print(f"[API-FOOTBALL] Statut HTTP inattendu : {res.status_code}")
        print(res.text[:500])
        return []

    payload = res.json()
    matches = payload.get("response", [])
    print(f"[API-FOOTBALL] Évènements renvoyés : {len(matches)}")

    results = []

    for ev in matches:
        fixture = ev.get("fixture", {})
        league = ev.get("league", {})
        teams = ev.get("teams", {})
        home_team = teams.get("home", {}).get("name")
        away_team = teams.get("away", {}).get("name")

        if not home_team or not away_team:
            continue

        match_name = f"{home_team} - {away_team}"
        event_type = f"{league.get('country', '')} - {league.get('name', '')}"

        bookmakers = ev.get("bookmakers", [])
        for bm in bookmakers:
            bm_name = bm.get("name") or str(bm.get("id"))

            for bet in bm.get("bets", []):
                # On sécurise au cas où "bet" ne serait pas celui qu'on veut
                bet_name = bet.get("name", "").lower()
                if "winner" not in bet_name and "match winner" not in bet_name:
                    # Si tu forces bet=1 dans params, tu peux enlever ce test
                    continue

                odds_map = {}
                values = bet.get("values", [])

                for v in values:
                    label = v.get("value")      # "Home", "Draw", "Away", ou nom d'équipe
                    odd_str = v.get("odd")
                    if not label or not odd_str:
                        continue

                    try:
                        odd = float(str(odd_str).replace(",", "."))
                    except ValueError:
                        continue

                    l = label.lower()
                    if l in ("home", home_team.lower()):
                        odds_map["1"] = odd
                    elif l in ("away", away_team.lower()):
                        odds_map["2"] = odd
                    elif l in ("draw", "nul", "drawn"):
                        odds_map["N"] = odd

                # On garde seulement si on a bien 1 / N / 2
                if set(odds_map.keys()) == {"1", "N", "2"}:
                    results.append(
                        {
                            "bookmaker": bm_name,
                            "match": match_name,
                            "event_type": event_type,
                            "odds": odds_map,
                        }
                    )

    print(f"[API-FOOTBALL] Offres exploitables (1N2 complètes) : {len(results)}")
    return results
