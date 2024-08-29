import csv
from dataclasses import asdict, dataclass

from config import config
from logger import logger


@dataclass(kw_only=True, frozen=True)
class Restaurant:
    account_id: str
    alias: str
    scraping_mode: str
    emoji: str
    daily_price: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(kw_only=True)
class Menu:
    display_name: str
    body: str | None = None
    img_path: str | None = None

    def __init__(self, restaurant: Restaurant):
        self.display_name = (
            f"{restaurant.emoji} - {restaurant.alias} [{restaurant.daily_price} Eur]"
        )

    def __str__(self) -> str:
        return f"*{self.display_name}*\n{self.body if self.body else self.img_path}\n"

    def to_dict(self) -> dict:
        return asdict(self)


def load_restaurants() -> list[Restaurant]:
    restaurants: list[Restaurant] = []
    path = config.assets_dir / "restaurants.csv"
    logger.info(f"Loading restaurants from {path}...")
    try:
        with open(path, newline="") as f:
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
    except Exception as e:
        logger.error(f"Something went wrong when reading {path}: {e}")
        return []

    logger.info("Done.")
    return restaurants
