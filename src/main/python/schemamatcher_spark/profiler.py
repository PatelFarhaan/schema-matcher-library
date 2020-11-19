import argparse
import time
import sys
import pandas as pd
import statistics
import logging

from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, ArrayType, LongType, DoubleType, IntegerType
from pyspark.sql.functions import udf, struct, collect_list, monotonically_increasing_id
from pyspark.ml import Pipeline
from pyspark.ml.feature import MinHashLSH, HashingTF

from schemamatcher.utils.tokenizers import get_tokenizer
from schemamatcher.utils.types import infer_type, Type
from schemamatcher.utils.traits import get_pattern, get_common_words, get_word_freq

import nltk
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', download_dir='/opt/spark/work-dir')
    nltk.data.path.append('/opt/spark/work-dir')
from nltk.corpus import stopwords

logger = logging.getLogger("Profiler")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

PROFILER_SPEC = [
    {
        "name": "tokenizer_type",
        "command_line_arg": "--tokenizer-type",
        "command_line_shorthand": "-t",
        "json": "tokenizerType",
        "default": "underscore"
    },
    {
        "name": "random_state",
        "command_line_arg": "--random-state",
        "command_line_shorthand": "-r",
        "json": "randomState",
        "default": 10
    },
    {
        "name": "output_sample_size",
        "command_line_arg": "--output-sample-size",
        "command_line_shorthand": "-s",
        "json": "outputSampleSize",
        "default": 10
    }
]

COLUMNS = [
    "_id", "index", "dataset", "column", "column_lower", "word_tokens", 
    "three_gram_tokens", "three_gram_nv_tokens", "itype", "common_words", "mean_value", "median_value",  
    "length", "unique_count", "minhash_name_three_grams", "minhash_name_nv_three_grams", "minhash_name_words", 
    "minhash_content_patterns", "minhash_content_values", "minhash_content_common_words", "word_freq", 
    "sample"
]

def minhash_converter(hashes):
    """
    Serialize the minhash
    :param hashes: Pyspark dense vector of hashes
    :return: Serialized string of hashes
    """
    return [int(x) for y in hashes for x in y]

def sample_column(values, sample_size):
    """
    Sample a list of values
    :param values: list to sample from
    :param sample_size: sample size
    :return: list of samples
    """
    ds = pd.Series(values).dropna()
    ds = ds.sample(sample_size) if len(ds) > sample_size else ds
    sample = list()
    for value in ds:
        sample.append(str(value))
    return sample

def common_words_converter(series, itype, stop_words, drop_symbol_translator):
    """
    Generate common words list for textual columns
    :param series: Pandas series of values
    :param itype: column type
    :param drop_symbol_translator: a drop symbol translator
    :return: list of common words in the column
    """
    common_words = get_common_words(series, stop_words, drop_symbol_translator) \
        if not (itype & Type.Numeric) and not (itype & Type.Datetime) else ['']
    if len(common_words) == 0:
        common_words = ['']
    return common_words

