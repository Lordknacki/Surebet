# run_scraper.py
import json
from scrapers import winamax  # Ajoute d'autres scrapers ici si dispo
from surebet_engine import detect_surebets

def collect_all_odds():
    odds = []
    odds += winamax.scrape()
    # odds += betclic.scrape()
    # odds += unibet.scrape()
    # odds += betify.scrape()
    return odds

if __name__ == "__main__":
    all_odds = collect_all_odds()
    surebets = detect_surebets(all_odds)
    with open("docs/surebets.json", "w", encoding="utf-8") as f:
        json.dump(surebets, f, ensure_ascii=False, indent=2)
    print(f"{len(surebets)} surebets trouvés.")
