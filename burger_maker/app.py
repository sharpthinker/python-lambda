import json
import os
from typing import Any
import uuid
import random
import re

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.api_gateway import ApiGatewayResolver
from aws_lambda_powertools.event_handler.exceptions import NotFoundError

# https://awslabs.github.io/aws-lambda-powertools-python/#features
tracer = Tracer()
logger = Logger()
metrics = Metrics()
app = ApiGatewayResolver()

# Global variables are reused across execution contexts (if available)
# session = boto3.Session()

burger_recipes = {
    "cheeseburger": [
        "bun",
        "red onion",
        "tomato",
        "ketchup",
        "salad",
        "cheddar",
        "steak",
    ],
    "bacon": ["bun", "bacon", "garlic sauce", "brie", "steak", "tomato"],
    "farmer": ["bun", "red onion", "bbq sauce", "stilton", "chicken", "tomato"],
    "fish": ["bun", "tartare sauce", "cucumber", "old gouda", "fish fillet"],
    "veggie": [
        "bun",
        "goat cheese",
        "tomato confit",
        "red onion",
        "super-secret veggie steak",
    ],
    "frenchie": ["baguette", "butter", "brie", "smoked ham"],
}


@app.get("/recipes")
def gime_the_menu() -> list[str]:
    return list(burger_recipes.keys())


@app.delete("/burgers/<recipe>")
def prepare_a_burger(recipe: str) -> dict[str, Any]:
    if recipe == "any":
        # pick one at random
        recipe = random.choice(list(burger_recipes.keys()))

    ingredients = burger_recipes.get(recipe)
    if ingredients is None:
        raise NotFoundError(f"No such recipe: {recipe}")

    return {
        "name": recipe,
        "id": str(uuid.uuid1()),
        "ingredients": list(
            map(lambda name: {"id": str(uuid.uuid1()), "name": name}, ingredients)
        ),
    }


@metrics.log_metrics(capture_cold_start_metric=True)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event: Any, context: LambdaContext) -> Any:
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
    return app.resolve(event, context)
