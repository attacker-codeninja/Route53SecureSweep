#!/bin/bash

# Set the default region to us-east-1
export AWS_DEFAULT_REGION=us-east-1

# File to store RDS endpoint addresses
rds_domains_file="results/rds_domains.txt"
> "$rds_domains_file" # Empty the file if it exists

# Fetch list of all AWS regions
REGIONS=( $(aws ec2 describe-regions --query "Regions[].RegionName" --output text) )

# Function to describe RDS instances
describe_db_instances() {
  region=$1
  endpoint_addresses=( $(aws rds describe-db-instances --region $region --query 'DBInstances[*].Endpoint.Address' --output text) )

  # If no RDS instances in this region, print a message and skip the rest of the loop
  if [ -z "$endpoint_addresses" ]; then
    echo "No RDS instances found in region $region."
    return
  fi

  # Write the endpoints to the file

  printf "%s\n" "${endpoint_addresses[@]}" >> "$rds_domains_file"

}

# Run the function for each region
for region in "${REGIONS[@]}"; do
  describe_db_instances $region
done

# Unset the default region
unset AWS_DEFAULT_REGION

echo "Completed. RDS endpoints in results."
