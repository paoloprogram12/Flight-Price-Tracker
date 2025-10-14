import typer
from rich import print
from datetime import date, timedelta
from api.travelpayouts import prices_for_dates, TPError

app = typer.Typer()

@app.command()
def track(origin: str = "LAX", dest: str = "NRT", days_from: int = 30, days_to: int = 60):
    depart_from = (date.today() + timedelta(days=days_from)).strftime("%Y-%m-%d")
    depart_to = (date.today() + timedelta(days=days_to)).strftime("%Y-%m-%d")
    return_from = (date.today() + timedelta(days=days_from+5)).strftime("%Y-%m-%d")
    return_to = (date.today() + timedelta(days=days_to+10)).strftime("%Y-%m-%d")

    print(f"[cyan]Fetching deals from {origin} -> {dest}...[/cyan]")
    deals = prices_for_dates(origin, date, depart_from, depart_to, return_from, return_to)

    if not deals:
        print("[yellow]No deals found.[/yellow]")
        raise typer.Exit()
    
    for d in sorted(deals, key=lambda x: x['price'])[:10]:
        print(f"[bold green]{d['price']} USD[/bold green] • {origin} -> {dest} "
              f"({['depart_date']} -> {d['return_date']}) • "
              f"Airline: {d['airline'] or '-'} • Stops: {d['changes']}")
        print()
