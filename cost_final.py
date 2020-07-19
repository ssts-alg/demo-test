from datetime import datetime,timedelta,date
import boto3
import logging
from config import *
import calendar
import sys
import os
from botocore.exceptions import ClientError
from dateutil.relativedelta import relativedelta
print("")
if len(account_details)==0:
    print("Please Provide al least one account details in config file")
    sys.exit(0)
for x in account_details:
    try:
        region="aws configure set default.region us-west-2"
        profile="aws configure set profile." + x['Account_Name'] + ".role_arn arn:aws:iam::" + x['Account_ID'] + ":role/s3_cross_account"
        meta_data="aws configure set profile." + x['Account_Name'] + ".credential_source Ec2InstanceMetadata"
        os.system(region)
        os.system(profile)
        os.system(meta_data)
        session=boto3.Session(profile_name=x['Account_Name'])
        sts = session.client('sts')
        sts.get_caller_identity()
    except ClientError as e:
        try:
            if e.response['Error']['Code'] == 'AccessDenied':
                session=boto3.Session(aws_access_key_id=x['access_key'],aws_secret_access_key=x['secret_access_key'])
                sts = session.client('sts')
                sts = session.client('sts')
                sts.get_caller_identity()
        except:
            print(x['Account_Name']+ " account has invalid Details. Please configure proper IAM roles or access keys for this account "+x['Account_ID'])
            continue
    #required Variables
    DATE_REPLACE = str(datetime.today().replace(day=1))
    FIRST_DAY_DATE = DATE_REPLACE.split()[0]
    DATE_ADDING = str(datetime.today() + timedelta(days=1))
    TOMORROW_DAY_DATE = DATE_ADDING.split()[0]
    NEXT_MONTH_FIRST_DATE = str(date.today().replace(day=1) + relativedelta(months=1))
    NOW = datetime.now()
    MONTH_NAME = NOW.strftime('%B')
    LAST_DAY_OF_CURRENT_MONTH=calendar.monthrange(date.today().year,date.today().month)[1]
    TODAY_DATE_IN_DAY=date.today().day
    TODAY_DATE_FULL=str(date.today())
    # print (NEXT_MONTH_FIRST_DATE)

    ce_client = session.client('ce')

    cost_usage_response = ce_client.get_cost_and_usage(TimePeriod={"Start": FIRST_DAY_DATE,"End": NEXT_MONTH_FIRST_DATE},Granularity='MONTHLY',Metrics=['UNBLENDED_COST',],GroupBy=[{'Type': 'DIMENSION','Key': 'LINKED_ACCOUNT'},],)
    for groups in cost_usage_response['ResultsByTime']:
        for amount in groups['Groups']:
          MONTH_TO_DATE_COST=str(amount['Metrics']['UnblendedCost']['Amount'])
        print("For account "+x['Account_ID']+" With Name "+x['Account_Name']+" :")
        print("-----------------------------------------")
        print(str(MONTH_NAME)+" month to date cost for account  is : $"+str(MONTH_TO_DATE_COST))

#Taking projection cost from forecast

    if TOMORROW_DAY_DATE==NEXT_MONTH_FIRST_DATE:
        print(str(MONTH_NAME)+" Today is lastday of this month There is nothing predict cost. please check overall cost ")
    elif TODAY_DATE_IN_DAY == LAST_DAY_OF_CURRENT_MONTH:
        print("Today is the last day in this month")
        forecast_response = ce_client.get_cost_forecast(TimePeriod={'Start': TODAY_DATE_FULL,'End': NEXT_MONTH_FIRST_DATE},Metric='UNBLENDED_COST',Granularity='MONTHLY',PredictionIntervalLevel=99)
        PROJECTION_COST=str(forecast_response['Total']['Amount'])
        print(str(MONTH_NAME)+" months Projection cost for account is : $"+str(PROJECTION_COST)+" \n  ")
    else:
        forecast_response = ce_client.get_cost_forecast(TimePeriod={'Start': TOMORROW_DAY_DATE,'End': NEXT_MONTH_FIRST_DATE},Metric='UNBLENDED_COST',Granularity='MONTHLY',PredictionIntervalLevel=99)
        PROJECTION_COST=str(forecast_response['Total']['Amount'])
        print(str(MONTH_NAME)+" months Projection cost for account is : $"+str(PROJECTION_COST)+" \n  ")
