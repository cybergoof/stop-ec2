from aws_cdk import (
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_sns as sns,
    aws_sqs as sqs,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_events_targets as targets,
    aws_sns_subscriptions as subs,
    aws_events as events,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    core
)


class StopEc2Stack(core.Stack):
    """
    StopEc2Stack will create a cloudformation stack that will faclitate automatically stopping
    and EC2 after a set timeframe

    Inputs:
    User Group name that will be used to trigger when a new EC2 is started
    Duration - how long the EC2 must stay before it is terminated

    Artifacts:
    Lambda function that will terminate the EC2.  Input is the EC2 ID
    Rule that monitors when an EC2 is created by a particular group
    Lambda function that will create a timed rule.
    SNS topic when a system is deleted0
    """

    def __init__(self, scope: core.Construct, id: str, group_name: str, minute_duration: int, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # TODO: Setup alerting of failure to an SNS
        # TODO: Failure is not the same as a student not in a group
        # TODO: Streamline input data so that lambda's only get the info they really need
        # TODO: Comment
        # TODO: Need to separate unexpected errors from regular errors
        # Setting up monitoring

        schedule_stop = lambda_.Function(self,
                                         id="ScheduleStopLambda",
                                         runtime=lambda_.Runtime.PYTHON_3_7,
                                         code=lambda_.Code.from_inline(
                                             open("./resources/schedule-termination.py", 'r').read()),
                                         handler="index.handler",
                                         log_retention=logs.RetentionDays.ONE_DAY,
                                         environment=dict(
                                             GROUP_NAME=group_name),
                                         timeout=core.Duration.seconds(30)
                                         )
        schedule_stop.add_to_role_policy(
            statement=iam.PolicyStatement(
                actions=[
                    "ec2:Describe*",
                    "iam:ListGroupsForUser",
                    "iam:ListUsers"
                ],
                effect=iam.Effect.ALLOW,
                resources=["*"]
            ))

        terminate_ec2 = lambda_.Function(self,
                                         id="TerminateEC2",
                                         runtime=lambda_.Runtime.PYTHON_3_7,
                                         code=lambda_.Code.from_inline(
                                             open("./resources/terminate-ec2.py", 'r').read()),
                                         handler="index.handler",
                                         log_retention=logs.RetentionDays.ONE_DAY,
                                         timeout=core.Duration.seconds(30)
                                         )
        terminate_ec2.add_to_role_policy(
            statement=iam.PolicyStatement(
                actions=[
                    "ec2:DescribeInstance*",
                    "ec2:TerminateInstances",
                ],
                effect=iam.Effect.ALLOW,
                resources=["*"]
            ))

        # The lambda object that will see if we should schedule.
        schedule_stop_task = tasks.LambdaInvoke(self,
                                                id='schedule stop',
                                                lambda_function=schedule_stop,
                                                input_path="$.detail.userIdentity",
                                                result_path="$.Payload",
                                                )
        # TODO: Need to change this based on the configuration info above
        # Wait state to try and delete
        # wait_x = sfn.Wait(self, 'Wait x minutes', time=sfn.WaitTime.seconds_path("10"))
        wait_x = sfn.Wait(self, id='Wait x minutes',
                          time=sfn.WaitTime.duration(core.Duration.minutes(minute_duration)))

        job_failed = sfn.Fail(self, id="Failed Job", cause="Error in the input", error="Error")
        job_finished = sfn.Succeed(self, id="Job Finished")
        choice = sfn.Choice(self, 'Can I delete')
        choice.when(sfn.Condition.boolean_equals('$.Payload.Payload', False), job_finished)
        choice.otherwise(wait_x)
        terminate_ec2_task = tasks.LambdaInvoke(self,
                                                'terminate',
                                                lambda_function=terminate_ec2,
                                                input_path="$.detail.responseElements.instancesSet"
                                                )
        wait_x.next(terminate_ec2_task).next(job_finished)

        state_definition = schedule_stop_task \
            .next(choice)
        terminate_machine = sfn.StateMachine(self, id="State Machine", definition=state_definition)
        cloudwatch.Alarm(self, "EC2ScheduleAlarm",
                         metric=terminate_machine.metric_failed(),
                         threshold=1,
                         evaluation_periods=1)
        # TODO Build Rule that monitors for EC2 creation
        # Any new creation, the EC2 will have to be destroyed.  Including
        # other things?
        create_event = events.Rule(self,
                                   id='detect-ec2-start',
                                   description="Detects if an EC2 is created",
                                   enabled=True,
                                   event_pattern=events.EventPattern(
                                       detail_type=["AWS API Call via CloudTrail"],
                                       source=["aws.ec2"],
                                       detail={"eventName": ["RunInstances"],
                                               "eventSource": ["ec2.amazonaws.com"]}),
                                   targets=[targets.SfnStateMachine(terminate_machine)]
                                   )

