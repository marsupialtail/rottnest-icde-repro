START=$1
END=$2
SHARD=$3

echo "Starting $START $END $SHARD"

cd /opt/dlami/nvme
aws s3 cp s3://cluster-dump/rottnest-1.4.0-cp38-abi3-manylinux_2_34_x86_64.whl .
pip3 install --break-system-packages --force-reinstall rottnest-1.4.0-cp38-abi3-manylinux_2_34_x86_64.whl
pip3 install --break-system-packages numpy==1.26.4

# seq -f "%g.parquet" ${START} ${END} | xargs -P 8 -I {} aws s3 cp "s3://sift-vecs/parquets/{}" "."

echo "import rottnest.internal as internal" > merge.py
for i in $(seq ${START} ${END}); do
    echo "internal.index_files_vector(['$(printf "%g.parquet" $i)'], 'vector', 'index$i', remote = 's3://sift-vecs/parquets/')" >> merge.py
done

python3 merge.py

mkdir indices;
mv index* indices/.;
# aws s3 sync indices/ s3://rottnest-indices/sift-index/
