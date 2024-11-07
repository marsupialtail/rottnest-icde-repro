import pyspark.sql.functions as F
import polars
import time
x = polars.read_parquet("substring_benchmark.parquet")
queries = x['query'].to_list()
df = spark.read.parquet(f's3a://{C4_PARQUETS}/')

times = []

for i in range(40):
    start = time.time()
    result = df.filter(F.col('text').contains(queries[i])).collect()
    print(len(result))
    times.append(time.time() - start)