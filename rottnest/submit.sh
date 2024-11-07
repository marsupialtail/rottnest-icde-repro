#!/bin/bash

# Array of IP addresses
IPS=(  
)
aws s3 cp $SCRIPT s3://$X/$SCRIPT
aws s3 cp dist/rottnest-1.4.0-cp38-abi3-manylinux_2_34_x86_64.whl s3://$X/rottnest-1.4.0-cp38-abi3-manylinux_2_34_x86_64.whl
for i in "${!IPS[@]}"; do
  ip="${IPS[$i]}"
  ssh -o StrictHostKeyChecking=no -i /home/ziheng/Downloads/zihengw-new.pem ubuntu@"$ip" "aws s3 cp s3://$X/$SCRIPT ."
done
for i in "${!IPS[@]}"; do
  ip="${IPS[$i]}"  
  ssh -o StrictHostKeyChecking=no -i /home/ziheng/Downloads/zihengw-new.pem ubuntu@"$ip" "nohup bash $SCRIPT $((i * 1000)) $((i * 1000 + 999)) $i > nohup.log &" &
done
echo "All jobs submitted"
