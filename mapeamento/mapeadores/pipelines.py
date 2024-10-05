# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter
from scrapy.exceptions import DropItem


class FilterAndExportPipeline:
    """
    Filter repeated itens and distribute them across multiple CSV files according 
    to their 'status' field
    """
    
    def open_spider(self, spider):
        self.status_codes = {}
        self.valid_entries = set()
        self.invalid_entries = set()

    def close_spider(self, spider):
        for exporter, csv_file in self.status_codes.values():
            exporter.finish_exporting()
            csv_file.close()

    def _exporter_for_item(self, adapter):
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
            return f"../resultados/invalidos/{pattern}_invalidos"
        return f"../resultados/validos/{pattern}_validos"

    def _item_exists(self, adapter):
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

        if self._item_exists(adapter):
            raise DropItem("Dropping duplicated item")

        exporter = self._exporter_for_item(adapter)
        exporter.export_item(item)
        return item

