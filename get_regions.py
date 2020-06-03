#! /usr/local/bin/python3

import os
import boto3
import sys
# region=input("Enter Region: ")

os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "./creds"
# os.environ["AWS_DEFAULT_REGION"] = region
client = boto3.client('ec2')
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
print(regions)
