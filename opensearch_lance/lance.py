import glob
import os
import numpy as np
import pyarrow as pa

os.environ["LANCE_LOG"] = "info"

import lance
from lance.indices import IndicesBuilder, IvfModel, PqModel

# Settings used to debug script and test locally

# The directory containing the npy files, must be on the local disk
NPY_DIR = None
# The number of NPY files
NUM_NPY_FILES = 100
# The URL where the lance dataset should go, can be local or cloud, can also be an absolute path
DS_URL = "s3://{X}/{Y}"
# Base URL for saving snapshot artifacts, can also be an absolute path
SNAPSHOT_BASE = "s3://{X}"
# Directory for storing temp files (must be local absolute path)
WORKDIR = os.getcwd()

# Parameters for the index
NUM_PARTITIONS = 10000
NUM_SUBVECTORS = 32

try:
    ds = lance.dataset(DS_URL)
    num_rows = ds.count_rows()
    if num_rows != 10_000_000 * NUM_NPY_FILES:
        raise Exception("Not all data uploaded")
    print(f"Using existing dataset at {DS_URL} with {num_rows} rows")
except:
    print(f"Uploading new dataset since no existing dataset could be found")
    offset = 0
    for npy_idx in range(NUM_NPY_FILES):
        path = f"{NPY_DIR}/{npy_idx}.npy"
        print(f"Uploading {path} to {DS_URL}")
        arr = pa.array(np.load(path).astype(np.float32))
        arr = pa.FixedSizeListArray.from_arrays(arr, 128)
        row_ids = pa.array(range(offset, offset + len(arr)))
        offset += len(arr)
        table = pa.table({
            "vector": arr,
            "row_number": row_ids
        })
        lance.write_dataset(table, DS_URL, mode="append", data_storage_version="stable")

    print("Dataset upload complete")
    ds = lance.dataset(DS_URL)
    
builder = IndicesBuilder(ds, "vector")

ivf_path = f"{SNAPSHOT_BASE}/sift-lance-ivf-big.lance"
try:
    ivf = IvfModel.load(ivf_path)
    print("Using previously trained IVF model")
except:
    print("Training IVF model")
    ivf = builder.train_ivf(num_partitions=NUM_PARTITIONS, accelerator="cuda")
    ivf.save(ivf_path)

pq_path = f"{SNAPSHOT_BASE}/sift-lance-pq-big.lance"
try:
    pq = PqModel.load(pq_path)
    print("Using previously trained PQ model")
except:
    print("Training PQ model")
    pq = builder.train_pq(ivf, num_subvectors=NUM_SUBVECTORS)
    pq.save(pq_path)

print("Quantizing dataset vectors and assigning to IVF partitions")
builder.transform_vectors(ivf, pq, f"{WORKDIR}/unsorted-sift")
print("Sorting quantized vectors by partition")
builder.shuffle_transformed_vectors(["unsorted-sift"], WORKDIR, ivf, "sorted")

print("Uploading completed index to dataset")
filenames = glob.glob(f"sorted*", root_dir=WORKDIR)
builder.load_shuffled_vectors(filenames, WORKDIR, ivf, pq)
print("Index building complete.  Printing indices")
print(lance.dataset(DS_URL).list_indices())