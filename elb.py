#! /usr/local/bin/python3

import os
import boto3
import sys
from config import *

# Declaring Clients
client = boto3.client('ec2',aws_access_key_id=access_key,aws_secret_access_key=secret_access_key,region_name=region)
elb_client = boto3.client('elb',aws_access_key_id=access_key,aws_secret_access_key=secret_access_key,region_name=region)
sts = boto3.client('sts',aws_access_key_id=access_key,aws_secret_access_key=secret_access_key,region_name=region)

#Region Validation
regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
if region not in regions:
    print(f"{region}No Such Region Found.")
    sys.exit(2)

#Credentials Validation
try:
    sts.get_caller_identity()
    print("Credentials are valid.")
except:
    print("Credentials invalid. Please Provide Valid Credentials.")
    sys.exit(1)

elb_list=[]
instance_list=[]

# Fetching all available ELBs names from this account.
elb_response = elb_client.describe_load_balancers()
a=elb_response['LoadBalancerDescriptions']
for z in a:
    elb_list.append(z['LoadBalancerName'])

# ELB name Validation
if elb_name not in elb_list:
    print(f"{elb_name} ELB not Found in this {region}")
    sys.exit(0)
else:
    print(f"Trying to Deregister Instances from {elb_name} ELB")
elb_response1=elb_client.describe_load_balancers(LoadBalancerNames=[elb_name])

insta=elb_response1['LoadBalancerDescriptions'][0]['Instances']
for s in insta:
    instance_list.append(s['InstanceId'])
deregistered_instances=[]
response = client.describe_instances(Filters=[{'Name': 'instance-id','Values': instance_list}])
for d in response['Reservations']:
    for z in d['Instances']:
        if z['Placement']['AvailabilityZone']==availablity_zone and z['Tags'][0]['Value']==ec2_tag_name:
            deregistered_instances.append(z['InstanceId'])
            # Deregistering Instances from ELB
            elb_response = elb_client.deregister_instances_from_load_balancer(
                           LoadBalancerName=elb_name,
                           Instances=[
                                    {
                                        'InstanceId': z['InstanceId']
                                    }
                                    ]
                    )
print(f"{deregistered_instances} are Deregistered Successfully")
