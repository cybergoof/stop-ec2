#!/usr/bin/env python3

from aws_cdk import core

from stop_ec2.stop_ec2_stack import StopEc2Stack


app = core.App()
StopEc2Stack(app, "stop-ec2")

app.synth()
