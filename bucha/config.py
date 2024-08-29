from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, kw_only=True)
class Config:
    outputs_dir: Path = Path().parent / "out"
    assets_dir: Path = Path().parent / "assets"
    menus_dir: Path = outputs_dir / "menus"
    logs_dir: Path = outputs_dir / "logs"
    scraper_logs_dir: Path = logs_dir / "scraper"
    slack_bot_logs_dir: Path = logs_dir / "slack_bot"

    default_driver_wait_timeout: int = 20


config = Config()
