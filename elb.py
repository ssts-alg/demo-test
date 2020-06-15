#! /usr/local/bin/python3

import os
import boto3
import sys
import logging
import threading
from config import *

logging.basicConfig(filename='elb.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

default_region="us-west-2"

#Credentials Validation
sts = boto3.client('sts',aws_access_key_id=access_key,aws_secret_access_key=secret_access_key,region_name=default_region)
try:
    sts.get_caller_identity()
    logging.info("Credentials are valid.")
except:
    logging.info("Credentials invalid. \nPlease Provide Valid Credentials in config file.\nThanks")
    sys.exit(0)

#Region Validation
client = boto3.client('ec2',aws_access_key_id=access_key,aws_secret_access_key=secret_access_key,region_name=default_region)
regions_list = [region['RegionName'] for region in client.describe_regions()['Regions']]
def region_check(regions):
    for region in regions:
        if region not in regions_list:
            logging.info(f"{region} No Such Region Found.\nPlease Enter Valid Region in config file.\nThanks")
            sys.exit(1)


#Checks
if len(regions)==0:
    logging.info("Please Enter Atleast One region in Config file.")
    sys.exit(2)
if len(ec2_tag_names)==0:
    logging.info("Please Enter Atleast One EC2 Tag name in Config file.")
    sys.exit(3)


def matching_instances(regions):
    instance_ids_with_matching_tags=[]
    for region in regions:
        client = boto3.client('ec2',aws_access_key_id=access_key,aws_secret_access_key=secret_access_key,region_name=region)
        response = client.describe_instances(Filters=ec2_tag_names)
        for d in response['Reservations']:
            for z in d['Instances']:
                instance_ids_with_matching_tags.append(z['InstanceId'])
    if len(instance_ids_with_matching_tags)==0:
        logging.info(f"No matching instances found in this {ec2_tag_names} tagging creteria. \nPlease Provide Valid Tags.\nThanks")
        sys.exit(4)
    print(instance_ids_with_matching_tags)

def deregistering_instances(regions):
    elb_list=[]
    instance_list=[]
    # Fetching all available ELBs names from this account.
    for region in regions:
        elb_client = boto3.client('elb',aws_access_key_id=access_key,aws_secret_access_key=secret_access_key,region_name=region)
        elb_response = elb_client.describe_load_balancers()
        a=elb_response['LoadBalancerDescriptions']
        for z in a:
            elb_list.append(z['LoadBalancerName'])
    elb_names=elb_list
    logging.info("Trying to Deregister Instances...")
    deregistered_instances=[]
    instance_list=[]
    for region in regions:
        new_list=[]
        elb_client = boto3.client('elb',aws_access_key_id=access_key,aws_secret_access_key=secret_access_key,region_name=region)
        elb_response=elb_client.describe_load_balancers()
        a=elb_response['LoadBalancerDescriptions']
        for z in a:
            if z['LoadBalancerName'] in elb_names:
                new_list.append(z['LoadBalancerName'])
                elb_response1=elb_client.describe_load_balancers(LoadBalancerNames=new_list)
                insta=elb_response1['LoadBalancerDescriptions']
                for f in insta:
                    for t in f['Instances']:
                        client = boto3.client('ec2',aws_access_key_id=access_key,aws_secret_access_key=secret_access_key,region_name=region)
                        response = client.describe_instances(Filters=ec2_tag_names)
                        for d in response['Reservations']:
                            for z in d['Instances']:
                                if t['InstanceId']==z['InstanceId']:
                                    instance_list.append(t['InstanceId'])
                                    for elb in new_list:
                                        elb_response = elb_client.deregister_instances_from_load_balancer(LoadBalancerName=elb,Instances=[{'InstanceId': t['InstanceId']}])
                                        logging.info(f"{t['InstanceId']} is Deregistered from ELB named \"{elb}\" in region \"{region}\"")
    # print(list(dict.fromkeys(instance_list)))
    if len(list(dict.fromkeys(instance_list)))==0 :
        logging.info("Nothing to Deregister.\nThanks.")

thread1=threading.Thread(target=region_check, args=(regions,))
thread2=threading.Thread(target=matching_instances, args=(regions,))
thread3=threading.Thread(target=deregistering_instances, args=(regions,))

thread1.start()
thread2.start()
thread3.start()

thread1.join()
thread2.join()
thread3.join()
