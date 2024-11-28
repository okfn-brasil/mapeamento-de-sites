import csv
import logging

from pathlib import Path

import scrapy

class Mapeador(scrapy.Spider):
    file_path = "../../resources/territories.csv"
    territories = []
    oldest_year_to_map = 1950

    def __init__(self):
        self.set_logger()       

        file = (Path(__file__).parent / self.file_path).resolve()
        with open(file, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.territories.append(row)

    def set_logger(self):
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] Mapeador %(name)s | %(levelname)s: %(message)s', 
                                      datefmt='%m-%d-%Y %H:%M:%S')
        ch.setFormatter(formatter)
        self.logger.logger.addHandler(ch)

    def show_progress(self, territory_index):
        if territory_index % 10 == 0:
            self.logger.info(f"Progresso {territory_index}/{len(self.territories)}")

    def make_invalid_item(self, item, url):
        item["url"] = url
        item["status"] = "invalido"
        item["date_from"] = ""
        item["date_to"] = ""
        return item