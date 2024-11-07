START=$1
END=$2
SHARD=$3

echo "Starting $START $END $SHARD"

sudo mkfs.ext4 /dev/nvme1n1
sudo mount /dev/nvme1n1 /data
sudo chmod 777 /data
cd /data

aws s3 cp s3://$X/rottnest-1.4.0-cp38-abi3-manylinux_2_34_x86_64.whl .
pip3 install --break-system-packages --force-reinstall rottnest-1.4.0-cp38-abi3-manylinux_2_34_x86_64.whl

seq -f "c4-train.%05g-of-01024.parquet" ${START} ${END} | xargs -P 8 -I {} aws s3 cp "s3://c4-benchmark/{}" "."

echo "import rottnest.internal as internal" > merge.py
for i in $(seq ${START} ${END}); do
    echo "internal.index_files_substring(['$(printf "c4-train.%05d-of-01024.parquet" $i)'], 'text', 'index$i', token_skip_factor = 2, remote = 's3://c4-benchmark/')" >> merge.py
done
python3 merge.py
mkdir indices; 
mv index* indices/.; 
aws s3 sync indices/ s3://${INDEX_NONMERGED}

python3 -c "import rottnest.internal as internal; internal.merge_index_substring('merged_index', [f'indices/index{i}' for i in range($START, $END + 1)])"

aws s3 cp merged_index.meta s3://${INDEX}/$SHARD.meta
aws s3 cp merged_index.lava s3://${INDEX}/$SHARD.lava
