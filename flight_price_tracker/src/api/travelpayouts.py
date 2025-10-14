import os, requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TRAVELPAYOUTS_TOKEN")
BASE = "https://api.travelpayouts.com/aviasales/v3"

class TPError(RuntimeError): ...
def _check_token():
    if not TOKEN:
        raise TPError("TRAVELPAYOUTS_TOKEN is missing. Put it in your .env")
    
def prices_for_dates(origin: str, destination: str,
                     depart_from: str, depart_to: str,
                     return_from: str, return_to: str,
                     currency: str = "USD", limit: int = 30):
    _check_token()
    url = f"{BASE}/prices_for_dates"
    parameters = {
        "origin": origin,
        "destination": destination,
        "departure_at": f"{depart_from}:{depart_to}",
        "return_at": f"{return_from}:{return_to}",
        "currency": currency,
        "sorting": "price",
        "direct": False,
        "limit": limit,
        "page": 1,
        "token": TOKEN,
    }

    r = requests.get(url, params=parameters, timeout=25)

    if r.status_code == 401:
        raise TPError("Unauthorized (401). Check TRAVELPAYOUTS_TOKEN")
    r.raise_for_status()

    data = r.json().get("data", [])
    results = []
    for it in data:
        results.append({
            "price": it.get("value"),
            "origin": it.get("origin"),
            "destination": it.get("destination"),
            "depart_date": it.get("depart_date") or it.get("departure_at"),
            "return_date": it.get("return_date") or it.get("return_at"),
            "airline": it.get("airline"),
            "changes": it.get("number_of_changes"),
            "found_at": it.get("found_at"),
            "link": it.get("link"),
        })
    return results

if __name__ == "__main__":
    print("Token:", TOKEN)

    