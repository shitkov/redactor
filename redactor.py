import re
import pymorphy2
from pyaspeller import YandexSpeller

def redact_text(text, yo_dict_path):
    morph = pymorphy2.MorphAnalyzer(lang='ru')
    speller = YandexSpeller()
    yo_dict = create_dict(yo_dict_path)

    text = replace_quotes(text)
    text = add_dot(text)
    text = add_title(text)
    text = check_max_len(text)
    text = get_brackets(morph, text)
    text = get_brackets(morph, text)
    text = spellcheck(speller, text)
    text = yoficator(yo_dict, text)
    return text

# 1. Replace quotes
def replace_quotes(text):
    q1 = '«'
    q2 = '»'
    ans = text.strip()
    ans = re.sub(r'\"\b', q1, ans)
    ans = re.sub(r'\"', q2, ans)
    return ans

# 2. Add dot to end of statement.
def add_dot(text):
    ans = text.strip()
    if len(text) > 0:
        if ans[-1] not in ['?', '!', '.']:
            ans += '.'
    return ans

# 3. Text title
def add_title(text):
    ans = text.strip()
    ans = ans.split(' ')
    ans[0] = ans[0].title()
    ans = ' '.join(ans)
    return ans

# 4. Max len 250 symbols
def check_max_len(text):
    if len(text) > 250:
        print('Превышена максимальная длина текста!')
        return text
    else:
        return text

# 5. Get brackets
def get_brackets(morph, text):
    word_list = text.split(' ')
    if len(word_list) < 2:
        return text
    forbidden_symbols = ['"', '«', '»']
    pos_list = [morph.parse(word)[0].tag.POS for word in word_list]
    case_list = [morph.parse(word)[0].tag.case for word in word_list]
    for i in range(len(word_list) - 1):
        if (pos_list[i] == pos_list[i + 1]) and (case_list[i] == case_list[i + 1]):
            if not any((c in forbidden_symbols) for c in (word_list[i] + word_list[i + 1])):
                word_list[i + 1] = '(' + word_list[i + 1] + ')'

    return ' '.join(word_list)

# 6. spellckecker
def spellcheck(speller, text):
    return speller.spelled(text)

# 7. yofication

def yoficator(yo_dict, text):
    tokens = text.split(' ')
    phrase = []
    for token in tokens:
        if token in yo_dict:
            phrase.append(yo_dict[token])
        else:
            phrase.append(token)

    return ' '.join(phrase)

def create_dict(data_path):
    dictionary = {}
    with open(data_path) as f:
        counts = 0
        for line in f:
            if not "*" in line:
                cline = line.rstrip('\n')
                if "(" in cline:
                    bline,sline = cline.split("(")
                    sline = re.sub(r'\)', '', sline)
                else:
                    bline = cline
                    sline = ""
                if "|" in sline:
                    ssline = sline.split("|")
                    for ss in ssline:
                        value = bline + ss;
                        key = re.sub(r'ё', 'е', value)
                        dictionary[key] = value
                        counts = counts + 1
                else:
                    value = bline
                    key = re.sub(r'ё', 'е', value)
                    dictionary[key] = value
                    counts = counts + 1
    return dictionary
