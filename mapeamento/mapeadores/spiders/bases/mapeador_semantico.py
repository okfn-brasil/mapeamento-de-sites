import scrapy

from slugify import slugify
from urllib.parse import urlparse, urlunparse

from mapeadores.spiders.bases.mapeador import Mapeador

class MapeadorSemantico(Mapeador):
    replacements = [("´", ""), ("`", ""), ("'", "")]
    stopwords = ["d", "da", "de", "do", "das", "dos", "e"]

    custom_settings = {
        "RETRY_ENABLED": False,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 200,
    }

    def start_requests(self):        
        for i, territory in enumerate(self.territories):
            self.show_progress(i)

            item = {
                "territory_id": territory['id'],
                "city": territory['name'],
                "state": territory["state_code"],
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
            pattern = pattern.replace("state_code", state_code) 
            parsed_url = urlparse(pattern)

            """
            It creates combinations depending on the context. If the 
            generalization "city_name"...
            - is in the hostname, combinations are more restricted 
            - is in the path, combinations are freer
            """
            if "city_name" in parsed_url.hostname:
                for scheme in schemes:
                    for option in self.domain_generator(name):
                        hostname = parsed_url.hostname.replace("city_name", option)
                        url = urlunparse(parsed_url._replace(scheme=scheme, netloc=hostname))
                        url_combinations.add(url)

            elif "city_name" in parsed_url.path:
                for scheme in schemes:
                    for option in self.path_generator(name):
                        path = parsed_url.path.replace("city_name", option)
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
            combinations.add(self.name_no_blankspaces(name))          
            combinations.update(self.name_parts_set(name))        
            combinations.update(self.progressive_colapsed_words_set(name))
        
        combinations.discard("")
        return combinations

    def path_generator(self, city):
        """
        same as domain_generator(), but special characters are allowed
        """
        combinations = self.domain_generator(city)

        for name in self.add_prefeitura_to_name(city):
            combinations.add(self.name_with_underline(name))    
            combinations.add(self.name_with_hifen(name))        

        return combinations

    def add_prefeitura_to_name(self, name):
        return [
            name,
            f"prefeitura {name}",
            f"prefeitura de {name}",
            f"prefeitura municipal {name}",
            f"prefeitura municipal de {name}",
        ]
    
    def name_no_blankspaces(self, name): 
        return slugify(name, separator="", replacements=self.replacements)

    def name_with_underline(self, name): 
        return slugify(name, separator="_", replacements=self.replacements)

    def name_with_hifen(self, name): 
        return slugify(name, separator="-", replacements=self.replacements)

    def name_parts_set(self, name): 
        stopwords = self.stopwords + ["prefeitura", "municipal"]
        return set(slugify(name, separator=" ", replacements=self.replacements, stopwords=stopwords).split())

    def progressive_colapsed_words_set(self, name):
        """
        Iterates over a words list creating combinations following
        abbreviation + rest pattern. 
        Stopwords are allowed to exist in "rest" part, but not 
        in "abbreviation" part.
        
        Example: 
        input: Prefeitura Municipal Santo Antonio do Paraiso
        outputs:
        - P Municipal Santo Antonio do Paraiso
        - P M Santo Antonio do Paraiso
        - P M S Antonio do Paraiso
        - P M S A do Paraiso
        - P M S A Paraiso
        - P M S A P
        """
        colapsed_words = set()
        words = slugify(name, separator=" ", replacements=self.replacements).split()

        abbrev = ""
        for i in range(len(words)):
            word = words[i]
            
            if word not in self.stopwords:
                abbrev += word[0]
                rest = words[i+1:]                
                colapsed_words.add(self.join_parts(abbrev, rest))
                colapsed_words.add(self.join_parts(abbrev, self._wo_stopwords(rest)))
        
        return colapsed_words

    def _wo_stopwords(self, sublist):
        return [x for x in sublist if x not in self.stopwords]
    
    def join_parts(self, inicial, sublist):
        """
        Concatenate text parts, discarding one letter only possibility
        For example, prevents returning "r" for "Recife"
        """
        opt = f"{inicial}{''.join(sublist)}"
        if len(opt) > 1:
            return opt
        return ""
