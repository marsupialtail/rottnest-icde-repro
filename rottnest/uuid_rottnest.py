import polars
import time
import rottnest.internal as internal
queries = polars.read_parquet("uuid_benchmark.parquet")["query"].to_list()
results = []
times = []
for query in queries[:30]:
    start = time.time()
    result = internal.search_index_uuid([f"s3://{ROTTNEST_SUBSTRING_INDEX}/{i}" for i in range(NUM_INDEX_FILES)], query, 10)
    results.append(result)
    times.append(time.time() - start)