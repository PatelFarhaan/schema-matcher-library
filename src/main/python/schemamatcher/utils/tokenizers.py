import re
from py_stringmatching import AlphabeticTokenizer, AlphanumericTokenizer, DelimiterTokenizer, QgramTokenizer, \
    WhitespaceTokenizer


class UppercaseTokenizer:
    """Returns tokens that are maximal sequences separated by upper case characters"""

    def __init__(self, return_set=False):
        """
        :param return_set: A flag to indicate whether to return tokens in a set instead of a list (default: False)
        """
        self.return_set = return_set

    def get_return_set(self):
        """
        Gets the value of the return_set flag.
        :return: The boolean value of the return_set flag.
        """
        return self.return_set

    def set_return_set(self, return_set):
        """
        Sets the value of the return_set flag.
        :param return_set: A flag to indicate whether to return tokens in a set instead of a list (default: False)
        :return:
        """
        self.return_set = return_set

    def tokenize(self, input_string):
        """
        Tokenizes input string into alphanumeric tokens
        :param input_string:  The string to be tokenized.
        :return: A Python list of tokens if the flag return_set is False, a set of tokens otherwise.
        """
        result = re.findall(r'\A[a-zA-Z][^A-Z]*|[A-Z][^A-Z]*', input_string)
        return set(result) if self.return_set else result


class SmartTokenizer:
    """"Returns tokens separated by special delimiters (currently, capitalized letters and symbols)"""

    def __init__(self, capitalized=False, symbol=False, return_set=False):
        """
        :param capitalized: A flag to indicate whether to tokenize by capitalized letters (default: False)
        :param symbol: A flag to indicate whether to tokenize by symbols (default: False)
        :param return_set: A flag to indicate whether to return tokens in a set instead of a list (default: False)
        """
        self.capitalized = capitalized
        self.symbol = symbol
        self.return_set = return_set

    def get_return_set(self):
        """
        Gets the value of the return_set flag.
        :return: The boolean value of the return_set flag.
        """
        return self.return_set

    def set_return_set(self, return_set):
        """
        Sets the value of the return_set flag.
        :param return_set: A flag to indicate whether to return tokens in a set instead of a list (default: False)
        :return:
        """
        self.return_set = return_set

    def tokenize(self, input_string):
        """
        Tokenizes input string into alphanumeric tokens
        :param input_string:  The string to be tokenized.
        :return: A Python list of tokens if the flag return_set is False, a set of tokens otherwise.
        """
        result = re.findall(r'\A[a-zA-Z][^A-Z]*|[A-Z][^A-Z]*', input_string) if self.capitalized else [input_string]
        temp_list = []
        if self.symbol:
            for token in result:
                temp_list.extend(re.split('[-_.]', token))
            result = temp_list

        result = list(filter(None, result))
        return set(result) if self.return_set else result


class AllSequencesTokenizer(SmartTokenizer):
    def __init__(self, capitalized=False, symbol=False, return_set=False):
        """
        :param capitalized: A flag to indicate whether to tokenize by capitalized letters (default: False)
        :param symbol: A flag to indicate whether to tokenize by symbols (default: False)
        :param return_set: A flag to indicate whether to return tokens in a set instead of a list (default: False)
        """
        super().__init__(capitalized, symbol, return_set)

    def tokenize(self, input_string):
        """
        Tokenizes input string into alphanumeric tokens
        :param input_string:  The string to be tokenized.
        :return: A Python list of tokens if the flag return_set is False, a set of tokens otherwise.
        """
        base_tokens = list(super().tokenize(input_string))
        tokens = []
        for index, base_token in enumerate(base_tokens):
            for last_index in range(len(base_tokens), index, -1):
                tokens.append(" ".join(base_tokens[index:last_index]))
        return set(tokens) if self.return_set else tokens


# Instantiate tokenizers
alphabetic = AlphabeticTokenizer()
alphanumeric = AlphanumericTokenizer()
space = DelimiterTokenizer()
underscore = DelimiterTokenizer({'_'})
dash = DelimiterTokenizer({'-'})
combo: DelimiterTokenizer = DelimiterTokenizer({' ', '_', '-'})
uppercase = UppercaseTokenizer()
whitespace = WhitespaceTokenizer()
one_gram = QgramTokenizer(qval=1)
two_gram = QgramTokenizer(qval=2)
three_gram = QgramTokenizer(qval=3)
four_gram = QgramTokenizer(qval=4)
five_gram = QgramTokenizer(qval=5)
smart_all = SmartTokenizer(capitalized=True, symbol=True)
smart_capitalized = SmartTokenizer(capitalized=True)
smart_symbol = SmartTokenizer(symbol=True)
smart_all_set = SmartTokenizer(capitalized=True, symbol=True, return_set=True)
sequences_all = AllSequencesTokenizer(capitalized=True, symbol=True, return_set=False)

tokenizer_dict = {
    'alphabetic': alphabetic,
    'alphanumeric': alphanumeric,
    'space': space,
    'underscore': underscore,
    'dash': dash,
    'combo': combo,
    'uppercase': uppercase,
    'whitespace': whitespace,
    'one_gram': one_gram,
    'two_gram': two_gram,
    'three_gram': three_gram,
    'four_gram': four_gram,
    'five_gram': five_gram,
    'smart': smart_all,
    'sequence': sequences_all
}


def get_tokenizer(identifier):
    return tokenizer_dict.get(identifier, None)

