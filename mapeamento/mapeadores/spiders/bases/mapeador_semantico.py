import scrapy

from slugify import slugify
from urllib.parse import urlparse, urlunparse

from mapeadores.spiders.bases.mapeador import Mapeador
from mapeadores.items import MapeamentoItem

class MapeadorSemantico(Mapeador):
    replacements = [("´", ""), ("`", ""), ("'", "")]
    stopwords = ["d", "da", "de", "do", "das", "dos"]

    custom_settings = {
        "RETRY_ENABLED": False,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 200,
    }

    def start_requests(self):
        print(f"------- COMEÇANDO MAPEAMENTO DE {self.name} -------")
        
        for i in range(len(self.territories)):
            self._print_log(i)

            item = {
                "territory_id": self.territories[i]['id'],
                "city": self.territories[i]['name'],
                "state": self.territories[i]["state_code"],
                "pattern": self.name,
            }

            for url_option in self.generate_combinations(item["city"], item["state"]):
                yield scrapy.Request(
                    url_option, 
                    callback=self.parse, 
                    cb_kwargs={"item": item}
                )

    def generate_combinations(self, name, state_code):
        schemes = ["http", "https"]
        url_combinations = set()

        for pattern in self.url_patterns:

            pattern = pattern.replace("uf", state_code) 
            parsed_url = urlparse(pattern)

            if "municipio" in parsed_url.hostname:

                for scheme in schemes:
                    for option in self.domain_generator(name):
                        hostname = parsed_url.hostname.replace("municipio", option)
                        url = urlunparse(parsed_url._replace(scheme=scheme, netloc=hostname))
                        url_combinations.add(url)

            elif "municipio" in parsed_url.path:

                for scheme in schemes:
                    for option in self.path_generator(name):
                        path = parsed_url.path.replace("municipio", option)
                        url = urlunparse(parsed_url._replace(scheme=scheme, path=path))
                        url_combinations.add(url)

            else: 
                print("erro") # colocar no log

        return url_combinations

    def InvalidItem(self, item, url):
        item["url"] = url
        item["status"] = "invalido"
        item["date_from"] = ""
        item["date_to"] = ""
        return item
                         
    def domain_generator(self, city):
        """
        special characters aren't allowed in domains
        """ 
        combinations = set()

        for name in self.add_prefeitura_to_name(city):
            combinations.add(self.no_blankspaces(name))           # cityname      
            combinations.add(self.abbreviated(name))              # cn
            combinations.update(self.name_parts_set(name))        # city | name
        
        return combinations


    def path_generator(self, city):
        """
        same as domain_generator(), but special characters are allowed
        """
        combinations = self.domain_generator(city)

        for name in self.add_prefeitura_to_name(city):
            combinations.add(self.name_with_underline(name))    # city_name
            combinations.add(self.name_with_hifen(name))        # city-name

        return combinations

    def add_prefeitura_to_name(self, name):
        return [
            name,
            f"prefeitura {name}",
            f"prefeitura de {name}",
            f"prefeitura municipal {name}",
            f"prefeitura municipal de {name}",
        ]
    
    def no_blankspaces(self, name): 
        return slugify(name, separator="", replacements=self.replacements)

    def name_with_underline(self, name): 
        return slugify(name, separator="_", replacements=self.replacements)

    def name_with_hifen(self, name): 
        return slugify(name, separator="-", replacements=self.replacements)

    def name_parts_set(self, name): 
        stopwords = self.stopwords + ["prefeitura", "municipal"]
        return set(slugify(name, separator="-", replacements=self.replacements, stopwords=stopwords).split("-"))

    def abbreviated(self, name):
        abbrev = ""
        for n in slugify(name, separator="-", replacements=self.replacements, stopwords=self.stopwords).split("-"):
            abbrev += n[0]
        return abbrev