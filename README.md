
# Stop EC2 Automatically

This CDK project will generate a CloudFormation template that monitors for EC2's started by a user 
of a particular group, and will terminate those instances after a duration.

To deploy the project, use the command:
```
cdk deploy -c GROUP_NAME="Students" -c DURATION=3
```
    
Replace "Students" with your group name and 3 with the number of minutes to wait.

A CloudWatch rule will look for EC2 creation, and kick off a Step Function that uses lambda functions
to check if the user belongs to a group, and another lambda function to terminate those instances.

If the EC2 creator is not part of the target group, the user is root, or is a cross account role, the
step function will simply exit.

If the lambda functions or Step function fail, a CloudWatch alarm will be generated.
 
The user must setup the AWS CDK.
Python 3.7 is used.
The python packages are loaded with a Pipefile using Pipenv.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
