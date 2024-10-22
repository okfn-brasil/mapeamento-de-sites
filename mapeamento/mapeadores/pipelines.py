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
    Filter repeated itens and distribute them across multiple CSV
    files according to their 'status' field
    """
    data_dir = "../resultados"
    
    def open_spider(self, spider):
        self.status_codes = {}
        self.valid_entries = set()
        self.invalid_entries = set()

    def close_spider(self, spider):
        for exporter, csv_file in self.status_codes.values():
            exporter.finish_exporting()
            csv_file.close()

    def exporter_for_item(self, adapter):
        """
        Creates CSV exporter per site status group
        - group invalidos: receives invalido status
        - group validos: receives atual and descontinuado status
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
            return f"{self.data_dir}/{pattern}_invalidos"
        return f"{self.data_dir}/{pattern}_validos"

    def item_exists(self, adapter):
        """
        Check if item already exists considering 
        - id as uniqueness criteria, like 0000000YYYY-MM-DDhttp...
        - comparison to valid_entries and invalid_entries, where 
        unique ids are kept
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

