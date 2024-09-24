import datetime

import scrapy

from mapeadores.spiders.bases.mapeador_semantico import MapeadorSemantico
from mapeadores.items import MapeamentoItem

class MapeadorNOME(MapeadorSemantico):
    name = "mapeador_NOME"

    def pattern_name(self):
        return "NOME"

    def urls_pattern(self, protocol, city, state_code):
        # examples
        # 
        # ... URLs conhecidas que fazem parte do padrão

        return [
            f"...",
        ]

    def domain_generator(self, name):
        # em MapeadorSemantico este método é implementado de forma completa
        # mas nem sempre faz sentido usar todas as combinações possiveis

        pass

    
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

        # poderia não existir já que não é de maior interesse guardar o que não 
        # foi compatível
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
        # só pq certa URL tentada existe (response 200), não significa que 
        # o layout da página é o do padrão sendo investigado 

        # ... adicionar lógica de verificação
        # retorna booleano
        pass

    def _get_last_page(self, response):
        # lógica para ir direto para a última página
        # não é necessário iterar todas as páginas
        pass

    def _get_date(self, response, position):
        # método pensado para servir para as 2 datas de interesse, a mais antiga e a mais atual
        # position 0: coleta data mais atual, na primeira pagina
        # position -1: coleta data mais antiga, na última pagina
        #  
        pass
        
    def _get_status(self, date):
        # a partir da data mais recente que consta no site, classifica a URL
        
        # site atual: se data for deste mês ou mês passado
        # site descontinuado: se a data for anterior

        current = datetime.date.today()
        if date.year == current.year:
            if date.month == current.month or date.month == current.month-1:
                return "atual"
        return "descontinuado"
