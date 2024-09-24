import datetime

import scrapy

from mapeadores.spiders.bases.mapeador_semantico import MapeadorSemantico
from mapeadores.items import MapeamentoItem

class MapeadorAdiarioV1(MapeadorSemantico):
    name = "mapeador_adiariov1"

    def pattern_name(self):
        return "ADIARIOS_v1"

    def urls_pattern(self, protocol, city, state_code):
        # examples
        # https://www.buriticupu.ma.gov.br/diariooficial.php
        # https://www.anajatuba.ma.gov.br/diariooficial.php

        return [
            f"{protocol}://www.{city}.{state_code}.gov.br/diariooficial.php",
        ]

    def domain_generator(self, name):

        cityname = self.remove_blankspaces(name)             # cityname
        abbrev = self.name_abbreviation(name)                # cn 
        
        combination_list = [
            cityname,
            abbrev,
        ]

        name_parts = self.name_parts(name)                   # city | name
        starts_with_prefeitura = self.add_prefeitura_to_names(combination_list) # pm/prefeitura + all
        combination_list += name_parts + starts_with_prefeitura

        return combination_list
    
    def parse(self, response, item):
        if self._belongs_to_pattern(response):
            item["pattern"] = self.pattern_name()
            item["url"] = response.url
            item["date_to"] = self._get_date(response, 0)
            item["status"] = self._get_status(item["date_to"])

            yield scrapy.Request(
                f"{response.url}?pagina={self._get_last_page(response)}", 
                callback=self.parse_last_page,
                cb_kwargs={"item": item},
            )

        else:
            yield MapeamentoItem(
                **item,
                pattern = "",
                url = "",
                status = "inválido",
                date_from = "",
                date_to = "",
            )

    def parse_last_page(self, response, item):
            yield MapeamentoItem(
                **item,
                date_from = self._get_date(response, -1),
            )

    def _belongs_to_pattern(self, response):
        if (
            "assesi.com.br" in response.text
            or "siasp.com.br" in response.text
            or len(response.xpath('//*[@class="public_paginas"]').getall()) > 0
        ):
            if "Foram encontrados 0 registros" not in response.text:
                return True
        return False

    def _get_last_page(self, response):
        page_pagination = response.css(".pagination li a span::text").getall()
        page_numbers = [int(i) for i in page_pagination]
        last_page_index = max(page_numbers)
        return last_page_index-1

    def _get_date(self, response, position):
        raw = response.css("#diario_lista")[position].css(".calendarioIcon::text").get().strip()
        return datetime.datetime.strptime(raw, "%d/%m/%Y").date()
        
    def _get_status(self, date):
        current = datetime.date.today()
        if date.year == current.year:
            if date.month == current.month or date.month == current.month-1:
                return "atual"
        return "descontinuado"
