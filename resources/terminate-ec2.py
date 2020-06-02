import boto3
from botocore.exceptions import ClientError


def handler(event, context):
    """Takes a list of EC2 ID's and attempts to terminate them"""
    print(event)
    ids = []
    # Extract the list of images form the JSON list

    try:
        for image in event['items']:
            ids.append((image['instanceId']))
    except:
        raise Exception("Malformed input")

    # Get a set of EC2 resource objects and terminates them
    try:
        ec2 = boto3.resource('ec2')
        ec2.instances.filter(InstanceIds=ids).terminate()
    except ClientError as e:
        raise Exception("Unexpected error: %s" % e)
