#! /usr/local/bin/python3

import os
import boto3
region=input("Enter Region: ")
ec2_tag_name=input("Enter EC2 Tag name to Deregister from Load Balancer: ")
elb_name=input("Enter target ELB : ")
os.environ["AWS_SHARED_CREDENTIALS_FILE"] = "./creds"
os.environ["AWS_DEFAULT_REGION"] = region
instance_list=[]
client = boto3.client('ec2')
elb_client = boto3.client('elb')
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
