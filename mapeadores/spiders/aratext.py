import scrapy
from dateparser import parse

from mapeadores.spiders.bases.mapeador_semantico import MapeadorSemantico
from mapeadores.items import MapeamentoItem


class MapeadorAratext(MapeadorSemantico):   
    """Mapeia o padrao aratext

    Exemplos:
    https://centrodoguilherme.ma.gov.br/diariooficial
    https://maranhaozinho.ma.gov.br/diariooficial
    """
    name = "aratext"

    url_patterns = [
        "https://nome_do_municipio.UF.gov.br/diariooficial",
    ]

    def parse(self, response, item):            
        if self.belongs_to_pattern(response):   
            item["url"] = response.url
            item["status"] = "valido"
            item["date_to"] = self.get_date(response, 2)            

            yield scrapy.Request(
                f"{response.url}?page={self.get_last_page_index(response)}", 
                callback=self.parse_last_page,
                cb_kwargs={"item": item},
            )
        
        else:                                   
            yield MapeamentoItem(
                **self.make_invalid_item(item, response.url),
            )

    def parse_last_page(self, response, item):
        yield MapeamentoItem(
            **item,
            date_from = self.get_date(response, -1)
        )

    def belongs_to_pattern(self, response):
        if "ara-text-materia row" in response.text:
            return True
        return False
    
    def get_last_page_index(self, response):
        page_pagination = response.css(".pagination .page-link::text").getall()
        page_pagination.remove('‹')
        page_pagination.remove('›')

        page_numbers = [int(i.strip()) for i in page_pagination]
        last_page_index = max(page_numbers)
        return last_page_index

    def get_date(self, response, position):
        rawdate = response.css("table tbody tr td")[position].css("::text").get()
        return parse(rawdate, languages=["pt"]).date()