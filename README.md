# NaturaTest App: Infrastructure as Code

## Init

The CDK project was created using:

    mkdir infra
    cd infra
    cdk init sample-app --language python
    rm -rf .venv
    rm source.bat

Cleanup sources, e.g. remove hard-coded wrong region (us-west-2)

You should create a new virtualenv if you've just cloned this project from a git repo:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .

Bootstrap CDK (run once in a lifetime):

    cdk bootstrap --profile natura-dev -c env=dev
    cdk bootstrap --profile natura-prod -c env=prod

## Deploy

Deploy changes (every time CDK stack or natura/jobs change):

Prod should be deployed first (because of DNS).
Before dev deployment, make sure NATURA_TLD_ZONE_ID correspond to natura.acme.im ZONE ID in natura prod account.

    cdk deploy --profile natura-dev -c env=dev
    cdk deploy --profile natura-prod -c env=prod

## Test

Manual steps need to be taken after `cdk deploy`:
* run generation of a json data (use lambda function test to trigger action) after the very first deploy. Payload:
```
  {
      "s3_bucket_name": "cdn.natura.acme.im"
  }
```
* run landing website build (AWS Amplify -> Main -> build)

### Smoke tests

    https://natura.acme.im
    https://natura.acme.im/privacy_policy.txt
    https://cdn.natura.acme.im/assets/video/flag_eagle.mp4
    https://cdn.natura.acme.im/civics_test/2008/data.json
