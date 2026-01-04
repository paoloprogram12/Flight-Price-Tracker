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
                     one_way:bool = False, direct: bool = False, adults: int = 1, children: int = 0,
                     infants: int = 0):
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
            'adults': adults,
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

            # extract departure and arrival times
            departure_datetime = first_segment['departure']['at'] # full datetime
            arrival_datetime = last_segment['arrival']['at'] # full datetime
            departure_time = departure_datetime[11:16] if len(departure_datetime) > 11 else None # HH:MM
            arrival_time = arrival_datetime[11:16] if len(arrival_datetime) > 11 else None # HH:MM

            # extract layover stops (intermediate airports)
            layover_stops = []
            if transfers > 0:
                for i in range(len(segments) - 1): # exclude last segment
                    layover_stops.append(segments[i]['arrival']['iataCode'])

            # get return flight details if exists
            return_departure_time = None
            return_arrival_time = None
            return_layover_stops = []
            if return_itinerary:
                return_segments = return_itinerary['segments']
                return_departure_datetime = return_segments[0]['departure']['at']
                return_arrival_datetime = return_segments[-1]['arrival']['at']
                return_departure_time = return_departure_datetime[11:16] if len(return_departure_datetime) > 11 else None
                return_arrival_time = return_arrival_datetime[11:16] if len(return_arrival_datetime) > 11 else None

                # return flight layovers
                if return_transfers > 0:
                    for i in range(len(return_segments) - 1):
                        return_layover_stops.append(return_segments[i]['arrival']['iataCode'])

            # build skyscanner deep link
            if return_itinerary:
                # round trip format: /origin/destination/departdate/returndate
                return_date_str = return_itinerary['segments'][0]['departure']['at'][:10].replace('-', '')
                departure_date_str = first_segment['departure']['at'][:10].replace('-', '')
                link = f"https://www.skyscanner.com/transport/flights/{first_segment['departure']['iataCode']}/{last_segment['arrival']['iataCode']}/{departure_date_str}/{return_date_str}/?adults={adults}&adultsv2={adults}&cabinclass=economy&children={children}&childrenv2=&inboundaltsenabled=false&infants={infants}&outboundaltsenabled=false&preferdirects=false&ref=home&rtn=1"
            else:
                # for one way flights
                departure_date_str = first_segment['departure']['at'][:10].replace('-', '')
                link = f"https://www.skyscanner.com/transport/flights/{first_segment['departure']['iataCode']}/{last_segment['arrival']['iataCode']}/{departure_date_str}/?adults={adults}&adultsv2={adults}&cabinclass=economy&children={children}&childrenv2=&inboundaltsenabled=false&infants={infants}&outboundaltsenabled=false&preferdirects=false&ref=home&rtn=0"

            # Build result obj matching existing format
            results.append({
                "price": float(offer['price']['total']),
                "origin": first_segment['departure']['iataCode'],
                "destination": last_segment['arrival']['iataCode'],
                "depart_date": first_segment['departure']['at'][:10],  # YYYY-MM-DD
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "return_date": return_itinerary['segments'][0]['departure']['at'][:10] if return_itinerary else None,
                "return_departure_time": return_departure_time,
                "return_arrival_time": return_arrival_time,
                "airline": first_segment['carrierCode'],
                "transfers": transfers,
                "return_transfers": return_transfers,
                "layover_stops": layover_stops,
                "return_layover_stops": return_layover_stops,
                "duration": duration,
                "flight_number": f"{first_segment['carrierCode']}{first_segment['number']}",
                "link": link  # Generic booking link
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
    
def parse_duration(duration_str: str) -> str:
    """
    Parse ISO 8601 duration to minutes.
    Example: PT2H30M -> 2h 30 min
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

    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{minutes}m"

if __name__ == "__main__":
    # Tests API
    print("Testing API")
    results = prices_for_dates("LAX", "JFK", "2026-02-15", "2026-02-20", one_way=False)
    print(f"Found {len(results)} flights")
    if results:
        print(f"Cheapest: ${results[0]['price']}")