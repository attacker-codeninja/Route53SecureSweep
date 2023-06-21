#!/bin/bash


# Set the default region to us-east-1
export AWS_DEFAULT_REGION=us-east-1

# File to store Elasticsearch endpoints
endpoints_file="results/elasticsearch_endpoints.txt"

# Empty the file if it exists
> "$endpoints_file"

# Fetch list of all AWS regions
regions=$(aws ec2 describe-regions --query "Regions[].RegionName" --output text)

# Iterate over each region
for region in $regions; do
  # Fetch Elasticsearch domain names in the region
  domain_names=$(aws es list-domain-names --region "$region" --query 'DomainNames[].DomainName' --output text)

  # Check if no domain names found in the region
  if [ -z "$domain_names" ]; then
    echo "No Elasticsearch domains found in region $region."
    continue
  fi

  # Iterate over each domain name
  for domain_name in $domain_names; do
    # Describe the Elasticsearch domain
    response=$(aws es describe-elasticsearch-domain --region "$region" --domain-name "$domain_name")

    # Extract the endpoint from the response
    endpoint=$(echo "$response" | jq -r '.DomainStatus.Endpoint')

    # Check if endpoint is not empty
    if [ -n "$endpoint" ] && [ "$endpoint" != "null" ]; then
      echo "$endpoint" >> "$endpoints_file"
    fi
  done
done

# Unset the default region
unset AWS_DEFAULT_REGION

echo "Completed. Elasticsearch endpoints are saved in results."

