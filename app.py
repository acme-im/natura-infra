#!/usr/bin/env python3

from aws_cdk import App

from cdk_stack.base_stack import BaseStack

app = App()
BaseStack(app, "base-cdk-stack")

app.synth()
