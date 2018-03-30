#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import csv
import re
import platform
from os.path import expanduser
try:
    import boto3
except:
    sys.exit("Error: You did not install boto3 (pip install boto3)")


"""
Find EC2, across accounts and export to csv file for the purposes of:
Compliance / Security / Finance
Future Plans: CLI Arguments to specify what should be dumped into the CSV.
# MacOS: pip freeze | grep boto3
# PC   : pip freeze | findstr boto3
# boto3==1.4.7
"""


__author__ = "Joseph Drane"
__version__ = "0.1.1"
__license__ = "MIT"


def get_ec2(account_profile):
    """
    Find all EC2 instances in all regions for a single account.
    """
    session = boto3.Session(profile_name=account_profile)
    client = session.client('ec2', region_name='us-east-1')
    ec2_regions = [region['RegionName']
                   for region in client.describe_regions()['Regions']
                   ]
    for region in ec2_regions:
        ec2 = session.resource('ec2', region_name=region)
        instances = ec2.instances.filter()
        with open('EC2_In_All_Accounts.csv', 'ab') as myfile:
            wr = csv.writer(myfile, dialect='excel')
            for instance in instances:
                try:
                    for tag in instance.tags:
                        if tag['Key'] == 'Name':
                            instancename = tag['Value']
                except:
                    instancename = 'Has No Name'
                mylist = [instancename,
                          instance.private_ip_address,
                          instance.state['Name']
                          ]
                print(mylist)
                wr.writerow(mylist)


def slash():
    """
    Get the right path slash for the OS used.
    """
    slash = ''
    if platform.system() == 'Windows':
        slash = '\\'
    else:
        slash = '/'
    return slash


def get_awscli_profiles():
    """
    Returns a List of profiles found in home > .aws > credentials
    """
    home = expanduser("~")
    credentials = home + slash() + '.aws' + slash() + 'credentials'
    creds_file = open(credentials, 'r').read()
    match = re.findall('(\[.*\])', creds_file)
    aws_profiles = [profile.replace('[', '').replace(']', '')
                    for profile in match
                    ]
    if aws_profiles:
        return aws_profiles
    else:
        sys.exit("ERROR: No Profiles Found. Please run: aws configure first")


def main():
    """
    Main entry point of the app
    Runs get_ec2 for each profile
    """
    profiles = get_awscli_profiles()
    for profile in profiles:
        try:
            get_ec2(profile)
        except:
            print ("This " +profile+ " profile didn't work.")


if __name__ == "__main__":
    """
    This is executed when run from the command line
    """
    main()
