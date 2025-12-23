from datetime import date, timedelta
from api.travelpayouts import prices_for_dates, TOKEN # imports api function and token (prices_for_dates = searches flights) (TOKEN API key from .env)

def main():
    # test cities
    origin = "LAX" 
    dest = "TYO"  # use TYO instead of NRT to test city code
    days_ahead = 30 # used to search for flights 30 days from today

    # Use month format for more flexible results
    depart_month = (date.today() + timedelta(days=days_ahead)).strftime("%Y-%m") # adds 30 days from days today, format as month only
    return_month = (date.today() + timedelta(days=days_ahead + 7)).strftime("%Y-%m") # adds 37 days (30 + 1 week) from today, format as month only

    print(f"🌐 Fetching {origin}→{dest} | depart: {depart_month}, return: {return_month}") # shows what you're searching

    # calls API with search criteria
    # one_way = False (round-trip flights only)
    # currency = USD (searches for USD prices)
    deals = prices_for_dates(origin, dest, departure_at=depart_month, return_at=return_month, one_way=False, currency="USD")
    print(f"📦 Received {len(deals)} deals\n")

# handles empty results (if there's no flights)
    if not deals:
        print("❌ No deals found")
        return

    # Show top 10 cheapest deals
    print("Top 10 Cheapest Flights:")
    print("-" * 80)

    # Convert RUB to USD (API returns prices in Russian Rubles)
    RUB_TO_USD = 0.011  # Approximate exchange rate: 1 RUB ≈ $0.011

    # searches for 10 cheapest deals
    # key= means what to sort by
    # lambda x means "Take x and return the price of x"
    # :10 means to sort only 10 lowest
    for d in sorted(deals, key=lambda x: x['price'])[:10]: # sorts by prices (lowest first)
        usd_price = d['price'] * RUB_TO_USD  # Convert RUB to USD
        print(f"  ${usd_price:.2f} • {d['origin']}→{d['destination']} "
              f"({d['depart_date'][:10]} → {d['return_date'][:10]}) • " # :10 takes the first 10 characters "2026-01-19T09:35:00-08:00" -> "2026-01-19"
              f"airline:{d.get('airline') or '—'} • stops:{d.get('transfers')}")

if __name__ == "__main__":
    print("🔧 __main__ hit")
    main()