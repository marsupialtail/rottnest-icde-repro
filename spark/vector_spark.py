import time
from pyspark.sql.types import StructType, StructField, BinaryType, IntegerType
import numpy as np
df = spark.read.parquet(f"s3a://{VECTOR_PARQUETS}/")
queries = np.load('queries.npy')
results = []
times = []
for query in queries[:40]:
    start = time.time()
    def vector_calc(iterator):
        import pyarrow
        import pyarrow.compute as pac
        for batch in iterator:
            arr = batch['vector']
            ids = batch['id'].to_numpy()
            buffers = arr.buffers()
            offsets = np.frombuffer(buffers[1], dtype = np.uint32)
            diffs = np.unique(offsets[1:] - offsets[:-1])
            assert len(diffs) == 1, "vectors have different length!"
            dim = diffs.item() // 4
            x = np.frombuffer(buffers[2], dtype = np.float32).reshape(len(arr), dim)
            distances = np.dot(query, x.T)
            indices = np.argpartition(-distances,kth=10)[:10]
            to_return = pac.cast(pyarrow.array(ids[indices]), pyarrow.int32())
            new_arr = pac.cast(pyarrow.array([arr[i] for i in indices]), pyarrow.binary())
            yield pyarrow.RecordBatch.from_arrays([to_return, new_arr], names = ['id', 'vector'])
    schema = StructType([StructField('id', IntegerType(), False), StructField('vector', BinaryType(), False)])
    result = df.mapInArrow(vector_calc, schema).repartition(1).mapInArrow(vector_calc,schema).toPandas()
    result['distance'] = result['vector'].apply(lambda x: np.frombuffer(x, dtype = np.float32).dot(query.astype(np.float32)))
    result = result.sort_values('distance')[-10:]['id'].to_list()
    results.append(result)
    print(result)
    times.append(time.time() - start)
    print(times[-1])