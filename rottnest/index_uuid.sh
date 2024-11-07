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

seq -f "%g.parquet" ${START} ${END} | xargs -P 8 -I {} aws s3 cp "s3://${DATA}/{}" "."

echo "import rottnest.internal as internal" > merge.py
for i in $(seq ${START} ${END}); do
    echo "internal.index_files_uuid(['$(printf "%g.parquet" $i)'], 'hashes', 'index$i', remote = 's3://${DATA}/')" >> merge.py
done
echo "internal.merge_index_uuid('merged_index', [f'index{i}' for i in range($START, $END + 1)])" >> merge.py

python3 merge.py

mkdir indices; 
mv index* indices/.; 
aws s3 sync indices/ s3://${INDEX_NONMERGED}

aws s3 cp merged_index.meta s3://${INDEX}/$SHARD.meta
aws s3 cp merged_index.lava s3://${INDEX}/$SHARD.lava
