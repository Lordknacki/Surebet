# scrapers/winamax.py
import requests
import json
from bs4 import BeautifulSoup

def scrape():
    url = "https://www.winamax.fr/paris-sportifs/sports/1"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    script = soup.find("script", string=lambda t: t and "PRELOADED_STATE" in t)
    if not script:
        return []
    json_text = script.string.split(" = ",1)[1].rsplit(";",1)[0]
    data = json.loads(json_text)
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
                    odds[outcome] = float(value)
        if len(odds) == 3:
            results.append({
                "bookmaker": "Winamax",
                "match": f"{match['competitor1Name']} - {match['competitor2Name']}",
                "odds": odds
            })
    return results
