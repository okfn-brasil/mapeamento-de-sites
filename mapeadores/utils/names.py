from slugify import slugify

def one_worded(text, stopwords=[]): 
    return slugify(text, separator="", stopwords=stopwords)

def underscored(text, drop_chars=[], stopwords=[]):
    for char in drop_chars:
        text = text.replace(char, "") 
    return slugify(text, separator="_", stopwords=stopwords) 

def hyphened(text, drop_chars=[], stopwords=[]):
    for char in drop_chars:
        text = text.replace(char, "") 
    return slugify(text, separator="-", stopwords=stopwords) 

def splitted(text, drop_chars=[], stopwords=[]):
    for char in drop_chars:
        text = text.replace(char, "")
    return slugify(text, separator=" ", stopwords=stopwords).split()

def progressive_collapsed(text, drop_chars=[], stopwords=[]):
    """Cria combinacoes de uma palavra no padrao abreviacao + resto

    Keyword arguments:
    text -- palavra a ser usada
    drop_chars -- lista de caracteres especiais a serem desconsiderados
    stopwords -- lista de palavras a serem desconsideradas

    Exemplo sem drop_chars e stopwords
    entrada: Prefeitura Municipal Santo Antonio do Paraiso
    saidas:
    - P Municipal Santo Antonio do Paraiso
    - P M Santo Antonio do Paraiso
    - P M S Antonio do Paraiso
    - P M S A do Paraiso
    - P M S A Paraiso
    - P M S A P
    """
    collapsed_words = []
    collapsed_prefix = ""

    for char in drop_chars:
        text = text.replace(char, "")

    words = slugify(text, separator=" ").split()
    for i, word in enumerate(words):
        
        if word not in stopwords:
            collapsed_prefix += word[0]

        following_words = words[i+1:]                
        collapsed_words.append(f"{collapsed_prefix}{''.join(following_words)}")
        collapsed_words.append(f"{collapsed_prefix}{''.join(_remove_stopwords(following_words, stopwords))}")

    return collapsed_words

def _remove_stopwords(sublist, stopwords):
    return [x for x in sublist if x not in stopwords]