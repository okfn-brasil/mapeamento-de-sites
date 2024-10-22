import datetime

import scrapy


from mapeadores.spiders.bases.mapeador_semantico import MapeadorSemantico
from mapeadores.items import MapeamentoItem


class MapeadorAdiariosV1(MapeadorSemantico):
    name = "adiarios_v1"
    
    """
    Cases
    https://www.buriticupu.ma.gov.br/diariooficial.php
    https://www.anajatuba.ma.gov.br/diariooficial.php
    """

    url_patterns = [
        "https://www.city_name.state_code.gov.br/diariooficial.php",
    ]

    def parse(self, response, item):
        if self.belongs_to_pattern(response):
            date_to = self.get_date(response, 0)
            item["url"] = response.url
            item["date_to"] = date_to
            item["status"] = self.get_status(date_to)

            yield scrapy.Request(
                f"{response.url}?pagina={self.get_last_page(response)}", 
                callback=self.parse_last_page,
                cb_kwargs={"item": item},
            )

        else:
            yield MapeamentoItem(
                **self.InvalidItem(item, response.url),
            )    

    def parse_last_page(self, response, item):  
        yield MapeamentoItem(
            **item,
            date_from = self.get_date(response, -1),
        )

    def belongs_to_pattern(self, response):
        if (
            "assesi.com.br" in response.text
            or "siasp.com.br" in response.text
            or len(response.xpath('//*[@class="public_paginas"]').getall()) > 0
        ):
            if "Foram encontrados 0 registros" not in response.text:
                return True
        return False

    def get_last_page(self, response):
        page_pagination = response.css(".pagination li a span::text").getall()
        page_numbers = [int(i) for i in page_pagination]
        last_page_index = max(page_numbers)
        return last_page_index-1

    def get_date(self, response, position):
        raw = response.css("#diario_lista")[position].css(".calendarioIcon::text").get().strip()
        return datetime.datetime.strptime(raw, "%d/%m/%Y").date()
        

