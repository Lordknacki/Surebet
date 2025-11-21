# scrapers/football_api_shots.py
import os
from datetime import date
import requests

API_KEY = os.getenv("FOOTBALL_API_KEY", "")
BASE_URL = "https://v3.football.api-sports.io/odds"

# Bets ShotOnGoal :
SHOT_BETS = [87, 88, 89]  # Total, Home, Away


def scrape():
    """
    Récupère les cotes pré-match ShotOnGoal (total, home, away)
    via API-FOOTBALL pour tous les matchs du jour.

    Renvoie une liste de dicts :
    {
        "match": "Team A - Team B",
        "event_type": "Country - League",
        "market": "Total ShotOnGoal / Home Total ShotOnGoal / Away Total ShotOnGoal",
        "bookmaker": "Unibet",
        "line": "Over 3.5",
        "odd": 1.85
    }
    """
    if not API_KEY:
        print("[SHOT-API] Clé API manquante (FOOTBALL_API_KEY)")
        return []

    today = date.today().isoformat()

    headers = {
        "x-apisports-key": API_KEY,
    }

    results = []

    for bet_id in SHOT_BETS:
        params = {
            "date": today,
            "bet": bet_id
        }

        print(f"[SHOT-API] Récupération des bets ID = {bet_id}...")

        try:
            res = requests.get(BASE_URL, headers=headers, params=params, timeout=15)
        except Exception as e:
            print("[SHOT-API] Erreur de requête :", e)
            continue

        if res.status_code != 200:
            print("[SHOT-API] Erreur HTTP :", res.status_code)
            print(res.text[:300])
            continue

        data = res.json().get("response", [])

        for ev in data:
            league = ev.get("league", {})
            teams = ev.get("teams", {})
            home = teams.get("home", {}).get("name")
            away = teams.get("away", {}).get("name")

            if not home or not away:
                continue

            match_name = f"{home} - {away}"
            event_type = f"{league.get('country', '')} - {league.get('name', '')}"

            for bookmaker in ev.get("bookmakers", []):
                bmname = bookmaker.get("name")

                for bet in bookmaker.get("bets", []):
                    market_name = bet.get("name")

                    for val in bet.get("values", []):
                        line = val.get("value")   # ex: "Over 3.5"
                        odd_str = val.get("odd")

                        if not line or not odd_str:
                            continue

                        try:
                            odd = float(str(odd_str).replace(",", "."))
                        except ValueError:
                            continue

                        results.append({
                            "match": match_name,
                            "event_type": event_type,
                            "market": market_name,
                            "bookmaker": bmname,
                            "line": line,
                            "odd": odd,
                        })

    print(f"[SHOT-API] Total lignes ShotOnGoal récupérées : {len(results)}")
    return results
