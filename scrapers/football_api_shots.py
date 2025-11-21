import os
from datetime import date
import requests

API_KEY = os.getenv("FOOTBALL_API_KEY", "")
BASE_URL = "https://v3.football.api-sports.io/odds"

SHOT_BETS = [87, 88, 89]  # Total / Home / Away Shots On Target


def scrape():
    if not API_KEY:
        print("[SHOT-API] FOOTBALL_API_KEY manquant.")
        return []

    today = date.today().isoformat()
    headers = {"x-apisports-key": API_KEY}

    results = []

    for bet_id in SHOT_BETS:
        print(f"[SHOT-API] Fetch bet_id={bet_id}...")

        params = {
            "date": today,
            "bet": bet_id
        }

        try:
            res = requests.get(BASE_URL, headers=headers, params=params, timeout=15)
        except Exception as e:
            print("Erreur réseau :", e)
            continue

        if res.status_code != 200:
            print(f"Erreur HTTP {res.status_code} : {res.text[:200]}")
            continue

        response = res.json().get("response", [])

        for ev in response:
            league = ev.get("league", {})
            country = league.get("country", "")
            league_name = league.get("name", "")
            event_type = f"{country} - {league_name}"

            teams = ev.get("teams", {})
            match = f"{teams.get('home', {}).get('name','')} - {teams.get('away', {}).get('name','')}"

            for book in ev.get("bookmakers", []):
                bookmaker = book.get("name")

                for bet in book.get("bets", []):
                    market = bet.get("name")

                    for val in bet.get("values", []):
                        line = val.get("value")
                        odd = val.get("odd")

                        try:
                            odd = float(str(odd).replace(',', '.'))
                        except:
                            continue

                        results.append({
                            "event_type": event_type,
                            "match": match,
                            "market": market,
                            "line": line,
                            "bookmaker": bookmaker,
                            "odd": odd,
                        })

    print(f"[SHOT-API] Total lignes récupérées : {len(results)}")
    return results
