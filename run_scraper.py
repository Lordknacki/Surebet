# run_scraper.py
import json
import os

from scrapers import football_api_shots


def main():
    os.makedirs("docs", exist_ok=True)

    print("Scraping tirs / tirs cadrés (API-FOOTBALL)...")
    shot_lines = football_api_shots.scrape()
    print(f"Total lignes récupérées : {len(shot_lines)}")

    # On écrit le JSON utilisé par le site
    with open("docs/shots.json", "w", encoding="utf-8") as f:
        json.dump(shot_lines, f, ensure_ascii=False, indent=2)

    print("Fichier docs/shots.json mis à jour.")


if __name__ == "__main__":
    main()
