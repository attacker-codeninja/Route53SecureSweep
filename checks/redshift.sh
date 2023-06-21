#!/bin/bash

# Set the default region to us-east-1
export AWS_DEFAULT_REGION=us-east-1

# File to store Redshift endpoint addresses
redshift_endpoints_file="results/redshift_endpoints.txt"

# Empty the file if it exists
> "$redshift_endpoints_file"

# Fetch list of all AWS regions
REGIONS=( $(aws ec2 describe-regions --query "Regions[].RegionName" --output text) )

# Function to describe Redshift clusters
describe_redshift_clusters() {
  region=$1
  endpoints=( $(aws redshift describe-clusters --region $region --query 'Clusters[*].Endpoint.Address' --output text) )

  # If no clusters in this region, print message and skip the rest of the loop
  if [ -z "$endpoints" ]; then
    echo "No Redshift clusters in region $region."
    return
  fi
  
  # Write the endpoints to the file
  printf "%s\n" "${endpoints[@]}" >> "$redshift_endpoints_file"
}

# Run the function for each region
for region in "${REGIONS[@]}"; do
  describe_redshift_clusters $region
done

#redshift_endpoints_filename=$(basename "$redshift_endpoints_file")

# Unset the default region
unset AWS_DEFAULT_REGION

echo "Completed. Redshift endpoints are saved in results."

