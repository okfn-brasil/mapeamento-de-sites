from slugify import slugify

def one_worded(text, stopwords=[]): 
    return slugify(text, separator="", stopwords=stopwords)

def underscored(text, join_char=[], stopwords=[]):
    for char in join_char:
        text = text.replace(char, "") 
    return slugify(text, separator="_", stopwords=stopwords) 

def hyphened(text, join_char=[], stopwords=[]):
    for char in join_char:
        text = text.replace(char, "") 
    return slugify(text, separator="-", stopwords=stopwords) 

def splitted(text, join_char=[], stopwords=[]):
    for char in join_char:
        text = text.replace(char, "")
    return slugify(text, separator=" ", stopwords=stopwords).split()

def progressive_collapsed(text, join_char=[], stopwords=[]):
    """
    Iterates over a words list creating combinations following
    abbreviation + rest pattern.
    
    Example without stopwords
    input: Prefeitura Municipal Santo Antonio do Paraiso
    outputs:
    - P Municipal Santo Antonio do Paraiso
    - P M Santo Antonio do Paraiso
    - P M S Antonio do Paraiso
    - P M S A do Paraiso
    - P M S A Paraiso
    - P M S A P
    """
    collapsed_words = []
    collapsed_prefix = ""

    for char in join_char:
        text = text.replace(char, "")

    words = slugify(text, separator=" ").split()

    for i, word in enumerate(words):
        
        if word not in stopwords:
            collapsed_prefix += word[0]

        following_words = words[i+1:]                
        collapsed_words.append(f"{collapsed_prefix}{''.join(following_words)}")
        collapsed_words.append(f"{collapsed_prefix}{''.join(_remove(following_words, stopwords))}")

    return collapsed_words

def _remove(sublist, stopwords):
    return [x for x in sublist if x not in stopwords]