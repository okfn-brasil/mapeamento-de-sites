import scrapy

from urllib.parse import urlparse, urlunparse
from itertools import product

from mapeadores.utils import utils
from mapeadores.spiders.bases.mapeador import Mapeador

class MapeadorSemantico(Mapeador):

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
        return {
            variation
            for pattern in self.url_patterns
            for variation in self.generate_pattern_variations(pattern, name, state_code)
        }

    def generate_pattern_variations(self, pattern, name, state_code):
        """
        Creates combinations depending on the context. 
        If "city_name" is in the netloc, combinations are more limited
        """
        pattern = pattern.replace("state_code", state_code.lower()) 
        parsed_url = urlparse(pattern)
        combinations = self.make_combinations(name)

        if "city_name" in parsed_url.netloc:
            combinations = self.remove_irrelevants(combinations, ["-", "_"])
            generated_attribute = "netloc"
        elif "city_name" in parsed_url.path:
            combinations = self.remove_irrelevants(combinations)
            generated_attribute = "path"
        else:
            self.logger.error("city_name should exist in URL pattern")
            return

        schemes = ["http", "https"]
        for scheme, option in product(schemes, combinations):
            replacements = {
                "scheme": scheme,
                generated_attribute: getattr(parsed_url, generated_attribute).replace(
                    "city_name", option
                ),
            }
            yield urlunparse(parsed_url._replace(**replacements))

    def make_combinations(self, city):
        combinations = set()
        prepened_names = self.add_prefeitura_to_name(city)

        stopwords_list = ["da", "de", "do", "das", "dos", "e"]
        stopwords_with_d = stopwords_list + ["d"]

        stopwords_options = ([], stopwords_list, stopwords_with_d)
        join_char_options = ([], "'", "-", ["'", "-"])
        
        for name, stopwords, char in product(prepened_names, stopwords_options, join_char_options):
            combinations.add(utils.one_worded(name, stopwords))
            combinations.add(utils.underscored(name, char, stopwords))
            combinations.add(utils.hyphened(name, char, stopwords))
            combinations.update(set(utils.splitted(name, char, stopwords_with_d)))
            combinations.update(set(utils.progressive_collapsed(name, char, stopwords)))

        return combinations

    def add_prefeitura_to_name(self, name):
        return [
            name,
            f"prefeitura {name}",
            f"prefeitura de {name}",
            f"prefeitura municipal {name}",
            f"prefeitura municipal de {name}",
            f"pm {name}",
        ]
    
    def remove_irrelevants(self, combinations, irrelevant_chars=[]):
        irrelevants = irrelevant_chars + [
            "municipal",
            "prefeitura",
        ] 
        for option, irrelevant in product(combinations, irrelevants):
            if irrelevant in option or len(option)<=1:
                combinations.remove(option)

        return combinations