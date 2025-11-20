# run_scraper.py
import json

from scrapers import winamax, betclic, unibet, betify
from surebet_engine import detect_surebets


def collect_all_odds():
    odds = []
    print("Scraping Winamax...")
    odds += winamax.scrape()

    print("Scraping Betclic...")
    odds += betclic.scrape()

    print("Scraping Unibet...")
    odds += unibet.scrape()

    print("Scraping Betify...")
    odds += betify.scrape()

    print(f"Total cotes récupérées : {len(odds)}")
    return odds


if __name__ == "__main__":
    all_odds = collect_all_odds()
    surebets = detect_surebets(all_odds)

    # crée le dossier docs/ si besoin
    import os
    os.makedirs("docs", exist_ok=True)

    with open("docs/surebets.json", "w", encoding="utf-8") as f:
        json.dump(surebets, f, ensure_ascii=False, indent=2)

    print(f"{len(surebets)} surebets trouvés.")
