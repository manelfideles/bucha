import csv
from dataclasses import asdict, dataclass


@dataclass(kw_only=True, frozen=True)
class Restaurant:
    account_id: str
    alias: str
    scraping_mode: str
    emoji: str
    daily_price: float

    def to_dict(self) -> dict:
        return asdict(self)


def load_restaurants() -> list[Restaurant]:
    restaurants: list[Restaurant] = []
    with open("restaurants.csv", newline="") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader, None)
        for row in reader:
            restaurants.append(
                Restaurant(
                    account_id=row[0],
                    alias=row[1],
                    scraping_mode=row[2],
                    emoji=row[3],
                    daily_price=row[4],
                )
            )
    return restaurants


restaurants = load_restaurants()
