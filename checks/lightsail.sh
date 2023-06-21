#!/bin/bash

# Set the default region to us-east-1
export AWS_DEFAULT_REGION=us-east-1

# File to store Lightsail public IPs
lightsail_ips_file="results/lightsail_ips.txt"

# Empty the file if it exists
> "$lightsail_ips_file"

# Fetch list of all AWS regions
REGIONS=( $(aws ec2 describe-regions --query "Regions[].RegionName" --output text) )

# Function to describe Lightsail instances
describe_lightsail_instances() {
  region=$1
  ips=( $(aws lightsail get-instances --region $region --query 'instances[*].publicIpAddress' --output text) )

  # If no instances in this region, print message and skip the rest of the loop
  if [ -z "$ips" ]; then
    echo "No Lightsail instances in region $region."
    return
  fi
  
  # Write the IPs to the file
  printf "%s\n" "${ips[@]}" >> "$lightsail_ips_file"
}

# Run the function for each region
for region in "${REGIONS[@]}"; do
  describe_lightsail_instances $region
done

# Unset the default region
unset AWS_DEFAULT_REGION

echo "Completed. Lightsail public IPs are saved in results."

