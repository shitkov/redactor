import re
import json
import pymorphy2
from pyaspeller import YandexSpeller


class Redactor:


    def __init__(self, yo_dict_path, abb_dict_path, all_abb_list_path, bad_abb_list_path):
        self.yo_dict = self._create_dict(yo_dict_path)
        self.morph = pymorphy2.MorphAnalyzer(lang='ru')
        self.speller = YandexSpeller(lang='ru', check_yo=True)
        self.abb_dict = None
        self.all_abb_list = None
        self.bad_abb_list = None
        self._get_abb_lists(abb_dict_path, all_abb_list_path, bad_abb_list_path)


    def run(self, text):
        text = self.speller.spelled(text)
        text = self.check_max_len(text)
        text = self.replace_quotes(text)
        text = self.abbreviator(text)
        text = self.get_brackets(text)
        text = self.yoficator(text)
        text = self.remove_empty(text)
        text = self.remove_endpoints(text)
        text = self.add_title(text)
        text = self.hyphen_replacement(text)
        return text


    # Hyphen replacement
    def hyphen_replacement(self, text):
        hyphen = '—'
        sentenses = []
        for sent in list(map(lambda t: t.strip(), text.split('\n'))):
            if len(sent) > 0:
                if sent[0] == '-':
                    sent = hyphen + ' ' + sent[1:]
                    sent = re.sub(r" +", " ", sent)
            sentenses.append(sent)
        return '\n'.join(sentenses)

    # Replace quotes
    def replace_quotes(self, text):
        q1 = '«'
        q2 = '»'
        ans = text.strip()
        ans = re.sub(r'\"\b', q1, ans)
        ans = re.sub(r'\"', q2, ans)
        return ans


    # Title
    def add_title(self, text):
        sentenses = []
        for sent in list(map(lambda t: t.strip(), text.split('\n'))):
            if len(sent) > 0:
                sent_clean = re.sub('[^а-яёА-ЯË ]', ' ', sent)
                sent_clean = re.sub(r" +", " ", sent_clean).strip()
                fword = sent_clean.split(' ')[0]
                if len(fword) > 1:
                    fword_upp = fword[0].upper() + fword[1:]
                elif len(fword) == 1:
                    fword_upp = fword[0].upper()
                sent = sent.replace(fword, fword_upp, 1)
            sentenses.append(sent)
        return '\n'.join(sentenses)


    # Max len 250 symbols
    def check_max_len(self, text):
        if len(text) > 250:
            return 'Превышена максимальная длина текста: входная последовательность {} символов при максимальной длине в 250'.format(len(text))
        else:
            return text


    # Get brackets
    def get_brackets(self, text):
        text_clean = re.sub('[^А-ЯËа-яё ]', ' ', text)
        text_clean = re.sub(r" +", " ", text_clean).strip()
        word_list = text_clean.split(' ')
        if len(word_list) < 2:
            return text
        forbidden_symbols = ['"', '«', '»', '(', ')']
        pos_list = [self.morph.parse(word)[0].tag.POS for word in word_list]
        case_list = [self.morph.parse(word)[0].tag.case for word in word_list]
        for i in range(len(word_list) - 1):
            if (pos_list[i] == pos_list[i + 1] == 'NOUN') and (case_list[i] == case_list[i + 1] == 'nomn'):
                if not any((c in forbidden_symbols) for c in (word_list[i] + word_list[i + 1])):
                    text = text.replace(word_list[i + 1], '(' + word_list[i + 1] + ')')
        return text


    # Yofication
    def yoficator(self, text):
        tokens = text.split(' ')
        phrase = []
        for token in tokens:
            if token in self.yo_dict:
                text = text.replace(token, self.yo_dict[token])
        return text


    # Abbreviation
    def abbreviator(self, text):
        words = re.findall(r"\b[а-яёА-ЯË]{1,}\b", text)
        caps_list = re.findall(r"\b[А-ЯË]{2,}\b", text)
        for abb in words:
            if abb.upper() in self.bad_abb_list:
                return 'Запрещенная аббревиатура: {}!'.format(abb.upper())
            elif abb.upper() in self.abb_dict.keys():
                text = text.replace(abb, self.abb_dict[abb.upper()])
            elif abb.upper() in self.all_abb_list:
                text = text.replace(abb, abb.upper())
            elif abb in caps_list:
                text = text.replace(abb, abb.lower())
        return text

    
    # Remove empty strings
    def remove_empty(self, text):
        return re.sub(r'[\n]{2,}', '\n', text)


    # Remove endpoints
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