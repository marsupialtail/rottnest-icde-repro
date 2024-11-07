#!/bin/bash

# Create a bootstrap script
cat << EOF > bootstrap-actions.sh
#!/bin/bash
sudo python3 -m pip install polars pandas pyarrow numpy
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update
EOF

# Upload the bootstrap script to S3
aws s3 cp bootstrap-actions.sh s3://$BUCKET/bootstrap-actions.sh

# Create the EMR cluster
aws emr create-cluster \
    --name "learning" \
    --release-label emr-7.2.0 \
    --applications Name=Spark \
    --ec2-attributes KeyName=$KEY \
    --instance-type r6i.4xlarge \
    --instance-count $COUNT \
    --bootstrap-actions Path="s3://$BUCKET/bootstrap-actions.sh"
