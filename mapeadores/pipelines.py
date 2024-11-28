# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter
from scrapy.exceptions import DropItem


class FilterAndExportPipeline:
    """Filtra itens repetidos e os salva, em arquivos CSV, por status."""
    
    def open_spider(self, spider):
        self.today = datetime.today().strftime('%Y%m%d')
        self.data_dir = spider.settings.get("DATA_OUTPUT_DIR")
        
        self.status_codes = {}
        self.valid_entries = set()
        self.invalid_entries = set()

    def close_spider(self, spider):
        for exporter, csv_file in self.status_codes.values():
            exporter.finish_exporting()
            csv_file.close()

    def exporter_for_item(self, adapter):
        """Cria exportadores CSV para cada status.

        Os status possiveis sao: validos ou invalidos.
        """
        status = adapter["status"]

        if status not in self.status_codes:
            fn = self._file_name(status, adapter["pattern"])
            csv_file = open(f"{fn}.csv", "wb+")
            exporter = CsvItemExporter(csv_file)
            exporter.start_exporting()
            self.status_codes[status] = (exporter, csv_file)

        return self.status_codes[status][0]

    def _file_name(self, status, pattern):        
        if status == "invalido":
            return f"{self.data_dir}/{self.today}_{pattern}_invalidos"
        return f"{self.data_dir}/{self.today}_{pattern}_validos"

    def item_exists(self, adapter):
        """Verifica existencia de itens repetidos. 

        Para a verificacao, considera:
        - id: criterio de unico, dado no padrao 0000000AAAA-MM-DDhttp...
        - valid_entries: armazena ids de itens validos
        - invalid_entries: armazena ids de itens invalidos
        """
        id = f'{adapter["territory_id"]}{adapter["date_from"]}{adapter["url"]}'

        if adapter["status"] == "invalido":
            if id in self.invalid_entries:
                return True
            else:
                self.invalid_entries.add(id)
                return False

        if id in self.valid_entries:
            return True
        else:
            self.valid_entries.add(id)
            return False

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if self.item_exists(adapter):
            raise DropItem("Dropping duplicated item")

        exporter = self.exporter_for_item(adapter)
        exporter.export_item(item)
        return item