def generate_traits(df, params):
    """
    Generate column traits from the column infor stored in a a Spark dataframe
    :param df: Spark dataframe of column info
    :param params: optional parameters as defined in PROFILER_SPEC
    :return: Spark dataframe with column traits
    """
    # Add an _id column
    df = df.withColumn('_id', monotonically_increasing_id())
    
    # Index column = dataset/column
    index_udf = udf(lambda x: "{}/{}".format(x[0], x[1]), StringType())
    df = df.withColumn("index", index_udf(struct("dataset", "column")))

    # Column names in lower case
    lower_case_udf = udf(lambda x: x.lower(), StringType())
    df = df.withColumn("column_lower", lower_case_udf("column"))

    # Column name tokens
    word_tokenizer_udf = udf(lambda x: get_tokenizer(params["tokenizer_type"]).tokenize(x), ArrayType(StringType()))
    df = df.withColumn("word_tokens", word_tokenizer_udf("column"))

    # Column name three gram tokens
    three_gram_tokenizer_udf = udf(lambda x: get_tokenizer('three_gram').tokenize(x), ArrayType(StringType()))
    df = df.withColumn("three_gram_tokens", three_gram_tokenizer_udf("column_lower"))

    # Column name three gram tokens without vowels
    drop_vowel_translator = str.maketrans('', '', 'aeiou')
    three_gram_nv_tokenizer_udf = udf(lambda x: get_tokenizer('three_gram').tokenize(x.translate( \
        drop_vowel_translator)), ArrayType(StringType()))
    df = df.withColumn("three_gram_nv_tokens", three_gram_nv_tokenizer_udf("column_lower"))

    # Column itype
    itype_udf = udf(lambda x: str(infer_type(pd.Series(x), random_state=params['random_state'])), StringType()) 
    df = df.withColumn("itype", itype_udf("values"))
    
    # List of common words in the column
    drop_symbol_translator = str.maketrans('', '', ',./\'\"\\:;[]{}-_?!~`@#$%^&*()')
    stop_words = set(stopwords.words('english'))
    common_words_udf = udf(lambda x: common_words_converter(pd.Series(x[0]), Type.deserialize(x[1]), stop_words, drop_symbol_translator), ArrayType(StringType()))
    df = df.withColumn("common_words", common_words_udf(struct("values", "itype")))

    # Mean of numeric columns
    mean_udf = udf(lambda x: pd.Series(x[0]).mean() if Type.deserialize(x[1]) & Type.Numeric else None, DoubleType())
    df = df.withColumn("mean_value", mean_udf(struct("values", "itype")))

    # Median of numeric columns
    median_udf = udf(lambda x: pd.Series(x[0]).median() if Type.deserialize(x[1]) & Type.Numeric else None, DoubleType())
    df = df.withColumn("median_value", median_udf(struct("values", "itype")))

    # Average length of column values
    avg_length_udf = udf(lambda x: statistics.mean(list(map(lambda y: len(str(y)), x))), DoubleType())
    df = df.withColumn("length", avg_length_udf("values"))

    # Number of unique entries in the column
    unique_count_udf = udf(lambda x: pd.Series(x).nunique(), IntegerType())
    df = df.withColumn("unique_count", unique_count_udf("values"))

    # List of patterns of column values
    patterns_udf = udf(lambda x: list(map(lambda y: get_pattern(y), x)), ArrayType(StringType()))
    df = df.withColumn("patterns", patterns_udf("values"))

    # Dictionary of value frequencies for textual columns
    word_freq_udf = udf(lambda x: str(get_word_freq(pd.Series(x[0]))) if Type.deserialize(x[1]) & Type.Textual else '', StringType())
    df = df.withColumn("word_freq", word_freq_udf(struct("values", "itype")))

    # Value samples
    sample_udf = udf(lambda x: sample_column(x, params['output_sample_size']), ArrayType(StringType()))
    df = df.withColumn("sample", sample_udf("values"))

    return df

