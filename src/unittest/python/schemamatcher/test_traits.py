import pandas as pd
import nltk
from schemamatcher.utils.traits import get_word_freq, ValueFrequency, get_pattern, get_common_words

class TestTraits():
    def test_get_word_frequency(self):
        li = [
            "this is a sentence",
            "this is another sentence",
            "this is yet another sentence",
            "holy moly, one more sentence"
        ]
        series = pd.Series(li)
        freq = get_word_freq(series)
    def test_value_frequency(self):
        s1 = pd.Series(['hello', 'world', 'how', 'are', 'you'])
        s2 = pd.Series(['hello', 'some', 'overlap', 'world'])
        val_freq = ValueFrequency(s1)
        other = ValueFrequency(s2)
        jac = val_freq.jaccard(other)
        ol = val_freq.overlap(other)
        ser = str(val_freq)
        val_freq = ValueFrequency.deserialize(ser)
        val_freq = ValueFrequency.deserialize('')
        assert val_freq == None
        val_freq = ValueFrequency.deserialize(None)
        assert val_freq == None
    def test_get_pattern(self):
        number = '+1-608-770-2345'
        pattern = get_pattern(number)
        assert pattern == '+9 999 999 9999'
    def test_get_common_words(self):
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        from nltk.corpus import stopwords
        stop_words = set(stopwords.words('english'))
        drop_symbol_translator = str.maketrans('', '', ',./\'\"\\:;[]{}-_?!~`@#$%^&*()')
        series = pd.Series([1, 2, 3])
        cw = get_common_words(series, stop_words, drop_symbol_translator)
        assert cw == []
