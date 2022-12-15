# Python Serverless on AWS project sample

This project sample shows the usage of _to be continuous_ templates:

* Python
* SonarQube (from [sonarcloud.io](https://sonarcloud.io/))
* AWS (Amazon Web Services)
* Postman

The project deploys a basic serverless API developped in Python (3.9) on AWS Lambda, and implements automated accetance tests with Postman.

## Python template features

This project uses the following features from the GitLab CI Python template:

* Uses the `pyproject.toml` build specs file with [Poetry](https://python-poetry.org/) as build backend,
* Enables the [pytest](https://docs.pytest.org/) unit test framework by declaring the `$PYTEST_ENABLED` in the `.gitlab-ci.yml` variables,
* Enables [pylint](https://pylint.pycqa.org/) by declaring the `$PYLINT_ENABLED` in the `.gitlab-ci.yml` variables,
* Enables the [Bandit](https://pypi.org/project/bandit/) SAST analysis job by declaring the `$BANDIT_ENABLED` and skips the `B311`
  test by overriding `$BANDIT_ARGS` in the `.gitlab-ci.yml` variables.

The Python template also enforces:

* [test report integration](https://docs.gitlab.com/ee/ci/testing/unit_test_reports.html),
* and [code coverage integration](https://docs.gitlab.com/ee/user/project/pipelines/settings.html#test-coverage-report-badge).

## SonarQube template features

This project uses the following features from the SonarQube template:

* Defines the `SONAR_HOST_URL` (SonarQube server host),
* Defines `organization` & `projectKey` from [sonarcloud.io](https://sonarcloud.io/) in `sonar-project.properties`,
* Defines :lock: `$SONAR_TOKEN` as secret CI/CD variable,
* Uses the `sonar-project.properties` to specify project specific configuration:
    * source and test folders,
    * code coverage report (from `pytest`),
    * unit test reports (from `pytest`).

## AWS template features

This project uses AWS [Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/) 
(SAM) to build and deploy this serverless application on AWS.

This project uses the following features from the AWS template:

* Enables review, staging and production environments (by declaring the `$AWS_REVIEW_ENABLED`, `$AWS_STAGING_ENABLED` and `$AWS_PROD_ENABLED` in the project variables); the AWS template implements [environments integration](https://gitlab.com/to-be-continuous/samples/maven-on-gcloud/environments) and review environment cleanup support (manually or when the related development branch is deleted).
* Configures AWS authentication by specifying AWS credentials (`$AWS_ACCESS_KEY_ID`, `$AWS_SECRET_ACCESS_KEY` and `$AWS_DEFAULT_REGION`) as (secret) CI/CD project variables.
* Overrides the Docker image used by the template (`AWS_CLI_IMAGE`) with the [official](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-image-repositories.html) `public.ecr.aws/sam/build-python3.9:latest`.

In order to perform AWS deployments, the project implements:

* `aws-deploy.sh` script: generic deployment script using `sam build` and `sam deploy` commands,
* `aws-cleanup.sh` script: generic cleanup script using the `sam delete` command.

Both scripts make use of variables dynamically evaluated and exposed by the AWS template:

* `${environment_name}`: the application target name to use in this environment (ex: `myproject-review-fix-bug-12` or `myproject-staging`); 
  this is used as the SAM/CloudFormation [stack name](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-deploy.html),
* `${environment_type}`: the environment type (`review`, `integration`, `staging` or `production`); added as a tag.

Lastly, the deployment script implements the [dynamic way](https://docs.gitlab.com/ee/ci/environments/#set-dynamic-environment-urls-after-a-job-finishes) of
defining the environment URLs: retrieves the generated server URL as a [CloudFormation output](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html), and dumps it into a `environment_url.txt` file, supported by the template.

## Postman

This project also implements Postman acceptance tests, simply storing test collections in the default [postman/](./postman) directory.

The upstream deployed environment base url is simply referenced in the Postman tests by using the [{{base_url}} variable](https://learning.postman.com/docs/sending-requests/variables/) evaluated by the template.
