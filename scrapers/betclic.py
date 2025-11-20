# scrapers/betclic.py
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.betclic.fr/football-s1"


def _to_float(text: str) -> float | None:
    text = text.strip().replace(',', '.')
    try:
        return float(text)
    except ValueError:
        return None


def scrape():
    """
    Scraper simplifié pour Betclic.
    ⚠️ Tu devras adapter les sélecteurs CSS en fonction du HTML réel.
    """
    try:
        res = requests.get(BASE_URL, timeout=10)
    except Exception as e:
        print(f"[Betclic] Erreur de requête : {e}")
        return []

    if res.status_code != 200:
        print(f"[Betclic] Statut HTTP inattendu : {res.status_code}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    results = []

    # ⚠️ À ADAPTER : sélecteur des blocs de matchs
    # Inspecte le HTML de Betclic et trouve le conteneur de chaque match
    match_cards = soup.select(".card-event, .event-item, .match, .event")  # exemples génériques

    for card in match_cards:
        # ⚠️ À ADAPTER : sélecteurs des noms d'équipes
        team_elems = card.select(".scoreboard_contestantLabel, .team-name, .event__participant")
        if len(team_elems) < 2:
            continue

        team1 = team_elems[0].get_text(strip=True)
        team2 = team_elems[1].get_text(strip=True)
        match_name = f"{team1} - {team2}"

        # ⚠️ À ADAPTER : sélecteur des cotes 1N2
        odd_elems = card.select(".oddValue, .option__price, .betButton__odd")
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
                "bookmaker": "Betclic",
                "match": match_name,
                "odds": odds,
            }
        )

    print(f"[Betclic] Matchs récupérés : {len(results)}")
    return results
