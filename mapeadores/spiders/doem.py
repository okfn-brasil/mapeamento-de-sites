import datetime
import dateparser

import scrapy

from mapeadores.spiders.bases.mapeador_semantico import MapeadorSemantico
from mapeadores.items import MapeamentoItem


class MapeadorDoem(MapeadorSemantico):   
    """Mapeia o padrao doem

    Exemplos:
    https://doem.org.br/ba/acajutiba/diarios
    https://doem.org.br/ba/mascote/diarios
    """
    name = "doem"

    url_patterns = [
        "https://doem.org.br/UF/nome_do_municipio/diarios",
    ]

    def parse(self, response, item):
        if self.belongs_to_pattern(response):
            item["url"] = response.url
            item["status"] = "valido"

            current = datetime.date.today()
            for year in range(self.oldest_year_to_map, current.year+1):
                for month in range (1,current.month+1):
                    yield scrapy.Request(
                        f"{response.url}/{year}/{month}",
                        callback=self.parse_page,
                        cb_kwargs={"item":item}
                    )

        # Itens invalidos DOEM sao ignorados ao invés de salvos. 
        # Por ser um padrao de um servico privado, todos os itens invalidos sao
        # como https://doem.org.br/ba/vereda/diarios, coisa que nao serve para
        # encontrar outros sites de prefeituras

    def parse_page(self, response, item):
        date_to = self.get_date(response, 0)

        yield MapeamentoItem(
            **item,
            date_to = date_to,
            date_from = self.get_date(response, -1),
        )

    def belongs_to_pattern(self, response):
        if all([
           "doem.org.br" in response.text,
           "está Indisponível" not in response.text,
           "Não foi possível carregar o diário" not in response.text,
           "404 - Página não encontrada" not in response.text,
           "ibdm.org.br" not in response.url,
        ]):
            return True
        return False

    def get_date(self, response, position):
        raw = response.css('span.data-diario.pull-right::text')[position].get().strip()
        date = dateparser.parse(raw, languages=["pt"]).date()
        return date