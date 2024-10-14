import csv
import time
import datetime
import logging

from pathlib import Path

import scrapy


class Mapeador(scrapy.Spider):
    file_path = "../../resources/territories.csv"
    territories = []
    logger = None

    def __init__(self):
        self.set_logger()       

        file = (Path(__file__).parent / self.file_path).resolve()
        with open(file, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.territories.append(row)

    def set_logger(self):
        self.logger = logging.getLogger(self.name)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] Mapeador %(name)s | %(levelname)s: %(message)s', 
                                      datefmt='%m-%d-%Y %H:%M:%S')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def get_status(self, date):
        current = datetime.date.today()
        if date.year == current.year:
            if date.month == current.month or date.month == current.month-1:
                return "atual"
        return "descontinuado"

    def show_progress(self, territory_index):
        if territory_index % 10 == 0:
            self.logger.info(f"Progress {territory_index}/{len(self.territories)}")

        