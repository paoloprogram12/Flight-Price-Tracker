import os
from dotenv import load_dotenv
from amadeus import Client, ResponseError

load_dotenv()

# Get credentials and validate
API_KEY = os.getenv('AMADEUS_API_KEY')
API_SECRET = os.getenv('AMADEUS_API_SECRET')

print(f"DEBUG - Amadeus API Key loaded: {API_KEY[:10] if API_KEY else 'MISSING'}...")
print(f"DEBUG - Amadeus API Secret loaded: {API_SECRET[:10] if API_SECRET else 'MISSING'}...")

# Initialize Amadeus
amadeus = Client(
    client_id=API_KEY,
    client_secret=API_SECRET
)

class APIError(RuntimeError):
    """Custom error for API issues"""
    pass

def prices_for_dates(origin: str, destination: str,
                     departure_at: str, return_at: str = None,
                     currency: str = "USD", limit: int = 30,
                     one_way:bool = False, direct: bool = False):
    """
    Fetch cheapest flight prices for specific dates from Amadeus API.
    
    Args:
        origin: IATA code of origin city/airport (e.g., "LAX")
        destination: IATA code of destination city/airport (e.g., "JFK")
        departure_at: Departure date in YYYY-MM-DD format
        return_at: Return date in YYYY-MM-DD format (None for one-way)
        currency: Currency code (default "USD")
        limit: Max number of results (default 30)
        one_way: True for one-way tickets, False for round-trip (default False)
        direct: True for non-stop flights only (default False)

    Returns:
        List of flight deals with price, dates, airline, etc.

    """

    try:
        print(f"DEBUG - Searching flights: {origin} -> {destination}")
        print(f"DEBUG - Departure: {departure_at}, Return: {return_at}, One-way: {one_way}")

        # Build search parameters
        search_params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departure_at,
            'adults': 1,
            'currencyCode': currency,
            'max': min(limit, 250)  # Amadeus max is 250
        }

        # Add return date for round-trip
        if return_at and not one_way:
            search_params['returnDate'] = return_at

        # Add non-stop filter if requested
        if direct:
            search_params['nonStop'] = 'true'

        print(f"DEBUG - API Parameters: {search_params}")

        # Make API call
        response = amadeus.shopping.flight_offers_search.get(**search_params)

        print(f"DEBUG - Response status: {response.status_code}")
        print(f"DEBUG - Number of offers: {len(response.data)}")

        # Parse results
        results = []
        for offer in response.data:
            # Get first itinerary [outbound]
            itinerary = offer['itineraries'][0]
            segments = itinerary['segments']

            # Get return itinerary if exists
            return_itinerary = offer['itineraries'][1] if len(offer['itineraries']) > 1 else None

            # Calculate local transfers (stops)
            transfers = len(segments) - 1
            return_transfers = len(return_itinerary['segments']) - 1 if return_itinerary else 0

            # Get flight details
            first_segment = segments[0]
            last_segment = segments[-1]

            # Calculate duration (in minutes)
            duration_str = itinerary['duration'] # Format:PT2H30M
            duration = parse_duration(duration_str)

            # Build result obj matching existing format
            results.append({
                "price": float(offer['price']['total']),
                "origin": first_segment['departure']['iataCode'],
                "destination": last_segment['arrival']['iataCode'],
                "depart_date": first_segment['departure']['at'][:10],  # YYYY-MM-DD
                "return_date": return_itinerary['segments'][0]['departure']['at'][:10] if return_itinerary else None,
                "airline": first_segment['carrierCode'],
                "transfers": transfers,
                "return_transfers": return_transfers,
                "duration": duration,
                "flight_number": f"{first_segment['carrierCode']}{first_segment['number']}",
                "link": f"https://www.google.com/travel/flights?q=flights+from+{origin}+to+{destination}+on+{departure_at}"  # Generic booking link
            })

        # sort by price
        results.sort(key=lambda x: x['price'])

        print(f"DEBUG - Returning {len(results)} flights")
        return results[:limit] # return only requested limit
    except ResponseError as error:
        print(f"DEBUG - Amadeus API error:")
        print(f"  Error Type: {type(error).__name__}")
        if hasattr(error, 'response') and error.response:
            print(f"  Status Code: {error.response.status_code}")
            print(f"  Error Details: {error.response.body}")
        if hasattr(error, 'description'):
            desc = error.description() if callable(error.description) else error.description
            print(f"  Description: {desc}")
        print(f"  Full Error: {str(error)}")

        # Get error message
        error_msg = "Unknown error"
        if hasattr(error, 'description'):
            error_msg = error.description() if callable(error.description) else error.description

        raise APIError(f"Amadeus API Error: {error_msg}")
    except Exception as e:
        print(f"DEBUG - Unexpected Error: {str(e)}")
        raise APIError(f"Flight search failed: {str(e)}")
    
