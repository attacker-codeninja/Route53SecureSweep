#!/bin/bash


# Set the default region to us-east-1
export AWS_DEFAULT_REGION=us-east-1

# # Create the "results" folder if it doesn't exist
# mkdir -p results

# File to store Load Balancer DNS names
lb_domains_file="results/lb_domains.txt"
> "$lb_domains_file" # Empty the file if it exists

# File to store Load Balancer IPs
lb_ips_file="results/lb_ips.txt"
> "$lb_ips_file" # Empty the file if it exists

# Fetch list of all AWS regions
REGIONS=( $(aws ec2 describe-regions --query "Regions[].RegionName" --output text) )

# Function to describe load balancers
describe_load_balancers() {
  region=$1
  dns_names=( $(aws elbv2 describe-load-balancers --region $region --query 'LoadBalancers[*].DNSName' --output text) )

  # If no Load Balancers in this region, print message and skip the rest of the loop
  if [ -z "$dns_names" ]; then
    echo "No Load Balancer found in region $region."
    return
  fi

  for dns_name in "${dns_names[@]}"; do
    echo "$dns_name" >> "$lb_domains_file"
    ip=$(dig +short $dns_name)
    echo "$ip" >> "$lb_ips_file"
  done
}

# Run the function for each region
for region in "${REGIONS[@]}"; do
  describe_load_balancers $region
done

# Extract the file names without the directory path
#lb_domains_filename=$(basename "$lb_domains_file")
#lb_ips_filename=$(basename "$lb_ips_file")

# Unset the default region
unset AWS_DEFAULT_REGION

echo "Completed. Load Balancer DNS names and IPs are saved in results."


