import typing as t

from aws_cdk import (
    NestedStack,
    aws_iam,
)
from aws_cdk import aws_route53 as aws_r53
from constructs import Construct

from cdk_stack.conf import (
    ACCOUNT_ID,
    ACME_TLD_ZONE_ID,
    HOSTED_ZONE,
    NATURA_TLD_ZONE_ID,
)
from cdk_stack.misc import get_fqdn


class DnsStack(NestedStack):
    def __init__(self, scope: Construct, construct_id: str, env: str, **kwargs: dict[str, t.Any]) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.main_zone = aws_r53.PublicHostedZone(
            self,
            id="main-zone",
            zone_name=get_fqdn(HOSTED_ZONE, env),
        )

        if env == "prod":
            # create natura.acme.im record in infra account

            aws_r53.CrossAccountZoneDelegationRecord(
                self,
                "cross-acc-zone-delegation-rec",
                delegated_zone=self.main_zone,
                parent_hosted_zone_id=ACME_TLD_ZONE_ID,
                delegation_role=aws_iam.Role.from_role_arn(
                    self, id="Role", role_arn=f'arn:aws:iam::{ACCOUNT_ID["infra"]}:role/DnsDelegationRoleAcme'
                ),
            )

            # policy to allow sub-accounts to make changes in TLD
            dns_policy = aws_iam.ManagedPolicy(
                self,
                id="dns-delegation-allow-policy",
                statements=[
                    aws_iam.PolicyStatement(
                        effect=aws_iam.Effect.ALLOW,
                        actions=["route53:ChangeResourceRecordSets"],
                        resources=["*"],
                    )
                ],
            )

            deleg_role = aws_iam.Role(
                self,
                id="dns-delegation-role",
                role_name="DnsDelegationRoleNatura",
                assumed_by=aws_iam.CompositePrincipal(
                    aws_iam.AccountPrincipal(ACCOUNT_ID["dev"]),
                ),
            )

            dns_policy.attach_to_role(deleg_role)

        else:
            # create env.natura.acme.im record in natura prod account

            aws_r53.CrossAccountZoneDelegationRecord(
                self,
                "cross-acc-zone-delegation-rec",
                delegated_zone=self.main_zone,
                parent_hosted_zone_id=NATURA_TLD_ZONE_ID,
                delegation_role=aws_iam.Role.from_role_arn(
                    self, id="Role", role_arn=f'arn:aws:iam::{ACCOUNT_ID["prod"]}:role/DnsDelegationRoleNatura'
                ),
            )
