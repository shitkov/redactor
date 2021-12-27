import re
import json
import pymorphy2
from pyaspeller import YandexSpeller


class Redactor:


    def __init__(self, yo_dict_path, abb_dict_path, all_abb_list_path, bad_abb_list_path):
        self.yo_dict = self._create_dict(yo_dict_path)
        self.morph = pymorphy2.MorphAnalyzer(lang='ru')
        self.speller = YandexSpeller()
        self.abb_dict = None
        self.all_abb_list = None
        self.bad_abb_list = None
        self._get_abb_lists(abb_dict_path, all_abb_list_path, bad_abb_list_path)


    def run(self, text):
        text = self.replace_quotes(text)
        text = self.check_max_len(text)
        text = self.abbreviator(text)
        text = self.get_brackets(self.morph, text)
        text = self.spellcheck(self.speller, text)
        text = self.yoficator(self.yo_dict, text)
        text = self.add_dot(text)
        text = self.add_title(text)
        text = self.remove_empty(text)
        text = self.remove_endpoints(text)
        return text
    

    # 1. Replace quotes
    def replace_quotes(self, text):
        q1 = '«'
        q2 = '»'
        ans = text.strip()
        ans = re.sub(r'\"\b', q1, ans)
        ans = re.sub(r'\"', q2, ans)
        return ans


    # 2. Add dot to end of statement.
    def add_dot(self, text):
        ans = text.strip()
        if len(text) > 0:
            if ans[-1] not in ['?', '!', '.']:
                ans += '.'
        return ans


    # 3. Text title
    def add_title(self, text):
        ans = text.strip()
        ans = ans.split(' ')
        ans[0] = ans[0].title()
        ans = ' '.join(ans)
        return ans


    # 4. Max len 250 symbols
    def check_max_len(self, text):
        if len(text) > 250:
            return 'Превышена максимальная длина текста: входная последовательность {} символов при максимальной длине в 250'.format(len(text))
        else:
            return text


    # 5. Get brackets
    def get_brackets(self, morph, text):
        text_clean = re.sub('[^А-ЯËа-яё ]', ' ', text)
        text_clean = re.sub(r" +", " ", text_clean).strip()
        word_list = text_clean.split(' ')
        if len(word_list) < 2:
            return text
        forbidden_symbols = ['"', '«', '»', '(', ')']
        pos_list = [morph.parse(word)[0].tag.POS for word in word_list]
        case_list = [morph.parse(word)[0].tag.case for word in word_list]
        for i in range(len(word_list) - 1):
            if (pos_list[i] == pos_list[i + 1] == 'NOUN') and (case_list[i] == case_list[i + 1] == 'nomn'):
                if not any((c in forbidden_symbols) for c in (word_list[i] + word_list[i + 1])):
                    text = text.replace(word_list[i + 1], '(' + word_list[i + 1] + ')')
        return text


    # 6. spellckecker
    def spellcheck(self, speller, text):
        return speller.spelled(text)


    # 7. yofication
    def yoficator(self, yo_dict, text):
        tokens = text.split(' ')
        phrase = []
        for token in tokens:
            if token in yo_dict:
                text = text.replace(token, yo_dict[token])
        return text


    # 8. abbreviation
    def abbreviator(self, text):
        words = re.findall(r"\b[а-яёА-ЯË]{1,}\b", text)
        for abb in words:
            if abb.upper() in self.bad_abb_list:
                return 'Запрещенная аббревиатура: {}!'.format(abb.upper())
            elif abb.upper() in self.abb_dict.keys():
                text = text.replace(abb, self.abb_dict[abb.upper()])
            elif abb.upper() in self.all_abb_list:
                text = text.replace(abb, abb.upper())
            else:
                text = text.replace(abb, abb.lower())
        return text

    
    # 9. Remove empty strings
    def remove_empty(self, text):
        return text.replace('\n\n', '\n')


    # 10. Remove endpoints
    def remove_endpoints(self, text):
        sentenses = []
        for sent in text.split('\n'):
            if sent[-1] == '.':
                sent = sent[:-1]
            sentenses.append(sent)
        return '\n'.join(sentenses)


    def _get_abb_lists(self, abb_dict_path, all_abb_list_path, bad_abb_list_path):
        # get abb dict
        with open(abb_dict_path) as json_file:
            self.abb_dict = json.load(json_file)

        # get all abbs
        all_abb_list = []
        with open(all_abb_list_path) as f:
            for line in f:
                all_abb_list.append(line.rstrip('\n'))
        self.all_abb_list = all_abb_list

        # get bad abbs
        bad_abb_list = []
        with open(bad_abb_list_path) as f:
            for line in f:
                bad_abb_list.append(line.rstrip('\n'))
        self.bad_abb_list = bad_abb_list


    def _create_dict(self, data_path):
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