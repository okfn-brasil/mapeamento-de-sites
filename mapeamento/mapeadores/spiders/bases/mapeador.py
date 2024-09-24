import csv
import time
from pathlib import Path

import scrapy


class Mapeador(scrapy.Spider):
    territories = []

    def read_csv(self):
        file_path = (Path(__file__).parent / "../../resources/territories.csv").resolve()

        with open(file_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.territories.append(row)
        csvfile.close()

    def _print_log(self, i):
        if i % 10 == 0:
            print(
                f"[{i}/{len(self.territories)}] {time.strftime('%H:%M:%S', time.localtime())}"
            )