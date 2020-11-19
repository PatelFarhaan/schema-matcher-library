from abc import abstractmethod
from schemamatcher import logger
import pandas as pd

class Storage: # pragma: no cover
    def __init__(self, **kwargs):
        self.random_state = kwargs['random_state'] if 'random_state' in kwargs else 10

    @property
    @abstractmethod
    def identifier(self):
        """Returns a unique identifier for the storage"""
        pass

    @abstractmethod
    def search(self, search_string):
        """Returns a list of table ids whose names match the given search string"""
        pass

    @abstractmethod
    def search_all(self):
        """Returns a list of table ids """
        pass

    @abstractmethod
    def read(self, table_id, **kwargs):
        pass

    @abstractmethod
    def write(self, schema, name, df):
        pass

    def sample(self, table_id, sample_size=500):
        """
        Returns a pandas data frame of samples for the requested table (csv file)
        :param table_id: Id of the table that needs to be read
        :param sample_size: Max number of rows to sample (default: 500)
        :return:
        """
        df = self.read(table_id)
        df = df.sample(sample_size, random_state=self.random_state) if df.shape[0] > sample_size else df
        # changed the attribute being set from df.__table_name__ to df.index.name as the former is not serialized
        df.index.name = table_id
        return df

    def samples(self, search_string, sample_size=500):
        """
        Yields a pandas data frames of samples for each table that matches the search string
        :param search_string: search string for required tables
        :param sample_size: Max number of rows to sample. Default 500
        :return: yield a pandas dataframe for tables that match the search string
        """
        logger.info("Maximum sample size {}".format(sample_size))
        for table_id in self.search(search_string):
            df = self.sample(table_id, sample_size)
            logger.info("{} rows sampled from {}".format(df.shape[0], df.index.name))
            yield (df)

