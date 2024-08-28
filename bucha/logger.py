import logging
from datetime import datetime

from config import config

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M",
    filename=config.scraper_logs_dir / f"{int(datetime.timestamp(datetime.now()))}.log",
    filemode="w",
)
logger = logging.getLogger()
