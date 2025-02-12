import scrapy
import re 
import json
from dateutil.rrule import MONTHLY, rrule
from datetime import date

from mapeadores.spiders.bases.mapeador_semantico import MapeadorSemantico
from mapeadores.items import MapeamentoItem


class MapeadorDosp(MapeadorSemantico):   
    """Mapeia o padrao Dosp

    Exemplos:
    https://imprensaoficialmunicipal.com.br/adolfo
    https://imprensaoficialmunicipal.com.br/guaracai
    """
    name = "dosp"

    url_patterns = [
        "https://www.imprensaoficialmunicipal.com.br/nome_do_municipio",
    ]

    def parse(self, response, item):            
        if self.belongs_to_pattern(response):          
            code = re.search(r"https://dosp.com.br/api/index.php/'\+urlapi\+'.js/(\d*)/'\+idsecao\+'\?callback=dioe'", response.text).group(1)
            
            today = date.today()
            dates = list(rrule(freq=MONTHLY, 
                               interval=6, 
                               dtstart=date(self.oldest_year_to_map, 1, 1), 
                               until=today
                            ))
            dates.append(today)

            for i in range(len(dates)-1):
                date_from = dates[i].strftime("%Y-%m-%d")
                date_to = dates[i+1].strftime("%Y-%m-%d")

                yield scrapy.Request(
                    f"https://dosp.com.br/api/index.php/dioedata.js/{code}/{date_from}/{date_to}?callback=dioe",
                    callback=self.parse_response,
                    cb_kwargs={
                        "item": item,
                        "url": response.url
                    }
                )        
        
        # Itens invalidos DOSP sao ignorados ao invés de salvos. 
        # Por ser um padrao de um servico privado, todos os itens invalidos sao
        # como https://dosp.org.br/, coisa que nao serve para encontrar outros 
        # sites de prefeituras

    def belongs_to_pattern(self, response):
        if "dosp.com.br" in response.text:
            if "FILTRO POR DATA" in response.text:
                return True
        return False

    def parse_response(self, response, item, url):
        itens = json.loads(response.text[6:-2])['data']
        yield MapeamentoItem(
            **item,
            status = "valido",
            date_from = itens[-1]['data'],
            date_to = itens[0]['data'],
            url = url,
        )