import json
from agents.analyzer import AnalyzerAgent


def load_data():
    with open("scraper.json", "r", encoding="utf-8") as f:
        return json.load(f)


def validate(data):
    assert "sources" in data

    for s in data["sources"]:
        assert "url" in s
        assert "content" in s


def run():
    data = load_data()
    validate(data)

    analyzer = AnalyzerAgent()

    result = analyzer.run(data)

    print("\nRESULT:", result)


if __name__ == "__main__":
    run()