import json
from typing import Any
import pytest

from burger_maker import app


@pytest.fixture()
def getrecipes_event():
    with open("./events/GET_recipes_event.json", "r") as fp:
        return json.load(fp)


def test_menu_should_be_as_expected(getrecipes_event, lambda_context):
    response = app.lambda_handler(getrecipes_event, lambda_context)
    expected = json.dumps(
        ["cheeseburger", "bacon", "farmer", "fish", "veggie", "frenchie"],
        separators=(",", ":"),
    )

    assert response["statusCode"] == 200
    assert response["body"] == expected


@pytest.fixture()
def ordercheeseburger_event():
    with open("./events/DELETE_burgers_cheeseburger_event.json", "r") as fp:
        return json.load(fp)


def test_cheeseburger_should_be_as_expected(ordercheeseburger_event, lambda_context):
    response = app.lambda_handler(ordercheeseburger_event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["name"] == "cheeseburger"
    assert len(body["ingredients"]) == 7
    assert body["ingredients"][0]["name"] == "bun"
    assert body["ingredients"][1]["name"] == "red onion"
    assert body["ingredients"][2]["name"] == "tomato"
    assert body["ingredients"][3]["name"] == "ketchup"
    assert body["ingredients"][4]["name"] == "salad"
    assert body["ingredients"][5]["name"] == "cheddar"
    assert body["ingredients"][6]["name"] == "steak"


@pytest.fixture()
def orderanyburger_event():
    with open("./events/DELETE_burgers_any_event.json", "r") as fp:
        return json.load(fp)


def test_anyburger_should_be_delivered(orderanyburger_event, lambda_context):
    response = app.lambda_handler(orderanyburger_event, lambda_context)
    assert response["statusCode"] == 200


@pytest.fixture()
def ordernonexistingburger_event():
    with open("./events/DELETE_burgers_foie-gras_event.json", "r") as fp:
        return json.load(fp)


def test_nonexistingburger_should_fail(ordernonexistingburger_event, lambda_context):
    response = app.lambda_handler(ordernonexistingburger_event, lambda_context)
    assert response["statusCode"] == 404