def compute_hashes(df):
    """
    Compute LSH minhashes for column traits
    :param df: Spark dataframe containing column traits
    :return Spark dataframe with serialized minhash columns appended
    """
    # Define pipeline for computing LSH minhashes for six columns:
    # three_gram, three_gram_nv, values, word_tokens, patterns and common words
    stages = [
        HashingTF(inputCol="three_gram_tokens", outputCol="three_gram_vectors"),
        MinHashLSH(inputCol="three_gram_vectors", outputCol="three_gram_hashes_array", numHashTables=128),
        HashingTF(inputCol="three_gram_nv_tokens", outputCol="three_gram_nv_vectors"),
        MinHashLSH(inputCol="three_gram_nv_vectors", outputCol="three_gram_nv_hashes_array", numHashTables=128),
        HashingTF(inputCol="values", outputCol="value_vectors"),
        MinHashLSH(inputCol="value_vectors", outputCol="value_hashes_array", numHashTables=128),
        HashingTF(inputCol="word_tokens", outputCol="word_token_vectors"),
        MinHashLSH(inputCol="word_token_vectors", outputCol="word_token_hashes_array", numHashTables=128),
        HashingTF(inputCol="patterns", outputCol="pattern_vectors"),
        MinHashLSH(inputCol="pattern_vectors", outputCol="pattern_hashes_array", numHashTables=128),
        HashingTF(inputCol="common_words", outputCol="common_words_vectors"),
        MinHashLSH(inputCol="common_words_vectors", outputCol="common_words_hashes_array", numHashTables=128)
    ]

    # Computes Minhashes
    model = Pipeline(stages=stages).fit(df)
    df = model.transform(df)

    # Define a UDF for serializing the hashes
    minhash_conv_udf = udf(lambda x: minhash_converter(x), ArrayType(LongType()))

    # Apply the UDF to serialize the hashes
    df = df.withColumn("minhash_name_three_grams", minhash_conv_udf(df.three_gram_hashes_array))
    df = df.withColumn("minhash_name_nv_three_grams", minhash_conv_udf(df.three_gram_nv_hashes_array))
    df = df.withColumn("minhash_content_values", minhash_conv_udf(df.value_hashes_array))
    df = df.withColumn("minhash_content_patterns", minhash_conv_udf(df.pattern_hashes_array))
    df = df.withColumn("minhash_name_words", minhash_conv_udf(df.word_token_hashes_array))
    df = df.withColumn("minhash_content_common_words", minhash_conv_udf(df.common_words_hashes_array))

    return df

def profile(df, **kwargs):
    """
    Prepares a spark dataframe of column profiles for the table data stored at input path
    :param input_path: input path to a parquet file of table data. Format |dataset|column|values|
    :param kwargs: optional parameters for the profiler
    :return: spark dataframe of column traits
    """
    # Use defaults for optional arguments that haven't been specified
    for item in PROFILER_SPEC:
        var_name = item["name"]
        if var_name not in kwargs:
            kwargs[var_name] = item["default"]

    # Generate traits for each row of the input file
    df = generate_traits(df, kwargs)

    # Compute LSH Minhashes
    df = compute_hashes(df)

    # Select columns for the final output
    df = df.select(*COLUMNS)
    
    return df

def parse_args(argv):
    # Define command line arguments
    parser = argparse.ArgumentParser(description="Profiler for Schema Matching")
    parser.add_argument("input_path", help="Path to column data")
    parser.add_argument("output_path", help="Path where traits parquet file should be written")
    
    # Define optional arguments
    for item in PROFILER_SPEC:
        parser.add_argument(item["command_line_shorthand"], item["command_line_arg"])
    
    # Parse command line arguments
    args = parser.parse_args(argv)

    # Parse optional arguments
    kwargs = {}
    dict_args = vars(args)
    for item in PROFILER_SPEC:
        var_name = item["name"]
        if var_name in dict_args and dict_args[var_name] is not None:
            kwargs[var_name] = dict_args[var_name]
    return (args.input_path, args.output_path, kwargs)

if __name__ == "__main__": # pragma: no cover
    input_path, output_path, kwargs = parse_args(sys.argv[1:])

    logger.info("Input path: {}, Outputpath:{}".format(args.input_path, args.output_path))
    start_time = time.time()

    # Create a spark session
    spark = SparkSession\
                .builder\
                .appName("profiler")\
                .getOrCreate()
    sc = spark.sparkContext

    # Read in the input file 
    df = spark.read.parquet(input_path)

    # Run the profiler
    profiles_df = profile(df, **kwargs) 

    # Write an output parquet file
    profiles_df.write.parquet(output_path)
    
    end_time = time.time()
    logger.info("Execution time: {}s".format(end_time - start_time))
