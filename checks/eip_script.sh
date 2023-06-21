#!/bin/bash

# Set the default region to us-east-1
export AWS_DEFAULT_REGION=us-east-1

public_ip_file="results/public_eips.txt"
# File to store stale EIPs
stale_eip_file="results/stale_eip.txt"

# Empty the files if they exist
> "$public_ip_file"
> "$stale_eip_file"

# Fetch list of all AWS regions
REGIONS=( $(aws ec2 describe-regions --query "Regions[].RegionName" --output text) )

# Function to describe EIPs
describe_eips() {
  region=$1
  eips=( $(aws ec2 describe-addresses --region $region --query 'Addresses[].PublicIp' --output text) )

  # If no EIPs in this region, skip the rest of the loop
  if [ -z "$eips" ]; then
    echo "No EIPs in region $region."
    return
  fi
  
  for eip in "${eips[@]}"; do
    # Check if EIP is in public_ips.txt
    if grep -Fxq "$eip" "$public_ip_file"; then
      echo "EIP $eip found in $public_ip_file."
    else
      echo "EIP $eip not found in $public_ip_file."
      # Check if EIP is associated with an instance
      instance_id=$(aws ec2 describe-addresses --region $region --public-ips $eip --query 'Addresses[].InstanceId' --output text)
      if [ "$instance_id" == "None" ]; then
        echo "$eip" >> "$stale_eip_file"
        echo "EIP $eip is not associated with any instance, added to $stale_eip_file."
      fi
    fi
  done
}

# Run the function for each region
for region in "${REGIONS[@]}"; do
  describe_eips $region
done

# Unset the default region
unset AWS_DEFAULT_REGION

echo "Completed. Check the folder results."

