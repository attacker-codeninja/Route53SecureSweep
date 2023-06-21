#!/bin/bash

# Set the default region to us-east-1
export AWS_DEFAULT_REGION=us-east-1

# File to store CloudFront domains
cf_domains_file="results/cf_domains.txt"
> "$cf_domains_file" # Empty the file if it exists

# Function to list CloudFront distributions
list_distributions() {
  cf_domains=( $(aws cloudfront list-distributions --query 'DistributionList.Items[*].DomainName' --output text) )
  
  # If no distributions found, print a message and return
  if [ -z "$cf_domains" ]; then
    echo "No CloudFront distributions found."
    return
  fi
  
  # Append domain names to the file
  printf "%s\n" "${cf_domains[@]}" >> "$cf_domains_file"
}

# Run the function
list_distributions

# Unset the default region
unset AWS_DEFAULT_REGION

echo "Completed. CloudFront domains are saved in results."

