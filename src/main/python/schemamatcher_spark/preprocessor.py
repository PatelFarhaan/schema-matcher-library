import argparse
import sys
import time
import logging
from pyspark.sql import SparkSession
from schemamatcher.s3_storage import S3Storage

logger = logging.getLogger("Preprocessor")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

PREPROCESSOR_SPEC = [
    {
        "name": "sample_size",
        "command_line_arg": "--sample-size",
        "command_line_shorthand": "-s",
        "json": "sampleSize",
        "default": 1000
    }
]

# Columns returned by preprocessor
COLUMNS = ['dataset', 'column', 'values']

def get_storage(storage_config): # pragma : no cover
    """
    Get a Schemamatcher S3 storage object
    :param storage_config: Dictionary containing S3 bucket, access key, secret key and endpoint URL
    :return: Schemamatcher S3 Storage object
    """
    return S3Storage(
        bucket = storage_config['bucket'],
        access_key = storage_config['access_key'],
        secret_key = storage_config['secret_key'],
        endpoint_url = storage_config['endpoint_url']
    )

def get_sample(storage_config, table_id, sample_size):
    """
    Sample a table in the data lake
    :param storage_config: Dictionary containing S3 bucket, access key, secret key and endpoint URL
    :param table_id: path to the table within the bucket
    :param sample_size: number of samples to return
    :return: a Pandas dataframe of samples from the table
    """
    storage = get_storage(storage_config)
    return storage.sample(table_id, sample_size)

def map_table(df):
    """
    Map each column in the input dataframe to a list of traits
    :param df: a Pandas dataframe representing the input table
    :return: a list of lists, one list of traits per column in the table
    """
    return [map_column(df, column) for column in df.columns]

def map_column(df, column):
    """
    Map a column in the input dataframe to a list of traits
    :param df: a Pandas dataframe representing the input table
    :param column: name of the column to process
    :return: a list of traits for the input column
    """
    series = df[column]
    values = [value.lower() if type(value) == str else str(value).lower() for value in series]
    return [df.index.name, column, values]

def preprocess(spark, input_bucket, input_path, output_bucket, output_path, **kwargs): # pragma: no cover
    # Use defaults for optional arguments that haven't been specified
    for item in PROFILER_SPEC:
        var_name = item["name"]
        if var_name not in kwargs:
            kwargs[var_name] = item["default"]

    sc = spark.sparkContext
    
    # Collect S3 params in a storage_config object
    storage_config = {
        "bucket": input_bucket,
        "access_key": sc._jsc.hadoopConfiguration().get('fs.s3a.access.key'),
        "secret_key": sc._jsc.hadoopConfiguration().get('fs.s3a.secret.key'),
        "endpoint_url": sc._jsc.hadoopConfiguration().get('fs.s3a.endpoint')
    }

    # Get a Schemamatcher S3 storage object
    storage = get_storage(storage_config)

    # Create an RDD of table names
    tables_rdd = sc.parallelize(storage.search(input_path))

    # Sample each table and then map each column within each table to a list of traits and create an RDD from it
    column_data_rdd = tables_rdd.flatMap(lambda x: map_table(get_sample(storage_config, x, int(kwargs['sample_size']))))

    # Convert RDD to a Spark Dataframe 
    column_data_df = spark.createDataFrame(column_data_rdd).toDF(*COLUMNS)

    # Write out the dataframe as a parquet file
    column_data_df.write.parquet('s3a://{}/{}'.format(output_bucket, output_path))

def parse_args(argv):
    # Define command line arguments
    parser = argparse.ArgumentParser(description='Preprocess data lake info into a single table')
    parser.add_argument('input_bucket', help='S3 bucket where the data lake is stored')
    parser.add_argument('input_path', help='Path to data lake inside the input bucket')
    parser.add_argument('output_bucket', help='S3 bucket where table data is to be saved')
    parser.add_argument('output_path', help='Path for table data parquet file inside output bucket')

    # Define optional arguments
    for item in PREPROCESSOR_SPEC:
        parser.add_argument(item["command_line_shorthand"], item["command_line_arg"])

    # Parse command line arguments
    args = parser.parse_args(argv)

    # Parse optional arguments
    kwargs = {}
    dict_args = vars(args)
    for item in PREPROCESSOR_SPEC:
        var_name = item["name"]
        if var_name in dict_args and dict_args[var_name] is not None:
            kwargs[var_name] = dict_args[var_name]
    
    return (args.input_bucket, args.input_path, args.output_bucket, args.output_path, kwargs)

if __name__ == '__main__': # pragma: no cover
    input_bucket, input_path, output_bucket, output_path, kwargs = parse_args(sys.argv)
    
    logger.info("Preprocessing {}/{}".format(input_bucket, input_path))
    start_time = time.time()

    # Create a Spark session
    spark = SparkSession\
                .builder\
                .appName('preprocessor')\
                .getOrCreate()
    # Call preprocess
    preprocess(spark, input_bucket, input_path, output_bucket, output_path, **kwargs)

    end_time = time.time()
    logger.info("Execution time: {}s".format(end_time - start_time))
