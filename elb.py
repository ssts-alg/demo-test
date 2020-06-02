#! /usr/local/bin/python3
import botocore
import os
import boto3
import sys
region=input("Enter Region: ")

ec2_tag_name=input("Enter EC2 Tag name to Deregister from Load Balancer: ")
elb_name=input("Enter target ELB : ")
os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "./creds"
os.environ["AWS_DEFAULT_REGION"] = region
client = boto3.client('ec2')
elb_client = boto3.client('elb')
sts = boto3.client('sts')
try:
    sts.get_caller_identity()
    print("Credentials are valid.")
except:
    print("Credentials invalid.")

elb_list=[]
response1 = elb_client.describe_load_balancers()
a=response1['LoadBalancerDescriptions']
for z in a:
    elb_list.append(z['LoadBalancerName'])
if elb_name not in elb_list:
    print(f"{elb_name} ELB not Foung in this {region}")
    sys.exit(0)
else:
    print(f"Trying to Deregister Instances from {elb_name} ELB")


instance_list=[]

response = client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [ec2_tag_name]}])
for x in response['Reservations']:
    for y in x['Instances']:
        instance_list.append(y['InstanceId'])
for id in instance_list:
    elb_response = elb_client.deregister_instances_from_load_balancer(
               LoadBalancerName=elb_name,
               Instances=[
                        {
                            'InstanceId': id
                        }
                        ]
        )
    print(f"{instance_list} are removed from {elb_name} ELB Successfully")
