import typing as t

from aws_cdk import (
    Duration,
    NestedStack,
    aws_ecr,
)
from aws_cdk import aws_events as aws_ev
from aws_cdk import aws_events_targets as aws_evt
from aws_cdk import aws_iam
from aws_cdk import aws_lambda as aws_lamb
from constructs import Construct

from cdk_stack.bucket_stack import BucketStack
from cdk_stack.conf import ACCOUNT_ID

UPD_CIVICS_TEST_FUNC_NAME = "upd_civics_test"
PUSH_NOTIFICATIONS_FUNC_NAME = "push_notifications"
ECR_REPO_NAME = "im.acme.natura.jobs"
JOBS_DOCKER_IMAGE_TAG = "0.0.4"


class JobsStack(NestedStack):
    def __init__(
        self, scope: Construct, construct_id: str, bucket_stack: BucketStack, env: str, **kwargs: dict[str, t.Any]
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ecr_repo = aws_ecr.Repository.from_repository_arn(
            self,
            id="ecr-repo-lambda",
            repository_arn=f"arn:aws:ecr:us-east-1:{ACCOUNT_ID['infra']}:repository/{ECR_REPO_NAME}",
        )

        policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "s3:*",
            ],
            resources=[f"arn:aws:s3:::{bucket_stack.domain}/*"],
        )

        lamb_func1 = aws_lamb.DockerImageFunction(
            self,
            id=UPD_CIVICS_TEST_FUNC_NAME,
            code=aws_lamb.DockerImageCode.from_ecr(
                repository=ecr_repo,
                cmd=[f"jobs/{UPD_CIVICS_TEST_FUNC_NAME}.aws_lambda_handler"],
                tag_or_digest=JOBS_DOCKER_IMAGE_TAG,
            ),
            initial_policy=[policy],
            timeout=Duration.seconds(300),
            memory_size=256,
        )

        lamb_func2 = aws_lamb.DockerImageFunction(
            self,
            id=PUSH_NOTIFICATIONS_FUNC_NAME,
            code=aws_lamb.DockerImageCode.from_ecr(
                repository=ecr_repo,
                cmd=[f"jobs/{PUSH_NOTIFICATIONS_FUNC_NAME}.aws_lambda_handler"],
                tag_or_digest=JOBS_DOCKER_IMAGE_TAG,
            ),
            initial_policy=[policy],
            timeout=Duration.seconds(30),
            memory_size=128,
        )

        # run on the tenth day of each month.
        aws_ev.Rule(
            self,
            id="upd-civics-test-data-rule",
            schedule=aws_ev.Schedule.cron(minute="10", hour="10", day="10"),
            targets=[
                aws_evt.LambdaFunction(
                    handler=lamb_func1,
                    event=aws_ev.RuleTargetInput.from_object({"s3_bucket_name": bucket_stack.domain}),
                )
            ],
        )

        if env == "prod":  # avoid double runs
            # run every 12 hours
            aws_ev.Rule(
                self,
                id="push-notifications-rule",
                schedule=aws_ev.Schedule.cron(minute="0", hour="*/12"),
                targets=[
                    aws_evt.LambdaFunction(
                        handler=lamb_func2,
                        event=aws_ev.RuleTargetInput.from_object({"s3_bucket_name": bucket_stack.domain}),
                    )
                ],
            )
