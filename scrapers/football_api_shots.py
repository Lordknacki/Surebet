# scrapers/football_api_shots.py
import os
from datetime import date
import requests

API_KEY = os.getenv("FOOTBALL_API_KEY", "")
BASE_URL = "https://v3.football.api-sports.io/odds"

# Bets ShotOnGoal :
SHOT_BETS = [87, 88, 89]


def scrape():
    """
    Récupère les cotes pré-match ShotOnGoal (total, home, away)
    via API-FOOTBALL pour tous les matchs du jour.

    Renvoie une liste :
    {
        "match": "Team A - Team B",
        "event_type": "Country - League",
        "market": "Total ShotOnGoal",
        "bookmaker": "...",
        "line": "X.X",
        "odd": value
    }
    """
    if not API_KEY:
        print("[SHOT-API] Clé API manquante")
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
            print("[SHOT-API] Erreur :", e)
            continue

        if res.status_code != 200:
            print("[SHOT-API] Erreur HTTP:", res.status_code)
            continue

        data = res.json().get("response", [])

        for ev in data:
            fixture = ev.get("fixture", {})
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
                    for val in bet.get("values", []):
                        results.append({
                            "match": match_name,
                            "event_type": event_type,
                            "market": bet.get("name"),
                            "bookmaker": bmname,
                            "line": val.get("value"),   # ex: "Over 3.5"
                            "odd": val.get("odd")
                        })

    print(f"[SHOT-API] Total lignes ShotOnGoal récupérées : {len(results)}")
    return results
