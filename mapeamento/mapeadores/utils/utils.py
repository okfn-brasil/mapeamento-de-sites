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
    collapsed_words = []
    abbrev = ""

    for char in join_char:
        text = text.replace(char, "")

    words = slugify(text, separator=" ").split()

    for i in range(len(words)):
        word = words[i]
        
        if word not in stopwords:
            abbrev += word[0]

        rest = words[i+1:]                
        collapsed_words.append(f"{abbrev}{''.join(rest)}")
    
    return collapsed_words