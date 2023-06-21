#!/bin/bash


# Set the default region to us-east-1
export AWS_DEFAULT_REGION=us-east-1


# File to store public IPs and instance IDs
public_ips_file="results/public_ips.txt"
#instance_ids_file="results/instance_ids.txt"

# Empty the files if they exist
> "$public_ips_file"
#> "$instance_ids_file"

# Fetch list of all AWS regions
REGIONS=( $(aws ec2 describe-regions --query "Regions[].RegionName" --output text) )

# Function to describe instances
describe_instances() {
  region=$1
  instance_ids=( $(aws ec2 describe-instances --region $region --query 'Reservations[].Instances[].InstanceId' --output text) )

  # If no instances in this region, skip the rest of the loop
  if [ -z "$instance_ids" ]; then
    echo "No instances in region $region."
    return
  fi
  
  CHUNK_SIZE=100
  for (( i=0; i<${#instance_ids[@]}; i=i+CHUNK_SIZE )); do
    aws ec2 describe-instances --region $region --instance-ids ${instance_ids[@]:i:CHUNK_SIZE} --query 'Reservations[].Instances[].PublicIpAddress' --output text >> "$public_ips_file"
    #echo "${instance_ids[@]:i:CHUNK_SIZE}" >> "$instance_ids_file"
  done
}

# Run the function for each region
for region in "${REGIONS[@]}"; do
  describe_instances $region
done

# fix the tab characters

tr '\t' '\n' < results/public_ips.txt > results/public_ips_line_by_line.txt
mv results/public_ips_line_by_line.txt results/public_ips.txt

# Unset the default region
unset AWS_DEFAULT_REGION

echo "Completed. Public IPs are saved in results."
