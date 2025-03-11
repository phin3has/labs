#!/usr/bin/env python3

import boto3
import json

# The pricing service is only available in these regions, but we can query for eu-south-1 prices:
PRICING_REGION = "us-east-1"

# A helper function to query AWS pricing and parse the results
def get_aws_pricing(service_code, filters):
    client = boto3.client("pricing", region_name=PRICING_REGION)
    
    response = client.get_products(
        ServiceCode=service_code,
        Filters=filters,
        MaxResults=100
    )
    
    results = []
    for price_item in response["PriceList"]:
        parsed = json.loads(price_item)
        product_attrs = parsed["product"]["attributes"]
        
        # On-Demand pricing details
        on_demand_terms = parsed["terms"].get("OnDemand", {})
        # each key is a term code, so we iterate them
        for term_code, term_data in on_demand_terms.items():
            for price_dimension_code, price_dimension_data in term_data["priceDimensions"].items():
                results.append({
                    "sku": parsed["product"]["sku"],
                    "product_name": product_attrs.get("instanceType", product_attrs.get("usagetype", "N/A")),
                    "location": product_attrs.get("location"),
                    "operation": product_attrs.get("operation"),
                    "description": price_dimension_data["description"],
                    "pricePerUnit": price_dimension_data["pricePerUnit"].get("USD", "N/A"),
                })
    
    return results

def main():
    # --------------------------
    # 1) ECS Fargate (Linux)
    # --------------------------
    ecs_filters = [
        {"Type": "TERM_MATCH", "Field": "location",        "Value": "EU (Milan)"},
        {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
        {"Type": "TERM_MATCH", "Field": "operation",       "Value": "RunFargateTask"}
    ]
    ecs_prices = get_aws_pricing(service_code="AmazonECS", filters=ecs_filters)
    
    print("=== ECS Fargate (eu-south-1) ===")
    for p in ecs_prices:
        print(p)
    
    # --------------------------
    # 2) S3 Standard Storage
    # --------------------------
    #   - For S3, 'location' = 'EU (Milan)', 
    #   - 'storageClass' can be 'Standard', 'Infrequent Access', etc.
    #   - 'usagetype' might vary, e.g., "EU-South-1" for data usage.
    s3_filters = [
        {"Type": "TERM_MATCH", "Field": "location",     "Value": "EU (Milan)"},
        {"Type": "TERM_MATCH", "Field": "storageClass", "Value": "Standard"},
        {"Type": "TERM_MATCH", "Field": "servicecode",  "Value": "AmazonS3"},
    ]
    s3_prices = get_aws_pricing(service_code="AmazonS3", filters=s3_filters)
    
    print("\n=== S3 Standard (eu-south-1) ===")
    for p in s3_prices:
        print(p)
    
    # --------------------------
    # 3) RDS (MySQL example)
    # --------------------------
    #   - Filter by location, databaseEngine, instanceType, etc.
    rds_filters = [
        {"Type": "TERM_MATCH", "Field": "location",        "Value": "EU (Milan)"},
        {"Type": "TERM_MATCH", "Field": "databaseEngine",  "Value": "MySQL"},
        # For example, you can specify a particular instance type
        # {"Type": "TERM_MATCH", "Field": "instanceType", "Value": "db.t4g.micro"}
    ]
    rds_prices = get_aws_pricing(service_code="AmazonRDS", filters=rds_filters)
    
    print("\n=== RDS MySQL (eu-south-1) ===")
    for p in rds_prices:
        print(p)

if __name__ == "__main__":
    main()