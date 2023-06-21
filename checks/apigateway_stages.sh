#!/bin/bash

# Set the default region to us-east-1
export AWS_DEFAULT_REGION=us-east-1

# Files to store API Gateway endpoint addresses and their stages
rest_apis_file="results/rest_apis.txt"
http_apis_file="results/http_apis.txt"
websocket_apis_file="results/websocket_apis.txt"

rest_apis_stages_file="results/rest_apis_stages.txt"
http_apis_stages_file="results/http_apis_stages.txt"
websocket_apis_stages_file="results/websocket_apis_stages.txt"

# Empty the files if they exist
> "$rest_apis_file"
> "$http_apis_file"
> "$websocket_apis_file"
> "$rest_apis_stages_file"
> "$http_apis_stages_file"
> "$websocket_apis_stages_file"

# Fetch list of all AWS regions
REGIONS=( $(aws ec2 describe-regions --query "Regions[].RegionName" --output text) )

# Function to describe API Gateways
describe_apis() {
  region=$1
  
  # REST APIs
  rest_apis=( $(aws apigateway get-rest-apis --region $region --query 'items[*].id' --output text) )
  if [ -z "$rest_apis" ]; then
    echo "No REST APIs found in region $region."
  else
    for api_id in "${rest_apis[@]}"; do
      dns_name="${api_id}.execute-api.${region}.amazonaws.com"
      echo "$dns_name" >> "$rest_apis_file"
      stages=$(aws apigateway get-stages --rest-api-id "$api_id" --region "$region" --query 'item[].stageName' --output text)
      for stage in $stages; do
        echo "${dns_name}/${stage}" >> "$rest_apis_stages_file"
      done
    done
  fi

  # HTTP APIs
  http_apis=( $(aws apigatewayv2 get-apis --region $region --query 'Items[?ProtocolType==`HTTP`].ApiEndpoint' --output text) )
  if [ -z "$http_apis" ]; then
    echo "No HTTP APIs found in region $region."
  else
    for api_endpoint in "${http_apis[@]}"; do
      echo "$api_endpoint" >> "$http_apis_file"
      api_id=$(aws apigatewayv2 get-apis --region "$region" --query "Items[?ApiEndpoint=='$api_endpoint'].ApiId" --output text)
      stages=$(aws apigatewayv2 get-stages --api-id "$api_id" --region "$region" --query 'Items[].StageName' --output text)
      for stage in $stages; do
        echo "${api_endpoint}/${stage}" >> "$http_apis_stages_file"
      done
    done
  fi

  # WebSocket APIs
  websocket_apis=( $(aws apigatewayv2 get-apis --region $region --query 'Items[?ProtocolType==`WEBSOCKET`].ApiEndpoint' --output text) )
  if [ -z "$websocket_apis" ]; then
    echo "No WebSocket APIs found in region $region."
  else
    for api_endpoint in "${websocket_apis[@]}"; do
      echo "$api_endpoint" >> "$websocket_apis_file"
      api_id=$(aws apigatewayv2 get-apis --region "$region" --query "Items[?ApiEndpoint=='$api_endpoint'].ApiId" --output text)
      stages=$(aws apigatewayv2 get-stages --api-id "$api_id" --region "$region" --query 'Items[].StageName' --output text)
      for stage in $stages; do
        echo "${api_endpoint}/${stage}" >> "$websocket_apis_stages_file"
      done
    done
  fi
}

# Run the function for each region
for region in "${REGIONS[@]}"; do
  describe_apis "$region"
done

# Unset the default region to us-east-1
unset AWS_DEFAULT_REGION
echo "Completed. API Gateway endpoints and stages are saved in their respective files."

