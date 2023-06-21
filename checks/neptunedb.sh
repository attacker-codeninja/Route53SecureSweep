#!/bin/bash

# Set the default region to us-east-1
export AWS_DEFAULT_REGION=us-east-1

# File to store NeptuneDB endpoint addresses
neptune_endpoints_file="results/neptune_endpoints.txt"

# Empty the file if it exists
> "$neptune_endpoints_file"

# Fetch list of all AWS regions
REGIONS=( $(aws ec2 describe-regions --query "Regions[].RegionName" --output text) )

# Function to describe NeptuneDB instances
describe_neptune_instances() {
  region=$1
  endpoints=( $(aws neptune describe-db-instances --region $region --query 'DBInstances[*].Endpoint.Address' --output text) )

  # If no instances in this region, print message and skip the rest of the loop
  if [ -z "$endpoints" ]; then
    echo "No NeptuneDB instances in region $region."
    return
  fi
  
  # Write the endpoints to the file
  printf "%s\n" "${endpoints[@]}" >> "$neptune_endpoints_file"
}

# Run the function for each region
for region in "${REGIONS[@]}"; do
  describe_neptune_instances $region
done

# Unset the default region
unset AWS_DEFAULT_REGION

echo "Completed. NeptuneDB endpoints are saved in results."

