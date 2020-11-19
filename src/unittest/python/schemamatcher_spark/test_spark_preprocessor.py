from pyspark.sql import SparkSession
from schemamatcher_spark.preprocessor import get_sample, map_table, parse_args 
import pandas as pd

class TestSparkPreprocessor():
    def prepare(self):
        self.dataframe = pd.DataFrame([
            {
                'ticker': 'APPL',
                'company': 'Apple Computers',
                'price': 250.24,
                'date': '10/10/2019'
            },
            {
                'ticker': 'AMZN',
                'company': 'Amazon',
                'price': 1790.35,
                'date': '1/1/10'
            },
            {
                'ticker': 'XXXX',
                'price': '0',
                'date': ''
            },
        ])
        self.dataframe.index.name = 'Stocks'
    def test_map_column(self):
        self.prepare()
        li = map_table(self.dataframe)
    def test_parse_args(self):
        args = ['lake', 'courses', 'preprocessed_lakes', 'courses']
        input_bucket, input_path, output_bucket, output_path, kwargs = parse_args(args)
        assert kwargs == {}
        assert input_bucket == 'lake'
        assert input_path == 'courses'
        assert output_bucket == 'preprocessed_lakes'
        assert output_path == 'courses'
