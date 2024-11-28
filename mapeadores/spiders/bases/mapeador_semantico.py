import scrapy

from abc import ABC, abstractmethod
from urllib.parse import urlparse, urlunparse
from itertools import product

from mapeadores.utils import names
from mapeadores.spiders.bases.mapeador import Mapeador

class MapeadorSemantico(ABC, Mapeador):
    url_patterns = None
    
    def __init__(self):
        super().__init__()

        if isinstance(self.url_patterns, list) and len(self.url_patterns) > 0:
            for pattern in self.url_patterns:
                if "nome_do_municipio" not in pattern:
                    raise ValueError("O texto 'nome_do_municipio' deve existir em todas as strings de 'url_patterns'")
        else:
            raise TypeError("Adapte 'url_patterns' para ser uma lista de strings não-vazia")
        
    def start_requests(self):        
        for i, territory in enumerate(self.territories):
            self.show_progress(i)

            item = {
                "territory_id": territory['territory_id'],
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
        """Cria URLs padronizadas a partir de combinacoes com nome de municipio
        
        Keyword arguments:
        pattern -- string de URL contendo "nome_do_municipio" e/ou "UF"
        name -- string do nome do municipio
        state_code -- sigla do estado do municipio

        Constroi combinacoes com o nome do municipio e usa cada combinacao para
        substituir "nome_do_municipio" em pattern. Se "nome_do_municipio" estiver
        na parte do dominio, as combinacoes com caracteres especiais são descartadas.
        """
        combinations = self.make_combinations(name)

        pattern = pattern.replace("UF", state_code.lower()) 
        parsed_url = urlparse(pattern)        

        if "nome_do_municipio" in parsed_url.netloc:
            special_chars = ["-", "_"]
            combinations = self.remove_irrelevants(combinations, special_chars)
            generated_attribute = "netloc"
        elif "nome_do_municipio" in parsed_url.path:
            combinations = self.remove_irrelevants(combinations)
            generated_attribute = "path"

        schemes = ["http", "https"]
        for scheme, option in product(schemes, combinations):
            replacements = {
                "scheme": scheme,
                generated_attribute: getattr(parsed_url, generated_attribute).replace(
                    "nome_do_municipio", option
                ),
            }
            yield urlunparse(parsed_url._replace(**replacements))

    def make_combinations(self, city):
        combinations = set()
        prepened_names = self.add_prefeitura_to_name(city)

        stopwords_list = ["da", "de", "do", "das", "dos", "e", "no"]
        stopwords_with_d = stopwords_list + ["d"]

        stopwords_options = ([], stopwords_list, stopwords_with_d)
        drop_chars_options = ([], ["'"], ["-"], ["'", "-"])
        
        for name, stopwords, char in product(prepened_names, stopwords_options, drop_chars_options):
            combinations.add(names.one_worded(name, stopwords))
            combinations.add(names.underscored(name, char, stopwords))
            combinations.add(names.hyphened(name, char, stopwords))
            combinations.update(set(names.splitted(name, char, stopwords_with_d)))
            combinations.update(set(names.progressive_collapsed(name, char, stopwords)))

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
        irrelevant_words = [
            "municipal",
            "prefeitura",
        ]

        for option, word, char in product(combinations, irrelevant_words, irrelevant_chars):
            combinations.discard(word)
            if char in option or len(option)<3:
                combinations.discard(option)

        return combinations
    
    @abstractmethod
    def parse(self, response, item):
        """Processa a resposta do site"""
        pass

    @abstractmethod
    def belongs_to_pattern(self, response):
        """Verifica no site os marcadores conhecidos do padrão"""
        pass