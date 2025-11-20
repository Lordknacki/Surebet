# scrapers/betify.py
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://betify2.sh/fr/sport?bt-path=%2Fsoccer-1"  # ⚠️ remplace par l'URL réelle


def _to_float(text: str) -> float | None:
    text = text.strip().replace(',', '.')
    try:
        return float(text)
    except ValueError:
        return None


def scrape():
    """
    Gabarit de scraper pour Betify.
    Tu dois OBLIGATOIREMENT adapter :
    - l'URL
    - les sélecteurs des matchs, équipes, et cotes.
    """
    try:
        res = requests.get(BASE_URL, timeout=10)
    except Exception as e:
        print(f"[Betify] Erreur de requête : {e}")
        return []

    if res.status_code != 200:
        print(f"[Betify] Statut HTTP inattendu : {res.status_code}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    results = []

    # ⚠️ À ADAPTER : bloc d’un match
    match_cards = soup.select(".match, .event, .event-card")

    for card in match_cards:
        # ⚠️ À ADAPTER : noms des équipes
        team_elems = card.select(".team-name, .event-team, .event__participant")
        if len(team_elems) < 2:
            continue

        team1 = team_elems[0].get_text(strip=True)
        team2 = team_elems[1].get_text(strip=True)
        match_name = f"{team1} - {team2}"

        # ⚠️ À ADAPTER : cotes 1N2
        odd_elems = card.select(".odd, .price, .bet-odd")
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
                "bookmaker": "Betify",
                "match": match_name,
                "odds": odds,
            }
        )

    print(f"[Betify] Matchs récupérés : {len(results)}")
    return results
