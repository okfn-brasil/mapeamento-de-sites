import scrapy

from unidecode import unidecode

from mapeadores.spiders.bases.mapeador import Mapeador

class MapeadorSemantico(Mapeador):
    custom_settings = {
        "RETRY_ENABLED": False,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 100,
    }

    def start_requests(self):
        self._read_data()        

        for i in range(len(self.territories)):
            self._print_log(i)

            name = self._normalize_str(self.territories[i]["name"])
            state_code = self._normalize_str(self.territories[i]["state_code"])

            item = {
                "territory_id": self.territories[i]['id'],
                "city": self.territories[i]['name'],
                "state": state_code,
            }

            for protocol_option in ["http", "https"]:
                for name_option in self.domain_generator(name):                    
                    for url_option in self.urls_pattern(protocol_option, name_option, state_code):
                        yield scrapy.Request(
                            url_option, 
                            callback=self.parse, 
                            cb_kwargs={"item": item}
                        )

    def _read_data(self):
        print(f"------- COMEÇANDO MAPEAMENTO DE {self.pattern_name()} -------")
        self.read_csv() 

    def _normalize_str(self, string):
        string = (
            unidecode(string).strip().lower().replace("-", " ").replace("'", "")
        )
        return string

    # COMBINATIONS

    def domain_generator(self, name):
        # strings
        cityname = self.remove_blankspaces(name)             # cityname
        city_name = self.blankspaces_to_underline(name)      # city_name
        hifen_city_name = self.blankspaces_to_hifen(name)    # city-name
        abbrev = self.name_abbreviation(name)                # cn 
        
        # lists
        combination_list = [
            cityname,
            city_name,
            hifen_city_name,
            abbrev,
        ]

        name_parts = self.name_parts(name)                   # city | name
        starts_with_prefeitura = self.add_prefeitura_to_names(combination_list) # pm/prefeitura + all
        combination_list += name_parts + starts_with_prefeitura

        return combination_list

    # DOMAIN FORMATS

    def remove_blankspaces(self, name): 
        # cityname
        return name.replace(" ", "")

    def blankspaces_to_underline(self, name): 
        # city_name
        return name.replace(" ", "_")

    def blankspaces_to_hifen(self, name): 
        # city-name
        return name.replace(" ", "-")

    def name_abbreviation(self, city_name): 
        # cn 
        subnames = city_name.split()
        abbrev = ""
        for n in subnames:
            if n not in ["da", "de", "do"]:
                abbrev += n[0]
        return abbrev

    def name_parts(self, name): 
        # city | name
        name = name.replace(" da ", " ").replace(" de ", " ").replace(" do ", " ")
        return name.split()

    def add_prefeitura_to_names(self, list_names): 
        # prefeitura + all
        aux = []
        for name in list_names:
            aux.append(f"pm{name}")         # pm: prefeitura municipal
            aux.append(f"prefeitura{name}")
            aux.append(f"prefeiturade{name}")
        return aux
