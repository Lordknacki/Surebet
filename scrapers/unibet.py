# scrapers/unibet.py
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.unibet.fr/sport/football"


def _to_float(text: str) -> float | None:
    text = text.strip().replace(',', '.')
    try:
        return float(text)
    except ValueError:
        return None


def scrape():
    """
    Scraper simplifié pour Unibet (version HTML).
    Tu peux aussi, plus tard, utiliser leurs endpoints JSON,
    mais ça demande plus de reverse engineering.
    """
    try:
        res = requests.get(BASE_URL, timeout=10)
    except Exception as e:
        print(f"[Unibet] Erreur de requête : {e}")
        return []

    if res.status_code != 200:
        print(f"[Unibet] Statut HTTP inattendu : {res.status_code}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    results = []

    # ⚠️ À ADAPTER : bloc d’un match
    match_cards = soup.select(".ui-main-view .event, .KambiBC-event-item, .event-card")

    for card in match_cards:
        # ⚠️ À ADAPTER : noms des équipes
        team_elems = card.select(".event__participant, .KambiBC-event-participants__name, .team-name")
        if len(team_elems) < 2:
            continue

        team1 = team_elems[0].get_text(strip=True)
        team2 = team_elems[1].get_text(strip=True)
        match_name = f"{team1} - {team2}"

        # ⚠️ À ADAPTER : cotes 1N2
        odd_elems = card.select(
            ".KambiBC-outcome__odds, .outcome__odds, .bet-price"
        )
        if len(odd_elems) < 3:
            continue

        odds_values = []
        for el in odd_elems[:3]:
            val = _to_float(el.get_text())
            if val is not None:
                odds_values.append(val)

        if len(odds_values) != 3:
            continue

        odds = {
            "1": odds_values[0],
            "N": odds_values[1],
            "2": odds_values[2],
        }

        results.append(
            {
                "bookmaker": "Unibet",
                "match": match_name,
                "odds": odds,
            }
        )

    print(f"[Unibet] Matchs récupérés : {len(results)}")
    return results
