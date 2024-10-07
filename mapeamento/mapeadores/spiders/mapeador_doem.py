import datetime
import dateparser

import scrapy

from mapeadores.spiders.bases.mapeador_semantico import MapeadorSemantico
from mapeadores.items import MapeamentoItem


class MapeadorDoem(MapeadorSemantico):
    name = "doem"
    oldest_date = None
    
    """
    Cases
    https://doem.org.br/ba/acajutiba/diarios
    https://doem.org.br/ba/mascote/diarios
    """

    url_patterns = [
        "https://doem.org.br/state_code/city_name/diarios",
    ]

    def parse(self, response, item):
        if self.belongs_to_pattern(response):
            date_to = self.get_date(response, 0)
            item["url"] = response.url
            item["date_to"] = date_to
            item["status"] = self.get_status(date_to)

            self.oldest_date = date_to          

            current = datetime.date.today()
            for year in range(2000, current.year+1):
                for month in range (1,current.month+1):
                    yield scrapy.Request(
                        f"{response.url}/{year}/{month}",
                        callback=self.parse_page,
                        cb_kwargs={"item":item}
                    )            
        else:
            yield MapeamentoItem(
                **self.InvalidItem(item, response.url),
            )    

    def parse_page(self, response, item):
        page_oldest_date = self.get_date(response, -1)

        if page_oldest_date < self.oldest_date:
            self.oldest_date = page_oldest_date
        
            yield MapeamentoItem(
                **item,
                date_from = self.oldest_date,
            )

    def belongs_to_pattern(self, response):
        if "doem.org.br" in response.text:
            if "está Indisponível" not in response.text:
                if "Não foi possível carregar o diário" not in response.text:
                    if "404 - Página não encontrada" not in response.text:
                        if "ibdm.org.br" not in response.url:
                            return True
        return False

    def get_date(self, response, position):
        raw = response.css('span.data-diario.pull-right::text')[position].get().strip()
        date = dateparser.parse(raw, languages=["pt"]).date()
        return date