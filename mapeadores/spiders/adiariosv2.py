import datetime

import scrapy


from mapeadores.spiders.bases.mapeador_semantico import MapeadorSemantico
from mapeadores.items import MapeamentoItem


class MapeadorAdiariosV2(MapeadorSemantico):
    """Mapeia o padrao adiariosv2

    Exemplos:
    # https://buzios.aexecutivo.com.br/jornal.php
    https://www.transparencia.casimirodeabreu.rj.gov.br/jornal.php
    # https://portal.iguaba.rj.gov.br/jornal.php
    """
    name = "adiariosv2"

    url_patterns = [
        "https://nome_do_municipio.aexecutivo.com.br/jornal.php",
        "https://www.transparencia.nome_do_municipio.UF.gov.br/jornal.php",
        "https://portal.nome_do_municipio.UF.gov.br/jornal.php",
    ]

    def parse(self, response, item):
        if self.belongs_to_pattern(response):
            item["url"] = response.url
            item["status"] = "valido"

            date_to = self.get_date(response, 1)
            item["date_to"] = date_to

            yield scrapy.Request(
                f"{response.url}?pagina={self.get_last_page(response)}", 
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
            date_from = self.get_date(response, -1),
        )

    def belongs_to_pattern(self, response):
        if "table-condensed table-bordered" in response.text:
            if len(response.xpath('//*[@class="public_paginas"]').getall()) > 0:
                if "Foram encontrados 0 registros" not in response.text:
                    return True
        return False

    def get_last_page(self, response):
        page_pagination = response.css(".pagination li a span::text").getall()
        page_numbers = [int(i.strip()) for i in page_pagination]
        last_page_index = max(page_numbers)
        return last_page_index-1

    def get_date(self, response, position):
        raw = response.css("table tr")[position].css("td::text").get().strip()
        return datetime.datetime.strptime(raw, "%d/%m/%Y").date()
        

