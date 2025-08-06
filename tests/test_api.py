from src.api.general import new_project
from src.api.info_api import project_info
from src.shemes import DatasetTemplateData, Project, UpdateDatasetFormData, FormSlot, Slot
from src.api.project_edit_general import delete_project, add_intent_or_entity, delete_entity, delete_intent
from src.api.edit_dataset import update_dataset, update_dataset_template, update_dataset_with_file, replace_dataset_with_file
from config import projects_dir

from uuid import uuid4
import os
import yaml
import json

test_uuid = uuid4().hex
test_name = f"test-{test_uuid}"
test_name_2 = f"test-2-{test_uuid}"
project = Project(name=test_name, status="off", intents=[], entities=[])

class TestGeneral:
    def test_src(self):
        assert os.path.exists(projects_dir)

    def test_project_creation(self):
        new_project(test_name)
        assert os.path.exists(f"{projects_dir}/{test_name}")

        with open(f"{projects_dir}/{test_name}/config.yaml", "r", encoding="utf-8") as f:
            assert yaml.load(f, Loader=yaml.SafeLoader) == project.model_dump()
        with open(f"{projects_dir}/{test_name}/dataset.json", "r", encoding="utf-8") as f:
            assert f.read() == '{"hand-data": [], "template-data": []}'
        with open(f"{projects_dir}/{test_name}/educated.json", "r", encoding="utf-8") as f:
            assert f.read() == "{}"
        with open(f"{projects_dir}/{test_name}/sinonimz.json", "r", encoding="utf-8") as f:
            assert f.read() == "{}"

        assert new_project(test_name) == {"error": "a project with this name already exists"}
        assert new_project(test_name_2) != {"error": "a project with this name already exists"}
        assert os.path.exists(f"{projects_dir}/{test_name_2}")

    def test_project_info(self):
        assert project_info(test_name) == project.model_dump()

    def test_delete_project(self):
        assert delete_project(test_uuid, test_uuid) == {"error": "no such project exists"}
        assert delete_project(test_name_2, test_name) == {"error", "name of project and name in input don't match"}
        delete_project(test_name_2, test_name_2)
        assert not os.path.exists(f"{projects_dir}/{test_name_2}")

class TestEditProjectGeneral:
    def test_add_intent_and_entity(self):
        assert add_intent_or_entity(test_uuid, [], []) == {"error": "no such project exists"}
        add_intent_or_entity(test_name, None, None)

        project = project_info(test_name)
        assert not project["intents"] and not project["entities"]

        add_intent_or_entity(test_name, "about_entity", None)

        project = project_info(test_name)
        assert project["intents"] == ["about_entity"] and not project["entities"]

        add_intent_or_entity(test_name, None, "rrel_entity")

        project = project_info(test_name)
        assert project["intents"] == ["about_entity"] and project["entities"] == ["rrel_entity"]

        add_intent_or_entity(test_name, "color_message", "rrel_color")

        project = project_info(test_name)
        assert project["intents"] == ["about_entity", "color_message"] and project["entities"] == ["rrel_entity", "rrel_color"]

    def test_delete_intent_and_entity(self):
        assert delete_entity(test_uuid, " ") == {"error": "no such project exists"}
        assert delete_intent(test_uuid, " ") == {"error": "no such project exists"}
        assert delete_entity(test_name, " ") == {"error": "no such entity in this project"}
        assert delete_intent(test_name, " ") == {"error": "no such intent in this project"}
        delete_entity(test_name, "rrel_entity")
        assert "rrel_entity" not in project_info(test_name)["entities"]
        delete_intent(test_name, "about_entity")
        assert "about_entity" not in project_info(test_name)["intents"]



