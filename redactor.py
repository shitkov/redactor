import re
import pymorphy2

def redact_text(text):
    morph = pymorphy2.MorphAnalyzer(lang='ru')

    text = replace_quotes(text)
    text = add_dot(text)
    text = add_title(text)
    text = check_max_len(text)
    text = get_brackets(morph, text)
    text = get_brackets(morph, text)
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
        if ans[-1] != '.':
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
