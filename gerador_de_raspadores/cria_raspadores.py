import csv
from unidecode import unidecode
from datetime import datetime

from layouts import adiarios

source_file = "./resultados/resultado_mapeamento_adiariosv1.csv"
spiders_dir = "./../../../querido-diario/data_collection/gazette/spiders"
 
def apply_layout(padrao, args, isInterrupted):
    if padrao == "ADIARIOS_v1": return adiarios.write_pattern_v1(args, isInterrupted)
    if padrao == "ADIARIOS_v2": return adiarios.write_pattern_v2(args, isInterrupted)


def create_spider(item, isInterrupted):
    uf = item['uf'].lower()
    spider_name = _make_spider_name(item, isInterrupted)
    spider_file = f"{spiders_dir}/{uf}/{spider_name}.py"

    args = {
        "spider_name": spider_name,
        "class_name": _make_class_name(item),
        "ibge_id": item["id"],
        "date_from": _format_date(item['data_inicial']),
        "date_to": _format_date(item['data_final']),
        "url": item['url_do_padrao'],
        "nome_do_padrao": item['nome_do_padrao'],
        "uf": uf,
        "domain": "",
        "info_auxiliar": item["info_auxiliar"],
    }

    spider_str = apply_layout(item['nome_do_padrao'], args, isInterrupted)

    if not spider_str is None:   
        f = open(spider_file, "w")
        f.write(spider_str)
        f.close()

def read_metadata(filename):
    data = []
    with open(filename, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    csvfile.close()
    return data

def main():
    metadata = read_metadata(source_file)

    for i in range(len(metadata)):
        if "atual" in metadata[i]['status']:
            isInterrupted = False
        elif "descontinuado" in metadata[i]['status']:
            isInterrupted = True

        create_spider(metadata[i], isInterrupted)

def _make_spider_name(item, isInterrupted):
    uf = unidecode(item["uf"]).strip().lower()
    mun = unidecode(item["municipio"]).strip().lower().replace("-", " ").replace("'", "")
    name = f"{uf}_{mun.replace(' ', '_')}"

    if isInterrupted:
        return f"{name}_{item['data_inicial'][:4]}"  
    return name
    
def _make_class_name(item):
    uf = unidecode(item["uf"]).strip().lower()
    mun = unidecode(item["municipio"]).strip().lower().replace("-", " ").replace("'", "")
    mun_substrings = [x.capitalize() for x in mun.split()]

    return f"{uf.capitalize()}{''.join(mun_substrings)}"

def _format_date(rawdata):
    return datetime.strptime(rawdata, "%Y-%m-%d").strftime("%Y, %m, %d").replace(", 0", ", ")

if __name__ == "__main__":
    main()
