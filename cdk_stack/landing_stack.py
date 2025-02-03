import typing as t

from aws_cdk import (
    NestedStack,
    SecretValue,
)
from aws_cdk import aws_amplify_alpha as aws_amp
from aws_cdk import aws_codebuild as aws_cb
from constructs import Construct

from cdk_stack.conf import HOSTED_ZONE
from cdk_stack.misc import get_fqdn

# AWS Amplify is not as flexible as a raw CloudFront/S3 solution, but we don't really need that flexibility for static
# web content. It's easier to setup and we get a CI/CD out of the box, that's all we need for a static web app.

# make sure AWS Amplify app was installed in GitHub (for landing repo in natura account) and token has been generated:
# https://docs.aws.amazon.com/amplify/latest/userguide/setting-up-GitHub-access.html#setting-up-github-app-cloudformation

# aws secretsmanager create-secret --name github-access-token --secret-string "xxx" --profile natura-dev \
#    --region us-east-1
# aws secretsmanager create-secret --name github-access-token --secret-string "xxx" --profile natura-prod \
#    --region us-east-1

# You should run a manual build from AWS Amplify console after stack deployment is complete!

# TODO: switch to CodeCommit once https://github.com/aws-amplify/amplify-hosting/issues/64 is resolved


class LandingStack(NestedStack):
    def __init__(
        self, scope: Construct, construct_id: str, env: str, prefix: t.Optional[str] = None, **kwargs: dict[str, t.Any]
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        app = aws_amp.App(
            self,
            "landing-amp-app",
            source_code_provider=aws_amp.GitHubSourceCodeProvider(
                oauth_token=SecretValue.secrets_manager("github-access-token"),
                owner="acme-im",
                repository="natura-landing",
            ),
            build_spec=aws_cb.BuildSpec.from_object(
                {
                    "version": "1.0",
                    "frontend": {
                        "artifacts": {
                            "baseDirectory": "/www",
                            "files": ["**/*"],
                        },
                    },
                }
            ),
            custom_response_headers=[
                aws_amp.CustomResponseHeader(
                    pattern="**/*", headers={"Cache-Control": "public, max-age=31536000, immutable"}
                )
            ],
        )
        main_branch = app.add_branch(
            "branch-main",
            branch_name="main",
            stage="PRODUCTION",
            auto_build=True,
        )
        domain = app.add_domain(get_fqdn(HOSTED_ZONE, env, prefix))
        domain.map_root(main_branch)
