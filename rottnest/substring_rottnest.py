import polars
import time
import rottnest.internal as internal
queries = polars.read_parquet("substring_benchmark.parquet")["query"].to_list()
results = []
times = []
for query in queries[:20]:
    start = time.time()
    result = internal.search_index_substring([f"s3://{ROTTNEST_SUBSTRING_INDEX}/{i}" for i in range(NUM_INDEX_FILES)], query, 10, token_viable_limit=10, sample_factor = 2)
    results.append(result)
    times.append(time.time() - start)