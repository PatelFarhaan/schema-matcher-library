from ast import literal_eval
import pandas as pd
from py_stringmatching import Jaccard, OverlapCoefficient
import re
from collections import Counter


class ValueFrequency:
    def __init__(self, value_frequency_series):
        self.value_frequency_series = value_frequency_series

    def overlap(self, other, count=None):
        self_list = self.value_frequency_series.index.tolist()[0:count]
        other_list = other.value_frequency_series.index.tolist()[0:count]
        return OverlapCoefficient().get_sim_score(self_list, other_list)

    def jaccard(self, other, count=None):
        self_list = self.value_frequency_series.index.tolist()[0:count]
        other_list = other.value_frequency_series.index.tolist()[0:count]
        return Jaccard().get_sim_score(self_list, other_list)

    def __str__(self):
        return str(self.value_frequency_series.to_dict())

    @staticmethod
    def deserialize(string):
        if string == '' or string is None:
            vf = None
        else:
            vf = ValueFrequency(pd.Series(literal_eval(string)))
        return vf


def get_pattern(value):
    """
    Extracts pattern out of the value specified
    :param value: Input value whose pattern is required
    :return: str pattern
    """
    # Need better regular expressions for doing this
    value = value if type(value) == str else str(value)
    value = re.sub(r'\d', '9', value)
    value = re.sub('[a-z]', 'x', value)
    value = re.sub(r'\(', '', value)
    value = re.sub(r'\)', ' ', value)
    value = re.sub(r'-', ' ', value)
    value = re.sub('[ ]{2,}', ' ', value)
    return value


def get_common_words(series, stop_words, drop_symbol_translator):
    """
    Computes top 10 commonly used words of the given column of a series
    :param series: input series to find commonly used words
    :param drop_symbol_translator:
    :param stop_words:
    :return: top 10 commonly used words as a list
    """
    word_count = dict()

    for index, row in series.iteritems():
        if type(row) != str:
            continue

        words = row.split()

        for word in words:
            processed_word = word.translate(drop_symbol_translator)
            processed_word = processed_word.lower()
            if not processed_word or processed_word not in stop_words:
                if processed_word not in word_count:
                    word_count[processed_word] = 1
                else:
                    word_count[processed_word] += 1

    return [common_word for common_word, count in Counter(word_count).most_common(10)]


def get_word_freq(series):
    ds = series.str.replace(r'[^a-zA-Z\s]', '')
    ds = ds[ds.notnull()]
    try:
        ds = pd.DataFrame(ds.str.split().tolist()).stack().reset_index(drop=True)
    except IndexError:
        return None
    return ValueFrequency(ds.str.lower().value_counts()[0:30])
