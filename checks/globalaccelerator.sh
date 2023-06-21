#!/bin/bash

# Set the default region to us-east-1
export AWS_DEFAULT_REGION=us-east-1

# File to store public IPs
public_ips_file="results/accelerator_ips.txt"

# Empty the file if it exists
> "$public_ips_file"

# Function to list accelerators
list_accelerators() {
  # Fetch list of all accelerator IPs
  accelerator_ips=( $(aws globalaccelerator list-accelerators --region us-west-2 --query 'Accelerators[*].IpSets[*].IpAddresses' --output text) )
  
  # If no accelerators, return
  if [ -z "$accelerator_ips" ]; then
    echo "No accelerators found."
    return
  fi

  # Print the IPs to the file
  printf "%s\n" "${accelerator_ips[@]}" >> "$public_ips_file"
}

# Run the function
list_accelerators

# Unset the default region
unset AWS_DEFAULT_REGION

echo "Completed. Accelerator IPs are saved in results."

