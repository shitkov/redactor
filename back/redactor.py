import re
import json
import difflib
from pyaspeller import YandexSpeller
from pullenti_wrapper.processor import Processor, GEO


class Redactor:


    def __init__(self, yo_dict_path, abb_dict_path, all_abb_list_path, bad_abb_list_path):
        self.yo_dict = self._create_dict(yo_dict_path)
        self.processor = Processor([GEO])
        self.speller = YandexSpeller(lang='ru')
        self.abb_dict = None
        self.all_abb_list = None
        self.bad_abb_list = None
        self._get_abb_lists(abb_dict_path, all_abb_list_path, bad_abb_list_path)


    def run(self, text):
        err = {}
        clean = text
        text, err = self.spellchecker(text, err)
        text, err = self.geo_speller(text, err)
        text, err = self.hyphen_replacement(text, err)
        text, err = self.replace_quotes(text, err)
        text, err = self.remove_brackets(text, err)
        text, err = self.yoficator(text, err)
        text, err = self.remove_empty(text,err)
        text, err = self.remove_endpoint(text, err)
        diff = self.get_fixes_diff(clean, text)
        text, err, diff = self.abbreviator(clean, text, err, diff)
        text, err = self.add_title(text, err)
        err = self.check_max_len(text, err)
        return {'text': text, 'diff': diff, 'err': err}


    # Speller
    def spellchecker(self, text, err):
        keyword = 'spellcheck'
        text_clean = re.sub('[^а-яёА-ЯË ]', ' ', str(text))
        text_clean = re.sub(r" +", " ", text_clean).strip()
        text_clean.strip()
        text_checked = self.speller.spelled(text_clean)
        words = text_clean.split(' ')
        words_checked_full = text_checked.split(' ')
        words_checked = [self.speller.spelled(word) for word in words]
        for word, cword, cword_full in zip(words, words_checked, words_checked_full):
            if len(word) > 3:
                if word != cword:
                    text = text.replace(word, cword)
                    if keyword not in err.keys():
                        err[keyword] = []
                    err[keyword].append(word + ' > ' + cword)
                elif word != cword_full:
                    text = text.replace(word, cword_full)
                    if keyword not in err.keys():
                        err[keyword] = []
                    err[keyword].append(word + ' > ' + cword_full)
        return text, err

    def get_fixes_diff(self, clean, text):
        diff = []
        for symb in enumerate(difflib.ndiff(clean, text)):
            if symb[1][0] in ['-', ' ']:
                diff.append(symb[1][0])
        return diff
    
    # GEO speller
    def geo_speller(self, text, err):
        keyword = 'geographical'
        matches = self.processor(text.upper()).matches
        for match in matches:
            start = match.span.start
            stop = match.span.stop
            if text[start:stop] != text[start:stop].capitalize():
                if keyword not in err.keys():
                    err[keyword] = []
                err[keyword].append(text[start:stop] + ' > ' + text[start:stop].capitalize())
            text = text.replace(text[start:stop], text[start:stop].capitalize())
        return text, err


    # Hyphen replacement
    def hyphen_replacement(self, text, err):
        keyword = 'hyphen'
        hyphen = '—'
        sentenses = []
        for sent in list(map(lambda t: t.strip(), text.split('\n'))):
            if len(sent) > 0:
                if sent[0] == '-':
                    sent_new = hyphen + ' ' + sent[1:].strip()
                    if keyword not in err.keys():
                        err[keyword] = []
                    err[keyword].append(sent + ' > ' + sent_new)
                    sentenses.append(sent_new)
                else:
                    sentenses.append(sent)
        text = '\n'.join(sentenses)
        return text, err

    # Replace quotes
    def replace_quotes(self, text, err):
        keyword = 'quotes'
        q1 = '«'
        q2 = '»'
        ans = text.strip()
        ans = re.sub(r'\"\b', q1, ans)
        ans = re.sub(r'\"', q2, ans)
        if text.strip() != ans:
            if keyword not in err.keys():
                err[keyword] = []
            if re.search('«(.*)»', ans):
                res = re.search('«(.*)»', ans).group(1)
                err[keyword].append('"' + res + '"' + ' > ' + q1 + res + q2)
        return ans, err


    # Title
    def add_title(self, text, err):
        keyword = 'title'
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
                else:
                    fword_upp = ''
                if fword != fword_upp:
                    if keyword not in err.keys():
                        err[keyword] = []
                    err[keyword].append(fword + ' > ' + fword_upp)
                sent = sent.replace(fword, fword_upp, 1)
                sentenses.append(sent)
        text = '\n'.join(sentenses)
        return text, err

    # Remove brackets
    def remove_brackets(self, text, err):
        keyword = 'brackets'
        words = re.findall(r'\(.*?\)', text)
        if words:
            if keyword not in err.keys():
                err[keyword] = []
        for word in words:
            text = text.replace(word, word[1:-1])
            err[keyword].append(word + ' > ' + word[1:-1])
        return text, err


    # Yofication
    def yoficator(self, text, err):
        keyword = 'yofication'
        tokens = text.split(' ')
        for token in tokens:
            if token in self.yo_dict:
                new_token = self.yo_dict[token]
                text = text.replace(token, new_token)
                if keyword not in err.keys():
                     err[keyword] = []
                err[keyword].append(token + ' > ' + new_token)
        return text, err


    # Max len 250 symbols
    def check_max_len(self, text, err):
        keyword = 'max_len'
        if len(text) > 250:
            ans = 'Превышена максимальная длина текста: входная последовательность {} символов при максимальной длине в 250'.format(len(text))
            if keyword not in err.keys():
                err[keyword] = []
            err[keyword].append(ans)
        return err


    # Remove empty strings
    def remove_empty(self, text, err):
        keyword = 'empty_string'
        text_clean = re.sub(r'[\n]{2,}', '\n', text)
        if text != text_clean:
            if keyword not in err.keys():
                err[keyword] = []
            err[keyword].append('remove empty string')
        text = text_clean
        return text, err


    # Remove endpoints
    def remove_endpoint(self, text, err):
        keyword = 'endpoint'
        sentenses = []
        for sent in text.split('\n'):
            if len(sent) > 0:
                if sent[-1] == '.':
                    sent = sent[:-1]
                sentenses.append(sent)
        text_clean = '\n'.join(sentenses)
        if text != text_clean:
            if keyword not in err.keys():
                err[keyword] = []
            err[keyword].append('remove endpoint')
        text = text_clean
        return text, err

    # Abbreviation
    def abbreviator(self, clean_text, text, err, diff):
        keyword = 'abbreviations'
        words = re.findall(r"\b[а-яёА-ЯË]{1,}\b", text)
        caps_list = re.findall(r"\b[А-ЯË]{2,}\b", text)
        for abb in words:
            if abb.upper() in self.bad_abb_list:
                err = self._add_err(err, keyword, 'restricted abbreviation', abb.upper())
                diff = self._highlight(diff, clean_text, abb)
            elif abb.upper() in self.abb_dict.keys():
                if abb[0].isupper():
                    text = text.replace(abb, self.abb_dict[abb.upper()].capitalize())
                else:
                    text = text.replace(abb, self.abb_dict[abb.upper()])
                err = self._add_err(err, keyword, abb, self.abb_dict[abb.upper()])
                diff = self._highlight(diff, clean_text, abb)
            elif abb.upper() in self.all_abb_list:
                text = text.replace(abb, abb.upper())
                if abb != abb.upper():
                    err = self._add_err(err, keyword, abb, abb.upper())
                    diff = self._highlight(diff, clean_text, abb)
            elif abb in caps_list:
                text = text.replace(abb, abb.lower())
                err = self._add_err(err, keyword, abb, abb.lower())
                diff = self._highlight(diff, clean_text, abb)
        return text, err, diff

    
    def _highlight(self, diff, text, abb):
        start = text.lower().find(abb.lower())
        stop = start + len(abb)
        diff[start:stop] = ['-'] * len(abb)
        return diff


    def _add_err(self, err, keyword, sent_a, sent_b):
        if keyword not in err.keys():
            err[keyword] = []
        err[keyword].append(sent_a + ' > ' + sent_b)
        return err

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