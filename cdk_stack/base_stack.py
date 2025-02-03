import typing as t

from aws_cdk import Stack
from constructs import Construct

from cdk_stack.assets_stack import AssetsStack
from cdk_stack.bucket_stack import BucketStack
from cdk_stack.dns_stack import DnsStack
from cdk_stack.jobs_stack import JobsStack
from cdk_stack.landing_stack import LandingStack


class BaseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: dict[str, t.Any]) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env = self.node.try_get_context("env")
        if env is None:
            raise RuntimeError()

        dns_stack = DnsStack(self, "DnsStack", env=env)

        # bucket for assets and jobs artifacts
        assets_bucket_stack = BucketStack(self, "AssetsBucket", main_zone=dns_stack.main_zone, env=env, prefix="cdn")

        AssetsStack(self, "AssetsStack", bucket_stack=assets_bucket_stack)

        JobsStack(self, "JobsStack", bucket_stack=assets_bucket_stack, env=env)

        LandingStack(self, "LandingStack", env=env)
