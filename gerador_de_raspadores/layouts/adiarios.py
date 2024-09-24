def write_pattern_v1(args, isInterrupted):
    args["url"] = args["url"].replace("/diariooficial.php", "")
    args["domain"] = args["url"].replace("https://www.", "")
    return write_pattern(args, 1, isInterrupted)

def write_pattern_v2(args, isInterrupted):
    args["url"] = args["url"].replace("/jornal.php", "")
    args["domain"] = args["url"].replace("https://www.transparencia.", "")
    return write_pattern(args, 2, isInterrupted) 

def write_pattern(args, tipo, isInterrupted):
    if tipo == 1:
        superclassfile = "adiarios_v1"
        superclassname = "BaseAdiariosV1Spider"
    elif tipo == 2:
        superclassfile = "adiarios_v2"
        superclassname = "BaseAdiariosV2Spider"
    
    endline = ""
    if isInterrupted:
        endline = f"    end_date = date({args['date_to']})\n"

    return pattern(args, superclassfile, superclassname, endline)

def pattern(args, superclassfile, superclassname, endline=""):
    return f"""from datetime import date

from gazette.spiders.base.{superclassfile} import {superclassname}


class {args['class_name']}Spider({superclassname}):
    TERRITORY_ID = "{args['ibge_id']}"
    name = "{args['spider_name']}"
    allowed_domains = ["{args['domain']}"]
    BASE_URL = "{args['url']}"
    start_date = date({args['date_from']})
{endline}"""