# Objetivo
Repositório auxiliar para encontrar sites de prefeituras ou sites publicadores de 
diários oficiais.

É uma ação de apoio ao repositório de [raspadores do Querido Diário](https://github.com/okfn-brasil/querido-diario), 
visto que uma vez que padrões sejam mapeados em massa, o desenvolvimento
de raspadores para todos os casos achados é facilitado, permitindo aumentar a
cobertura do Querido Diário mais rapidamente.

# Contribuição
Leia o [CONTRIBUTING.md](/docs/CONTRIBUTING.md) para saber como contribuir.

# Entenda

| diretório | objetivo |
| --------- | -------- |
| [`mapeadores/spiders`](/mapeadores/spiders/) | conter um mapeador para cada padrão identificado |
| [`resultados/brutos`](/resultados/brutos/) | local de saída para arquivos de mapeamento |
| [`resultados/tratados`](/resultados/tratados/) | local de saída para as versões finais dos mapeamentos |
| [`docs`](/docs/) | ficam os arquivos de documentação do repositório |

Há duas rotinas pressupostas no repositório: **Mapeamento de URLs** e **Tratamento dos Resultados**.

## Mapeamento de URLs

Etapa que aciona mapeadores que funcionam com a lógica de tentativa e erro: fazer 
combinações com os nomes de municípios, encaixar em um formato de URL conhecido e 
experimentar fazer um acesso ao site "inventado" para verificar se é um caso existente, 
ou seja, se uma requisição a essa URL retorna sucesso.

Os mapeadores produzem dois arquivos `csv`, salvos no diretório `resultados/brutos`:
- `data-da-execucao_nome-do-mapeador_valido.csv`: contém a lista de URLs existentes 
e verificadas como casos de interesse (validadas).
- `data-da-execucao_nome-do-mapeador_invalido.csv`: contém a lista de URLs existentes, 
mas que não passaram na verificação do caso de interesse (inválida). 

O arquivo com `_invalido` não é utilizado por outras partes do fluxo, porém é criado 
por ser de valor para o objetivo central do repositório: encontrar sites das prefeituras. 
São casos em que, apesar de não serem do padrão sendo mapeado, a URL existe na internet
(o scrapy recebeu uma resposta de sucesso), fazendo da informação útil de ser preservada
para ser checada.

## Tratamento dos resultados

Script que percorre todos os arquivos válidos do diretório `resultados/brutos` 
fazendo duas coisas:
- aplica tratamentos neles e salva seus correspondentes tratados em `resultados/tratados`.
- unifica os mapeamentos parciais em um único mapeamento centralizado `resultados/cidades_mapeadas.csv`.

Como a lógica de mapeamento é a de "ficar chutando" URLs até encontrar casos de 
interesse e metadados importantes, é comum que o primeiro arquivo produzido (o 
salvo no diretório `resultados/brutos`) tenha muita "sujeira". Por exemplo, casos 
que o site existe, é do layout certo, mas só tem um documento. Ou, ainda, quando 
várias requisições são necessárias para encontrar a data mais antiga disponível, 
fazendo dos dados das requisições intermediárias são descartáveis.

Enfim, o script de tratamento existe para revisar e resumir esse arquivo inicial.

# Instalação
1. Faça um fork do repositório.
2. Em um terminal aberto no diretório de sua preferência, faça um clone (local) do seu fork (remoto).
``` sh
git clone https://github.com/<seu-usuario-do-github>/mapeamento-de-sites.git
```
3. Acesse o diretório local.
``` sh
cd mapeamento-de-sites/
```
4. Crie um ambiente virtual. A sugestão é nomear como `.venv`, mas pode escolher o nome que preferir.
``` sh
python3 -m venv .venv
```
5. Ative o ambiente virtual. 
``` sh
source .venv/bin/activate
```
6. Instale as dependências do projeto.
``` sh
pip install -r requirements.txt
```
5. Pronto! Seu repositório local está pronto para ser usado! :tada:

# Execução

## Um mapeador específico
1. Veja a lista de mapeadores integrados disponíveis para serem executados.
``` sh
scrapy list
``` 
2. Escolha um dos mapeadores da lista e execute-o.
``` sh
make run_spider SPIDER=<nome-do-mapeador>
```

## Tratamento dos dados mapeados
1. Acione a rotina de tratamento de arquivos
``` sh
make normalize
```

## Fluxo do repositório completo
1. O comando abaixo executa todos os mapeadores do repositório e, ao fim, aciona 
a rotina de tratamento de arquivos.
``` sh
make run_all
```