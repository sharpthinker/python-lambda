import json
import os
import uuid
import random
import re

# import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.api_gateway import ApiGatewayResolver

# https://awslabs.github.io/aws-lambda-powertools-python/#features
tracer = Tracer()
logger = Logger()
metrics = Metrics()
app = ApiGatewayResolver()

# error management
error_prefix_matcher = re.compile('^\\[(.+)\\].*$')
prefix_to_status = {
    'ok': 200,
    'created': 201,
    'accepted': 202,
    'nocontent': 204,
    'badrequest': 400,
    'unauthorized': 400,
    'forbidden': 403,
    'notfound': 404,
    'conflict': 409,
    'notimplemented': 501,
    'unavailable': 503,
    'serviceunavailable': 503,
}

# Global variables are reused across execution contexts (if available)
# session = boto3.Session()

burger_recipes = {
    'cheeseburger': ['bun', 'red onion', 'tomato', 'ketchup', 'salad', 'cheddar', 'steak'],
    'bacon': ['bun', 'bacon', 'garlic sauce', 'brie', 'steak', 'tomato'],
    'farmer': ['bun', 'red onion', 'bbq sauce', 'stilton', 'chicken', 'tomato'],
    'fish': ['bun', 'tartare sauce', 'cucumber', 'old gouda', 'fish fillet'],
    'veggie': ['bun', 'goat cheese', 'tomato confit', 'red onion', 'super-secret veggie steak'],
    'frenchie': ['baguette', 'butter', 'brie', 'smoked ham']
}

@app.get("/recipes")
def gime_the_menu():
    return list(burger_recipes.keys())


@app.delete("/burgers/<recipe>")
def prepare_a_burger(recipe):
    if recipe == 'any':
        # pick one at random
        recipe = random.choice(list(burger_recipes.keys()))
    
    ingredients = burger_recipes.get(recipe, None)
    if ingredients == None:
        raise Exception(f"[NotFound] No such recipe: {recipe}")

    return {
        "name": recipe,
        "id": str(uuid.uuid1()),
        "ingredients": list(map(lambda name: {"id": str(uuid.uuid1()), "name": name}, ingredients))
    }

@metrics.log_metrics(capture_cold_start_metric=True)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event, context: LambdaContext):
    """Sample pure Lambda function
    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format
        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
    context: object, required
        Lambda Context runtime methods and attributes
        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
    Returns
    -------
    API Gateway Lambda Proxy Output Format: dict
        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    try:
        # If we're using the default Lambda proxy integration, what should be the format for a successful response ?
        # response=app.resolve(event, context)
        # print("response: {response}")
        # if response is None:
        #     return {
        #         "statusCode": 204,
        #         "headers": get_headers()
        #     }
        # else:
        #     return {
        #         "statusCode": 200,
        #         "headers": get_headers(),
        #         "body": json.dumps(response)
        #     }
        return app.resolve(event, context)
    except Exception as err:
        logger.exception(err)
        error_message=str(err)
        match=error_prefix_matcher.match(error_message)
        statusCode=500
        if match is not None:
            statusCode = prefix_to_status.get(match.group(1).lower(), 500)
        return {
            "statusCode": statusCode,
            "headers": get_headers(),
            "body": json.dumps({"message": error_message})
        }

def get_headers():
    return {
        "access-control-allow-headers": "Content-Type,Authorization,X-Amz-Date",
        "access-control-allow-methods": "OPTIONS,HEAD,GET,POST,PUT,PATCH,DELETE",
        "access-control-allow-origin": "*",
    }