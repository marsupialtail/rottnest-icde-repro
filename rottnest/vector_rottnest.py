import rottnest.internal as internal
import numpy as np
import time
import sys
from tqdm import tqdm

queries = np.load('queries.npy')
results = []
times = []
for q in tqdm(range(30)):
    start = time.time()
    result = internal.search_index_vector([f"s3://{ROTTNEST_INDEX_VECTOR}/{i}" for i in range(NUM_INDEX_FILES)], queries[q], 10, columns = ['id'], nprobes = 15, refine= 15)['id'].to_list()
    times.append(time.time() - start)
    results.append(result)

print(results)