from schemamatcher.utils.tokenizers import get_tokenizer, SmartTokenizer, AllSequencesTokenizer

class TestTokenizer():
    def test_upper_case_tokenizer(self):
        column = 'SomeColumnName'
        tokenizer = get_tokenizer('uppercase')
        tokenizer.set_return_set(False)
        assert tokenizer.get_return_set() == False
        tokens = tokenizer.tokenize(column)
        assert tokens[0] == 'Some'
        assert tokens[1] == 'Column'
        assert tokens[2] == 'Name'
    def test_smart_tokenizer(self):
        column = 'some-column-name'
        tokenizer = get_tokenizer('smart')
        tokenizer.capitalized = False
        tokenizer.set_return_set(False)
        assert tokenizer.get_return_set() == False
        tokens = tokenizer.tokenize(column)
        assert tokens[0] == 'some'
        assert tokens[1] == 'column'
        assert tokens[2] == 'name'
        column = 'some-column-name'
        tokenizer = SmartTokenizer(capitalized=True, return_set=True)
        tokens = tokenizer.tokenize(column)
    def test_all_sequences_tokenizer(self):
        column = 'some-column-name'
        tokenizer = AllSequencesTokenizer(capitalized=True, return_set=True)
        tokens = tokenizer.tokenize(column)
        tokenizer = AllSequencesTokenizer(capitalized=True)
        tokens = tokenizer.tokenize(column)
