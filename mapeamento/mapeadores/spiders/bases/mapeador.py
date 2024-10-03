import csv
import time
import datetime

from pathlib import Path

import scrapy


class Mapeador(scrapy.Spider):
    territories = []

    def __init__(self):
        file_path = (Path(__file__).parent / "../../resources/territories.csv").resolve()

        with open(file_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.territories.append(row)

    def get_status(self, date):
        current = datetime.date.today()
        if date.year == current.year:
            if date.month == current.month or date.month == current.month-1:
                return "atual"
        return "descontinuado"

    def _print_log(self, i):
        if i % 10 == 0:
            print(
                f"[{i}/{len(self.territories)}] {time.strftime('%H:%M:%S', time.localtime())}"
            )