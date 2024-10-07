# mapeamento-de-sites
Repositório auxiliar para encontrar sites de prefeituras ou sites publicadores de diários oficiais


## Modelo de mapeador 
``` python
import scrapy

from mapeadores.spiders.bases.mapeador_<tipo> import Mapeador<tipo>
from mapeadores.items import MapeamentoItem

class Mapeador<nome>(Mapeador<tipo>):
    name = "<nome>"
    
    """
    Cases
    exemplo 1
    exemplo 2
    """
    # deve ter o termo "municipio" e "uf" nas partes generalizáveis
    url_patterns = [
        "",
    ]

    def parse(self, response, item):
        if self.belongs_to_pattern(response):
            # provavelmente a data mais recente já está na página
            date_to = self.get_date(response, 0)
            item["url"] = response.url
            item["date_to"] = date_to
            item["status"] = self.get_status(date_to)

            # lógica para buscar a data mais antiga

        else:
            yield MapeamentoItem(
                **self.InvalidItem(item, response.url),
            )    

    def belongs_to_pattern(self, response):
        if #condições para se validar que a página é do padrão de interesse
            return True
        return False

    def get_date(self, response, position):
        #lógica para coletar data
        return date
```