import pandas as pd
from schemamatcher.storage import Storage

class S3Storage(Storage): # pragma: no cover
    def __init__(self, bucket, **kwargs):
        import boto3
        from botocore.client import Config
        super().__init__(**kwargs)
        self.bucket = bucket
        access_key = kwargs.get("access_key", "")
        secret_key = kwargs.get("secret_key", "")
        endpoint_url = kwargs.get("endpoint_url", "")
        region_name = kwargs.get("region_name", "")
        self.client = boto3.client("s3",
                                   endpoint_url=endpoint_url,
                                   aws_access_key_id=access_key,
                                   aws_secret_access_key=secret_key,
                                   config=Config(signature_version="s3v4"),
                                   region_name=region_name
                                   )

    @property
    def identifier(self):
        return self.bucket

    def search(self, prefix):
        paginator = self.client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket, Prefix=prefix)

        li = []

        for page in pages:
            for item in page['Contents']:
                key = item['Key']
                if key.endswith('.csv'):
                    li.append(key)
        return li


    def search_all(self):
        paginator = self.client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket)

        li = []

        for page in pages:
            for item in page['Contents']:
                key = item['Key']
                if key.endswith('.csv'):
                    li.append(key)
        return li

    def read(self, table_id, **kwargs):
        url = self.client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self.bucket,
                'Key': table_id
            },
            ExpiresIn=300
        )
        try:
            df = pd.read_csv(url, encoding="utf-8", **kwargs)
        except UnicodeDecodeError:
            df = pd.read_csv(url, encoding="ISO-8859-1", **kwargs)
        df.index.name = table_id
        return df

    def write(self, schema, name, df):
        pass

    def sample(self, table_id, sample_size=500):
        import random

        # Count lines in file
        resp = self.client.select_object_content(
            Bucket=self.bucket,
            Key=table_id,
            ExpressionType='SQL',
            Expression="select count(*) from s3object s",
            InputSerialization={'CSV': {"FileHeaderInfo": "Use"}},
            OutputSerialization={'CSV': {}},
        )
        for event in resp['Payload']:
            if 'Records' in event:
                records = event['Records']['Payload'].decode('utf-8')
                num_lines = int(records)

        # Get file URL
        url = self.client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self.bucket,
                'Key': table_id
            },
            ExpiresIn=300
        )

        # Fraction of file to sample
        p = 1 if sample_size > num_lines else float(sample_size) / float(num_lines)

        # Read file into dataframe
        try:
            df = pd.read_csv(url, encoding="utf-8", header=0, skiprows=lambda i: i > 0 and random.random() > p)
        except UnicodeDecodeError:
            df = pd.read_csv(url, encoding="ISO-8859-1", header=0, skiprows=lambda i: i > 0 and random.random() > p)

        df.index.name = table_id
        return df

