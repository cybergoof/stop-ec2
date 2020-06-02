#!/usr/bin/env python3

from aws_cdk import core
import os
from stop_ec2.stop_ec2_stack import StopEc2Stack


app = core.App()
duration = app.node.try_get_context("DURATION")
group_name = app.node.try_get_context("GROUP_NAME")
account = os.environ["CDK_DEFAULT_ACCOUNT"]
region = os.environ["CDK_DEFAULT_REGION"]
app = core.App()
StopEc2Stack(app, id="stop-ec2",
             group_name=group_name,
             minute_duration=int(duration),
             env={'region': region, "account": account})

app.synth()
