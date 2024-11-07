# Rottnest ICDE reproduction

We have included a pre-compiled wheel of Rottnest 1.4.0 used in the evaluation. Rottnest is an active project that is maintained [here](https://github.com/marsupialtail/rottnest).

## Data
We use the C4 dataset from Fineweb, download [here]: https://huggingface.co/datasets/HuggingFaceFW/fineweb. The data starts at 1024 files which we convert into Parquet. Upload to S3.

For UUID, we generate 200 Parquet files each with 10M rows of 128-byte UUIDs. Upload to S3.

For vector search, we use the SIFT 1B dataset [here]: http://corpus-texmex.irisa.fr/. We use the associated ground truth labels and queries for recall and latency evaluation. The data is converted into Parquet files with the vectors stored as binary. Upload to S3.

## OpenSearch/LanceDB
See the opensearch_lance folder for ncessary scripts. You can launch an OpenSearch cluster in the AWS UI. For experiments here we use three r6g.large instances with EBS volumes. Assuming the data is on disk, uuid_upload.py and substring_upload.py can be used to populate the index. For LanceDB we use lance.py.

## Brute Force
See the spark folder for necessary scripts. Launch a cluster with emr.sh. After the cluster is launched log into the head node with `aws emr ssh -- cluster-id`, then launch PySpark and run the scripts. r6i.4xlarge instances are used to run this experiment.

## Rottnest
See the rottnest folder for necessary scripts. To build indices, use the index_* scripts. You can parallelize this process by running the scripts on multiple instances by using submit.sh. The search is done single node with the substring_rottnest.py etc. r6id.4xlarge instances are used for indexing for this paper for the substring and uuid experiments. g4dn.8xlarge instances are used for the vector indexing.

## Plots
The plots are generated using the Jupyter notebook plots.ipynb.
