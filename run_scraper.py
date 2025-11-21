import json
import os
from scrapers import football_api_shots

def main():
    os.makedirs("docs", exist_ok=True)

    print("Scraping tirs / tirs cadrés...")
    data = football_api_shots.scrape()

    with open("docs/shots.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("docs/shots.json mis à jour avec", len(data), "lignes.")

if __name__ == "__main__":
    main()
