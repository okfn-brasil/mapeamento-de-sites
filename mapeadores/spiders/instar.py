import scrapy
import re
from datetime import date

from mapeadores.spiders.bases.mapeador_semantico import MapeadorSemantico
from mapeadores.items import MapeamentoItem


class MapeadorInstar(MapeadorSemantico):   
    """Mapeia o padrao Instar

    Exemplos:
    https://www.montealto.instaridc.com.br/portal/diario-oficial
    https://www.ibitinga.instarbr.com.br/portal/diario-oficial
    https://www.prefeituradecrucilandia.mg.gov.br/portal/diario-oficial
    https://web.santoandre.sp.gov.br/portal/diario-oficial
    https://portal.contagem.mg.gov.br/portal/diario-oficial
    """
    name = "instar"

    url_patterns = [
        "https://www.nome_do_municipio.instaridc.com.br/portal/diario-oficial",
        "https://www.nome_do_municipio.instarbr.com.br/portal/diario-oficial",
        "https://www.nome_do_municipio.UF.gov.br/portal/diario-oficial", # com www
        "https://web.nome_do_municipio.UF.gov.br/portal/diario-oficial", # com web
        "https://portal.nome_do_municipio.UF.gov.br/portal/diario-oficial", # com portal
    ]

    def parse(self, response, item):   
        if self.belongs_to_pattern(response):
            item["url"] = response.url
            item["status"] = "valido"
            item["date_to"] = self.get_date(response, 0)
            
            yield scrapy.Request(
                response.url + self.get_last_page_url(response), 
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
        if "Instar Tecnologia" in response.text or "instar.com.br" in response.text:
            if "Nenhum diário oficial encontrado" not in response.text:
                if "dof_publicacao_diario" in response.text:
                    return True
        return False

    def get_last_page_url(self, response):
        path = response.css(".sw_cont_paginacao.sw_txt_tooltip a::attr(href)").getall()[-1]
        return path.replace("/portal/diario-oficial", "")

    def get_date(self, response, position):
        rawdate = response.css(".dof_cont_info_publicacao_diario.sw_bg_info_listagem")[position]
        rawdate = rawdate.css(".sw_descricao_info span::text").get()
        rawdate = re.search(r'(\d{2})/(\d{2})/(\d{4})', rawdate)

        if rawdate is None:
            return "Edição com data ausente"

        day = int(rawdate.group(1))
        month = int(rawdate.group(2))
        year = int(rawdate.group(3))
        return date(year, month, day)