def parse_duration(duration_str: str) -> int:
    """
    Parse ISO 8601 duration to minutes.
    Example: PT2H30M -> 150 minutes
    """
    import re

    hours = 0
    minutes = 0

    # Extract hours
    hour_match = re.search(r'(\d+)H', duration_str)
    if hour_match:
        hours = int(hour_match.group(1))

    # Extract minutes
    minute_match = re.search(r'(\d+)M', duration_str)
    if minute_match:
        minutes = int(minute_match.group(1))

    return hours * 60 + minutes

if __name__ == "__main__":
    # Tests API
    print("Testing API")
    results = prices_for_dates("LAX", "JFK", "2026-02-15", "2026-02-20", one_way=False)
    print(f"Found {len(results)} flights")
    if results:
        print(f"Cheapest: ${results[0]['price']}")

# OLD TRAVELPAYOUTS API

# TOKEN = os.getenv("TRAVELPAYOUTS_TOKEN")
# BASE = "https://api.travelpayouts.com/aviasales/v3" # base url for travelpayouts API

# class TPError(RuntimeError): ...
# def _check_token(): # checks if the token is valid, if not valid, returns an error
#     if not TOKEN:
#         raise TPError("TRAVELPAYOUTS_TOKEN is missing. Put it in your .env")
    
#     # defines the main function signature
# def prices_for_dates(origin: str, destination: str,
#                      departure_at: str, return_at: str = None,
#                      currency: str = "USD", limit: int = 30,
#                      one_way: bool = False, direct: bool = False):
#     """
#     Fetch cheapest flight prices for specific dates from Travelpayouts API.

#     Args:
#         origin: IATA code of origin city/airport (e.g., "LAX")
#         destination: IATA code of destination city/airport (e.g., "NRT")
#         departure_at: Departure date in YYYY-MM-DD or YYYY-MM format
#         return_at: Return date in YYYY-MM-DD or YYYY-MM format (None for one-way)
#         currency: Currency code (default "USD")
#         limit: Max number of results (default 30)
#         one_way: True for one-way tickets, False for round-trip (default False)
#         direct: True for non-stop flights only (default False)

#     Returns:
#         List of flight deals with price, dates, airline, etc.
#     """
#     _check_token() # calls the token checker function
#     url = f"{BASE}/prices_for_dates" # build the full API url with the given parameters
#     parameters = { # parameters for the API
#         "origin": origin,
#         "destination": destination,
#         "departure_at": departure_at,
#         "cy": currency,
#         "sorting": "price",
#         "direct": str(direct).lower(),  # API expects "true" or "false" strings
#         "limit": limit,
#         "page": 1,
#         "one_way": str(one_way).lower(),  # API expects "true" or "false" strings
#         "token": TOKEN,
#         "market": "us"
#     }

#     # Only add return_at if provided (for round-trip tickets)
#     if return_at and not one_way:
#         parameters["return_at"] = return_at

#     # for TYO->LAX debug
#     print(f"DEBUG - API Request URL: {url}")
#     print(f"DEBUG - Parameters: {parameters}")

#     # makes the API request, adds parameters to the URL, and sets wait max to 25 sec before giving up
#     r = requests.get(url, params=parameters, timeout=25)

#     if r.status_code == 401:
#         raise TPError("Unauthorized (401). Check TRAVELPAYOUTS_TOKEN")

#     if r.status_code != 200:
#         raise TPError(f"API Error ({r.status_code}): {r.text[:500]}")

#     # built in function that raises an error if status isn;t 2xx
#     r.raise_for_status()

#     # parses the JSON response
#     response_data = r.json()
#     # extracts the flight data
#     data = response_data.get("data", [])

#     results = [] # stores cleaned-up flight data
#     # iterates throught each flight and appends each parameter
#     for it in data:
#         results.append({
#             "price": it.get("price"),  # Field is "price" not "value"
#             "origin": it.get("origin"),
#             "destination": it.get("destination"),
#             "depart_date": it.get("departure_at"),
#             "return_date": it.get("return_at"),
#             "airline": it.get("airline"),
#             "transfers": it.get("transfers"),  # Field is "transfers" not "number_of_changes"
#             "return_transfers": it.get("return_transfers"),
#             "duration": it.get("duration"),
#             "flight_number": it.get("flight_number"),
#             "link": it.get("link"),
#         })
#     return results

