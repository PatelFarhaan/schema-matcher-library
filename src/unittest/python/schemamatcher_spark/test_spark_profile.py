from pyspark.sql import SparkSession
from schemamatcher_spark.profiler import profile, sample_column, parse_args, common_words_converter
from schemamatcher.utils.types import Type
import pandas as pd

class TestSparkProfiler():
    def prepare(self):
        spark = SparkSession.builder.master('local').appName("profiler").getOrCreate()
        self.df = spark.createDataFrame(
            [
                ('Stocks', 'ticker', ['APPL', 'AMZN']),
                ('Stocks', 'price', ['250.24', '1790.35'])
            ],
            ['dataset', 'column', 'values']
        )
        self.params = {
            'tokenizer_type': 'underscore',
            'random_state': 10,
            'output_sample_size': 10
        }

    def test_profile(self):
        self.prepare()
        df = profile(self.df, **self.params)
    def test_profiler_sample_column(self):
        values = ['string1', 'string2', 'string3', 'string4']
        sample = sample_column(values, 2)
        assert len(sample) == 2
        sample = sample_column(values, 10)
        assert len(sample) == 4
    def test_parse_args(self):
        input_path, output_path, kwargs = parse_args(['s3a://test/fake.parquet', 's3a://test/another_fake.parquet', '--tokenizer-type', 'underscore'])
        assert input_path == 's3a://test/fake.parquet'
        assert kwargs['tokenizer_type'] == 'underscore'
    def test_common_words_converter(self):
        itype = Type.Textual
        series = pd.Series([])
        from nltk.corpus import stopwords
        stop_words = set(stopwords.words('english'))
        drop_symbol_translator = str.maketrans('', '', ',./\'\"\\:;[]{}-_?!~`@#$%^&*()')
        common_words = common_words_converter(series, itype, stop_words, drop_symbol_translator)
        assert common_words == ['']
        series = pd.Series([
            "some jumble of words",
            "some more words",
            "just some text"
        ])
        common_words = common_words_converter(series, itype, stop_words, drop_symbol_translator)
        assert 'words' in common_words
