#!/bin/bash

# Set the default region to us-east-1
export AWS_DEFAULT_REGION=us-east-1

# File to store Elastic Beanstalk environment endpoints and their IPs
eb_envs_file="results/eb_domain.txt"
eb_envs_ips_file="results/eb_ips.txt"

> "$eb_envs_file" # Empty the file if it exists
> "$eb_envs_ips_file" # Empty the file if it exists

# Fetch list of all AWS regions
REGIONS=( $(aws ec2 describe-regions --query "Regions[].RegionName" --output text) )

# Function to describe Elastic Beanstalk environments
describe_eb_envs() {
  region=$1
  
  # Elastic Beanstalk environments
  eb_envs=( $(aws elasticbeanstalk describe-environments --region $region --query 'Environments[*].EndpointURL' --output text) )
  if [ -z "$eb_envs" ]; then
    echo "No Elastic Beanstalk environments found in region $region."
  else
    for env_endpoint in "${eb_envs[@]}"; do
      echo "$env_endpoint" >> "$eb_envs_file"
      ip=$(dig +short $env_endpoint)
      echo "$ip" >> "$eb_envs_ips_file"
    done
  fi
}

# Run the function for each region
for region in "${REGIONS[@]}"; do
  describe_eb_envs $region
done

# Unset the default region
unset AWS_DEFAULT_REGION

echo "Completed. Elastic Beanstalk environment endpoints and IPs are saved in their respective files."

