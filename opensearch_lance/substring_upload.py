import polars
import sys
import json
import time
from opensearchpy import OpenSearch
from opensearchpy import helpers
import os
from subprocess import call
import warnings
from urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
# Suppress only the single InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
host = X
port = 9200
auth = (USER, PASS) # For testing only. Don't store credentials in code.
es = OpenSearch(
    hosts = [host],
    http_compress = True, # enables gzip compression for request bodies
    http_auth = auth,
    verify_certs = False,
    timeout = 60
)

files = sorted(os.listdir(sys.argv[1]))
for f in tqdm(files[int(sys.argv[3]): int(sys.argv[3]) + 128]):
    f = f"{sys.argv[1]}/{f}"
    start_time = time.time()
    actions = []
    count = 0
    tot = 0
    for line in polars.read_parquet(f)['text']:
        data = {}
        line = line.strip().replace("\'", "")
        data['text'] = line

        action = {}
        action['_index'] = sys.argv[2]
        action['_type'] = "test"
        action['_source'] = data
        if(count == 10000):
            helpers.bulk(es, actions)
            actions = []
            count = 0
        actions.append(action)
        count += 1
        tot += 1
        #print(tot)
    helpers.bulk(es, actions)

end_time = time.time()
time_cost = end_time - start_time
print("time cost: " + str(time_cost))
