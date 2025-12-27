import os, requests # os reads environment variables like API token, requests makes HTTP requests to travelpayouts
from dotenv import load_dotenv # reads .env file

load_dotenv()
TOKEN = os.getenv("TRAVELPAYOUTS_TOKEN")
BASE = "https://api.travelpayouts.com/aviasales/v3" # base url for travelpayouts API

class TPError(RuntimeError): ...
def _check_token(): # checks if the token is valid, if not valid, returns an error
    if not TOKEN:
        raise TPError("TRAVELPAYOUTS_TOKEN is missing. Put it in your .env")
    
    # defines the main function signature
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
    _check_token() # calls the token checker function
    url = f"{BASE}/prices_for_dates" # build the full API url with the given parameters
    parameters = { # parameters for the API
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

    # for TYO->LAX debug
    print(f"DEBUG - API Request URL: {url}")
    print(f"DEBUG - Parameters: {parameters}")

    # makes the API request, adds parameters to the URL, and sets wait max to 25 sec before giving up
    r = requests.get(url, params=parameters, timeout=25)

    if r.status_code == 401:
        raise TPError("Unauthorized (401). Check TRAVELPAYOUTS_TOKEN")

    if r.status_code != 200:
        raise TPError(f"API Error ({r.status_code}): {r.text[:500]}")

    # built in function that raises an error if status isn;t 2xx
    r.raise_for_status()

    # parses the JSON response
    response_data = r.json()
    # extracts the flight data
    data = response_data.get("data", [])

    results = [] # stores cleaned-up flight data
    # iterates throught each flight and appends each parameter
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
