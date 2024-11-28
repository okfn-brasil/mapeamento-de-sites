import csv
from datetime import datetime, date
import os

def main():
    source_dir = os.environ["SOURCE_DIR"]
    output_dir = os.environ["OUTPUT_DIR"]
    final_data_dir = os.environ["FINAL_DATA_DIR"]

    all_data = []

    for file in os.listdir(source_dir):
        file_path = os.path.join(source_dir, file)

        if file_path.endswith("_validos.csv"):
            data = read(file_path)
            data = reduce_occurrences_to_one(data)
            data = make_list_dropping_occurences(data)
            data = sorted(data, key=lambda x: x['territory_id'])            
            write(data, os.path.join(output_dir, file))

            all_data += data

    all_data = sorted(all_data, key=lambda x: x['territory_id'])
    write(all_data, os.path.join(final_data_dir, "cidades_mapeadas.csv"))

def read(file_path):    
    data = {}

    with open(file_path, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            id = row["territory_id"]
            data.setdefault(id, []).append(row)

    return data

def write(data, file_path):
    field_names = ['territory_id','state','city','pattern','status','date_from','date_to','url']
    with open(file_path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(data)

def reduce_occurrences_to_one(data):
    """Reduz ocorrencias multiplas a apenas uma, por territorio e por URL.

    Recebe 'data' contendo URLs referentes a territorios com diferentes datas iniciais
    e finais. Itera nesses dados buscando a data mais antiga e a data mais recente, 
    no geral. Classifica a data mais recente em "atual" ou "descontinuado". 

    Por exemplo:
    Acajutiba,2019-09-02,2019-09-30,doem,BA,valido,2900306,https://doem.org.br/ba/acajutiba/diarios
    Acajutiba,2018-08-03,2018-08-31,doem,BA,valido,2900306,https://doem.org.br/ba/acajutiba/diarios
    Acajutiba,2021-08-05,2021-08-30,doem,BA,valido,2900306,https://doem.org.br/ba/acajutiba/diarios

    A ocorrencia reduzida deve ser apenas
    Acajutiba,2018-08-03,2021-08-30,doem,BA,descontinuado,2900306,https://doem.org.br/ba/acajutiba/diarios

    Para facilitar o agrupamento dos casos de mesmo contexto, 'data' esta organizado 
    como dicionario com territorio e URL como chaves:
    territory_id: {
        URL_1: { 
            date_from, 
            date_to, 
            ... 
        }
        URL_2: { 
            date_from, 
            date_to, 
            ... 
        }
    }
    """
    filtered = {}
    for city_id in data:
        if city_id not in filtered:
            filtered[city_id] = {}

        for city_entry in data[city_id]:
            url = city_entry["url"]

            if url not in filtered[city_id]:
                filtered[city_id][url] = city_entry
                filtered[city_id][url]["status"] = _classify_status(city_entry["date_to"])
            
            else:
                date_from, date_to = _best_dates(filtered[city_id][url], city_entry)
                filtered[city_id][url]["date_from"] = date_from
                filtered[city_id][url]["date_to"] = date_to
                filtered[city_id][url]["status"] = _classify_status(date_to)

    return filtered

def _best_dates(one, another):
    """Retorna a data mais antiga e a mais nova entre dois casos. 

    Assume as datas de one como padrão, trocando por another ao comparar, caso
    verdadeiro.
    """
    oldest_date_from = one['date_from']
    if one['date_from'] > another['date_from']:
        oldest_date_from = another['date_from']
    
    newest_date_to = one['date_to']
    if one['date_to'] < another['date_to']:
        newest_date_to = another['date_to']
    
    return oldest_date_from, newest_date_to  

def _classify_status(enddate):
    current = date.today()
    enddate = datetime.strptime(enddate, "%Y-%m-%d").date()
    if enddate.year < current.year:
        return "descontinuado"
    elif enddate.year == current.year and enddate.month < current.month-1:
        return "descontinuado"
    return "atual"

def make_list_dropping_occurences(data):
    """Transforma dicionario em lista descartando ocorrencias irrelevantes"""
    disaggregated = []

    for territory_id in data:
        for url in data[territory_id]:
            if is_droppable(data[territory_id], url):
                continue
            disaggregated.append(data[territory_id][url])
    return disaggregated

def is_droppable(entry, url):
    """Verifica casos descartaveis"""
    # caso: registro está vazio
    if entry is None or url is None:
        return True
    
    # caso: mesma URL com versoes http e https. Descarta a versao http 
    if "http:" in url and url.replace("http:", "https:") in entry:
        return True
    
    # caso: registro com data final e data inicial iguais
    if entry[url]['date_from'] == entry[url]['date_to']:
        return True

    return False           
    
if __name__ == '__main__':
    main()