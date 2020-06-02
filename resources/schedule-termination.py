import boto3
from botocore.exceptions import ClientError
import os


def handler(userIdentity, context):
    """Determines if the user is part of the User Group that will have automated deletions"""
    print(userIdentity)
    # Checks to see if it can extract the username.  If not, then likely not a local IAM user. Root user or user role

    # Connect to boto3 to get all the groups for the user
    try:
        group_name = os.environ['GROUP_NAME']
    except:
        raise Exception("There was no GROUP_NAME environment variable")

    try:
        userName = userIdentity["userName"]
    except:
        print("Not an IAM account, can not check Group")
        return False
    try:
        client = boto3.client('iam')
        response = client.list_groups_for_user(
            UserName=userName
        )
    except ClientError as e:
        raise Exception("Unexpected error: %s" % e)

    try:
        # If true, the user is part of the desired group.  If false, it is not
        if len(list(filter(lambda x: x["GroupName"] == group_name, response["Groups"]))):
            return True
        else:
            return False
    except:
        raise Exception("The data returned from list_group_for_users is not structured properly")
