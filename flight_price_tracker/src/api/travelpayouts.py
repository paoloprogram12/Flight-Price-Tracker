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
                     departure_at: str, return_at: str = None,
                     currency: str = "USD", limit: int = 30,
                     one_way: bool = False, direct: bool = False):
    """
    Fetch cheapest flight prices for specific dates from Travelpayouts API.

    Args:
        origin: IATA code of origin city/airport (e.g., "LAX")
        destination: IATA code of destination city/airport (e.g., "NRT")
        departure_at: Departure date in YYYY-MM-DD or YYYY-MM format
        return_at: Return date in YYYY-MM-DD or YYYY-MM format (None for one-way)
        currency: Currency code (default "USD")
        limit: Max number of results (default 30)
        one_way: True for one-way tickets, False for round-trip (default False)
        direct: True for non-stop flights only (default False)

    Returns:
        List of flight deals with price, dates, airline, etc.
    """
    _check_token()
    url = f"{BASE}/prices_for_dates"
    parameters = {
        "origin": origin,
        "destination": destination,
        "departure_at": departure_at,
        "cy": currency,
        "sorting": "price",
        "direct": str(direct).lower(),  # API expects "true" or "false" strings
        "limit": limit,
        "page": 1,
        "one_way": str(one_way).lower(),  # API expects "true" or "false" strings
        "token": TOKEN,
        "market": "us"
    }

    # Only add return_at if provided (for round-trip tickets)
    if return_at and not one_way:
        parameters["return_at"] = return_at

    r = requests.get(url, params=parameters, timeout=25)

    if r.status_code == 401:
        raise TPError("Unauthorized (401). Check TRAVELPAYOUTS_TOKEN")

    if r.status_code != 200:
        raise TPError(f"API Error ({r.status_code}): {r.text[:500]}")

    r.raise_for_status()

    response_data = r.json()
    data = response_data.get("data", [])

    results = []
    for it in data:
        results.append({
            "price": it.get("price"),  # Field is "price" not "value"
            "origin": it.get("origin"),
            "destination": it.get("destination"),
            "depart_date": it.get("departure_at"),
            "return_date": it.get("return_at"),
            "airline": it.get("airline"),
            "transfers": it.get("transfers"),  # Field is "transfers" not "number_of_changes"
            "return_transfers": it.get("return_transfers"),
            "duration": it.get("duration"),
            "flight_number": it.get("flight_number"),
            "link": it.get("link"),
        })
    return results

if __name__ == "__main__":
    print("Token:", TOKEN)
