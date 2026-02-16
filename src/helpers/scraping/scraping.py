import os, json

def get_products(path=None):
    # default path if not provided
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))  # helpers/scraping
        path = os.path.join(base_dir, "unique_products.json")

    if not os.path.exists(path):
        print(f"⚠️ Products file not found at {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        products = json.load(f)
    return products


def get_events(path=None):
    # default path if not provided
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))  # helpers/scraping
        path = os.path.join(base_dir, "final_interactions.json")

    if not os.path.exists(path):
        print(f"⚠️ Events file not found at {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        events = json.load(f)
    return events


