# run_scraper.py
import json
import os

from scrapers import football_api
from scrapers import football_api_shots
from surebet_engine import detect_surebets


def collect_all_odds():
    odds = []
    print("Scraping via API-FOOTBALL (pré-match)...")
    odds += football_api.scrape()
    print(f"Total cotes récupérées : {len(odds)}")
    return odds


if __name__ == "__main__":
    os.makedirs("docs", exist_ok=True)

    all_odds = collect_all_odds()
    surebets = detect_surebets(all_odds)

    with open("docs/surebets.json", "w", encoding="utf-8") as f:
        json.dump(surebets, f, ensure_ascii=False, indent=2)

    print(f"{len(surebets)} surebets trouvés.")

