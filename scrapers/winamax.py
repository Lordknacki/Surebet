# scrapers/winamax.py
import requests
import json
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


def scrape():
    url = "https://www.winamax.fr/paris-sportifs/sports/1"

    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
    except Exception as e:
        print(f"[Winamax] Erreur de requête : {e}")
        return []

    print("[Winamax] HTTP status:", res.status_code)

    if res.status_code != 200:
        # Si tu vois 403 ici -> Winamax bloque la requête
        return []

    soup = BeautifulSoup(res.text, "html.parser")

    script = soup.find("script", string=lambda t: t and "PRELOADED_STATE" in t)
    if not script:
        print("[Winamax] Script PRELOADED_STATE introuvable")
        # Pour debug : écrire un extrait dans un fichier
        with open("debug_winamax.html", "w", encoding="utf-8") as f:
            f.write(res.text)
        return []

    try:
        json_text = script.string.split(" = ", 1)[1].rsplit(";", 1)[0]
        data = json.loads(json_text)
    except Exception as e:
        print("[Winamax] Erreur parsing JSON PRELOADED_STATE :", e)
        return []

    matches = data.get("matches", {})
    odds_data = data.get("odds", {})
    bets = data.get("bets", {})
    results = []

    for match_id, match in matches.items():
        if "mainBetId" not in match:
            continue
        bet_id = str(match["mainBetId"])
        if bet_id not in bets:
            continue
        outcomes = bets[bet_id].get("outcomes", [])
        odds = {}
        for oid in outcomes:
            oid_str = str(oid)
            if oid_str in odds_data:
                out = odds_data[oid_str]
                outcome = out.get("label")
                value = out.get("value")
                if outcome and value:
                    try:
                        odds[outcome] = float(value)
                    except ValueError:
                        continue

        if len(odds) == 3:
            results.append(
                {
                    "bookmaker": "Winamax",
                    "match": f"{match['competitor1Name']} - {match['competitor2Name']}",
                    "odds": {
                        # à adapter selon les labels (ex: '1', 'N', '2' ou noms d’équipe)
                        "1": list(odds.values())[0],
                        "N": list(odds.values())[1],
                        "2": list(odds.values())[2],
                    },
                }
            )

    print(f"[Winamax] Matchs récupérés : {len(results)}")
    return results
