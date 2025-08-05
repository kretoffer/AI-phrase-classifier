from src.logic.sinanimizator import sinanimizate
from src.logic.parse_dataset import parse_dataset
from src.logic.template_to_hand import template2hand

from src.shemes import Project

import json


def test_sinanimizate():
    assert sinanimizate({}, "hello world") == "hello world"
    assert sinanimizate({"nika": "NIKA"}, "hello world") == "hello world"
    assert sinanimizate({"hello world": "Hello world!"}, "hello world") == "Hello world!"

def test_parse_dataset():
    with open("./tests/testdataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
    project = Project(name="test", status="off", intents=[], entities=[])
    assert parse_dataset(dataset, project) == ([
        'about_entity', 
        'about_lab_work_condition', 
        'subdividing', 
        'about_letter_search', 
        'about_skill', 
        'about_weather', 
        'about_lab_work_deadline', 
        'color_message',
        'greeting'
    ], ["rrel_entity", "rrel_color"])

def test_template_to_hand():
    with open("./tests/template_to_hand_test.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        template = data["template"]
        result = data["result"]
    assert template2hand(template) == result

