import pyspark.sql.functions as F

import time
import polars

x = polars.read_parquet("uuid_benchmark.parquet")
queries = x['query'].to_list()
df = spark.read.parquet(f"s3a://{HASH_PARQUETS}")

times = []
for i in range(50):
    start = time.time()
    result = df.filter(F.col('hashes') == queries[i]).collect()
    assert len(result) == 1
    times.append(time.time() - start)