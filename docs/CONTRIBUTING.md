# Sumário
- [O que deve ser mapeado](#o-que-deve-ser-mapeado)
- [O que o mapeamento busca obter](#o-que-o-mapeamento-busca-obter)
- [Como os mapeadores funcionam](#como-os-mapeadores-funcionam)
    - [Mapeadores base](#mapeadores-base)
    - [MapeadorSemantico](#MapeadorSemantico)
        - [Mapeadores derivados de MapeadorSemantico](#mapeadores-derivados-de-mapeadorsemantico)
            - [Elementos obrigatórios](#elementos-obrigatórios-nos-mapeadores-derivados-de-mapeadorsemantico)
            - [Modelo de código](#modelo-para-o-código-do-mapeador)
    - [MapeadorNumerico](#mapeadornumerico)

# O que deve ser mapeado
O acúmulo de conhecimento ao redor do Querido Diário, em particular de sites de prefeituras,
permitiu identificarmos diversos padrões que prefeituras usam. Nomeamos a situação de 
**Sistemas Replicáveis** e cada padrão recebe um nome particular.

O mapeamento, portanto, busca encontrar quantos municípios aderem a cada caso, 
partindo da [lista de padrões conhecidos](https://docs.queridodiario.ok.org.br/pt-br/latest/contribuindo/lista-sistemas-replicaveis.html)
e, se possível, encontrando novos layouts para serem mapeados também. 

Navegue [as issues](https://github.com/okfn-brasil/mapeamento-de-sites/issues) do
repositório para escolher um novo mapeador para contribuir ou cadastrar.

# O que o mapeamento busca obter
Definidos em [`items`](/mapeadores/items.py), os dados de interesse 
para serem mapeados são aqueles que os raspadores do Querido Diário usam:

| nome | descrição | ação |
| ---- | --------- | -------- |
| **territory_id** | código IBGE do município | mapeador usa de [`territories.csv`](/mapeadores/resources/territories.csv) |
| **city** | nome do município | mapeador usa de [`territories.csv`](/mapeadores/resources/territories.csv) |
| **state** | estado do município | mapeador usa de [`territories.csv`](/mapeadores/resources/territories.csv) |
| **pattern** | nome do padrão | deve ser definido no mapeador (*hardcoded*) |
| **url** | formato de URL para o município que existe na internet | deve ser coletado pelo mapeador |
| **date_from** | data da edição mais antiga disponível na URL | deve ser coletado pelo mapeador |
| **date_to** | data da edição mais recente disponível na URL | deve ser coletado pelo mapeador |
| **status** | classificação da URL entre "válido" e "inválido" | deve ser coletado pelo mapeador |

# Como os mapeadores funcionam

## Mapeadores base
- [Classe **Mapeador**](/mapeadores/spiders/bases/mapeador.py): 
Classe mãe para os outros dois mapeadores base do repositório. Seu principal propósito é 
o de carregar o arquivo `territories.csv`, com o nome dos municípios brasileiros, 
para ser usado por todos os mapeadores do projeto. 

- [Classe **MapeadorSemantico**](/mapeadores/spiders/bases/mapeador_semantico.py):
Derivando de `Mapeador`, o mapeador semântico serve para implementar a lógica de mapeamento baseada no nome do município, como em `https://www.buriticupu.ma.gov.br/diariooficial.php` que "Buriticupu" e "MA" estão presente na URL.

- [Classe **MapeadorNumerico**](/mapeadores/spiders/bases/mapeador_numerico.py)
[*implementação pendente!*]: Derivando de `Mapeador`, o mapeador numérico serve para implementar a lógica de mapeamento baseada em códigos, como em `https://www.portaliop.org.br/diariopref/?id=77` que o identificador da prefeitura é o `77`, não deixando evidente qual município diz respeito.

## MapeadorSemantico

A principal ação do `MapeadorSemantico` é a de criar variações com os nomes dos 
municípios - como `nomedomunicipio`, `prefeitura_de_municipio`, `nome-do-municipio`,
etc -, encaixá-las no molde da URL padrão e tentar um acesso a essa URL inventada, 
verificando se ela existe na internet (= a requisição retorna status positivo).

Idealmente, todas as possibilidades conhecidas e imagináveis podem ser previstas 
para serem tentadas e, um novo arranjo sendo descoberto, o `MapeadorSemantico` deve 
ser atualizado para incluí-lo.

### Mapeadores derivados de MapeadorSemantico
O `MapeadorSemantico` constroi as combinações e tenta acessar URLs inventadas, mas 
quem define o molde da URL a ser construída e o que é feito ao se obter sucesso 
no acesso à cada URL inventada é um mapeador específico. Cada mapeador fica em arquivos 
separados, nomeados pelo padrão, no diretório [`mapeamento-de-sites/mapeadores/spiders`](/mapeadores/spiders/).

#### Elementos obrigatórios nos mapeadores derivados de MapeadorSemantico
- **atributo `name`**: string com o nome do padrão

- **atributo `url_patterns`**: lista de strings que representam o padrão (molde), 
contendo `nome_do_municipio` e `UF` nos trechos generalizáveis. Exemplo:

``` python
# https://doem.org.br/ba/acajutiba/diarios
# https://doem.org.br/ba/mascote/diarios

url_patterns = ["https://doem.org.br/UF/nome_do_municipio/diarios"]
```

- **método `parse()`**: acionado quando a requisição à URL inventada obtém sucesso,
deve verificar se o site diz respeito ao padrão. Caso sim, deve construir um item 
de tipo `valido` e, caso não, um item de tipo `invalido`; sempre coletando os 
[metadados necessários](#o-que-o-mapeamento-busca-obter).

- **método `belongs_to_pattern()`**: usa a resposta da requisição para confirmar
o padrão a partir do layout da página. Algum ou alguns elementos da página podem 
ser escolhidos para serem verificados que, ao estarem presentes, confirmam o padrão.

*Importante*: sites com URLs de mesmo molde existirem não implica que os sites em
si também compartilham de um mesmo padrão visual. Abaixo, há três URLs em formato 
`https://www.nome_do_municipio.UF.gov.br/diariooficial.php`, onde um dos casos não 
tem a mesma estética dos outros. Experimente abrir os sites para ver.

- https://www.abreulandia.to.gov.br/diariooficial.php
- https://www.arame.ma.gov.br/diariooficial.php
- https://www.aurora.ce.gov.br/diariooficial.php

#### Modelo para o código do mapeador
``` python

import scrapy

from mapeadores.spiders.bases.mapeador_semantico import MapeadorSemantico
from mapeadores.items import MapeamentoItem


class Mapeador<Nome>(MapeadorSemantico):   
    """Mapeia o padrao <nome>

    Exemplos:
    url 1
    url 2
    """
    name = "<nome>"

    url_patterns = [
        # URL generalizada contendo 'nome_do_municipio' e/ou 'UF'
        # nas partes substituiveis
        "http...nome_do_municipio.UF... ",
    ]

    def parse(self, response, item):            # se o site não existir, nem chega aqui
        if self.belongs_to_pattern(response):   # o site existe e é do padrão
            item["url"] = response.url
            item["status"] = "valido"

            # lógica para coletar date_from
            # lógica para coletar date_to

            # ... caso necessário, evoca métodos auxiliares e/ou faz novas requisições ...

            # deve finalizar com o código abaixo, que pode ficar neste método ou 
            # dentro de algum dos métodos auxiliares criados
            yield MapeamentoItem(
                **item,
                # ...
            )
        
        else:                                   # o site existe, mas não é do padrão
            yield MapeamentoItem(
                **self.make_invalid_item(item, response.url),
            )

    def belongs_to_pattern(self, response):
        if ... # verificações no layout do site
            return True
        return False
```

## MapeadorNumerico
(... em breve ...)

