from enum import Enum
from fastapi import FastAPI, Body, Header, Query, Form
from fastapi.responses import RedirectResponse, HTMLResponse

from fastui import FastUI, prebuilt_html, AnyComponent
from fastui import components as c
from fastui.components.display import DisplayLookup
from fastui.events import GoToEvent, BackEvent, PageEvent
from fastui.forms import fastui_form

from pydantic import BaseModel, Field, create_model, field_validator, validator

from typing import Annotated, Iterable, Literal, List, Optional, Dict
import os
import yaml
import json
import shutil

from config import projects_dir, projects_dir_without_system_dir, more_then_one_user

from src.start_education import start_educate
from src.classifier import classificate


c.Page.model_rebuild()
c.ModelForm.model_rebuild()
c.Form.model_rebuild()

app = FastAPI()

class Project(BaseModel):
    name: str
    status: Literal["work", "educated", "off", "error"]
    hidden_layer: int = Field(50, gt=0)
    epochs: int = Field(0, gt=-1)
    learning_rate: float = Field(0.01, gt=0)
    embedding_dim: int = Field(32, gt=0)
    intents: List[str]
    activation_method: Literal["sigmoid"]
    entities: List[str]

class EditForm(BaseModel):
    #name: Optional[str] = Field("test", description="name of the project", title="Project name")
    hidden_layer: int = Field(50, gt=0, title="hidden neurouns", description="the count of neurons in hidden layer")
    epochs: int = Field(0, title="epochs", description="try 0 to auto set")
    learning_rate: float = Field(0.01, gt=0)
    embedding_dim: int = Field(32)
    activation_method: Literal["sigmoid"] = "sigmoid"

class FormAddToDatasetHand(BaseModel):
    classification: str
    slots: List[Dict[str, str]]
    text: str

if projects_dir_without_system_dir:
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
    projects_dir = f"{parent_dir}/{projects_dir}"

if not os.path.exists(projects_dir):
    os.makedirs(projects_dir)

userID = "admin"
if not os.path.exists(f"{projects_dir}/{userID}"):
    os.makedirs(f"{projects_dir}/{userID}")
    with open(f"{projects_dir}/{userID}/user.yaml", "w") as f:
        user_data = {
            "name": userID,
            "password": "admin",
            "projects": []
        }
        yaml.dump(user_data, f, allow_unicode=True, sort_keys=False)

def validate_request_post(userID, data: dict, elements_in_data: Iterable):
    if not userID:
        return {"error": "user identifier not specified"}
    if not all([el in data for el in elements_in_data]):
        return {"error": "not all data specified"}
    if not os.path.exists(projects_dir + "/" + str(userID)):
        return {"error": "user not registered"}


def validate_request_get(userID):
    if not userID:
        return {"error": "user identifier not specified"}
    if not os.path.exists(projects_dir + "/" + str(userID)):
        return {"error": "user not registered"}


@app.post("/api/new-project", response_model=FastUI, response_model_exclude_none=True, tags=["api"])
def new_project(name:str = Form("test", alias="project-name")):

    if os.path.exists(f"{projects_dir}/admin/{name}"):
        return {"error": "a project with this name already exists"}
    
    os.makedirs(f"{projects_dir}/admin/{name}")
    os.makedirs(f"{projects_dir}/admin/{name}/models")

    with open(f"{projects_dir}/admin/user.yaml", "r+", encoding="utf-8") as f:
        user_data = yaml.safe_load(f)
        user_data["projects"].append(name)
        f.seek(0)
        f.truncate()
        yaml.dump(user_data, f, allow_unicode=True, sort_keys=False)
    
    with open(f"{projects_dir}/admin/{name}/config.yaml", "w", encoding="utf-8") as f:
        project=Project(
            name=name,
            status="off",
            hidden_layer=50,
            epochs=0,
            learning_rate=0.01,
            embedding_dim=32,
            intents=[],
            activation_method="sigmoid",
            entities=[]
            )
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)

    with open(f"{projects_dir}/admin/{name}/dataset.json", "x", encoding="utf-8") as f:
        f.write('{"hand-data": [], "template-data": []}')

    
    return [c.FireEvent(event=GoToEvent(url=f"/web/project/{name}"))]


@app.post("/update_dataset")
def update_dataset(data: dict = Body(), userID: str = Header("admin", alias="userID")):
    if resp := validate_request_post(userID, data, ("project", "hand-data", "template-data")):
        return resp
    
    if not os.path.exists(projects_dir+"/"+str(userID)+"/"+str(data["project"])):
        return {"error": "no such project exists"}
    
    with open(f"{projects_dir}/{userID}/{data['project']}/dataset.json", "r+", encoding="utf-8") as f:
        dataset = json.load(f)
        dataset["hand-data"].extend(data["hand-data"])
        dataset["template-data"].extend(data["template-data"])
        f.seek(0)
        f.truncate()
        json.dump(dataset, f, ensure_ascii=False, indent=1)

    return {"success": "good"}


@app.get("/api/start_education/{name}", response_model=FastUI, response_model_exclude_none=True, tags=["api"])
def start_education(name):
    start_educate(f"{projects_dir}/admin/{name}")
    return [c.FireEvent(event=GoToEvent(url=f"/web/project/{name}"))]


@app.post("/api/update-project/{name}", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui api"])
def update_project(name: str, form: Annotated[EditForm, fastui_form(EditForm)]):
    if not os.path.exists(f"{projects_dir}/admin/{name}"):
        return {"error": "no such project exists"}
    
    with open(f"{projects_dir}/admin/{name}/config.yaml", "r+", encoding="utf-8") as f:
        project = Project.model_validate(yaml.load(f, Loader=yaml.SafeLoader))
        project = project.model_copy(update=form.model_dump())
        f.seek(0)
        f.truncate()
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)
    
    return []

@app.post("/api/delete-project/{name}", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui api"])
def delete_project(name: str, name_form: str = Form(None, alias="project-name")):
    if not os.path.exists(f"{projects_dir}/admin/{name}"):
        return {"error": "no such project exists"}
    
    if name != name_form:
        return {"error", "name of project and name in input don't match"}
    
    shutil.rmtree(f"{projects_dir}/admin/{name}", ignore_errors=True)
    
    return [c.FireEvent(event=GoToEvent(url="/web/"))]


@app.post("/api/add-intent-entity/{name}", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui api"])
def add_intent_or_entity(name: str, intent_name: Optional[str] = Form(None, alias="intent-name"), entity_name: Optional[str] = Form(None, alias="entity-name")):
    if not os.path.exists(f"{projects_dir}/admin/{name}"):
        return {"error": "no such project exists"}
    
    print(intent_name, entity_name)
    
    with open(f"{projects_dir}/admin/{name}/config.yaml", "r+", encoding="utf-8") as f:
        project = Project.model_validate(yaml.load(f, Loader=yaml.SafeLoader))

        if intent_name:
            project.intents.append(intent_name)
        if entity_name:
            project.entities.append(entity_name)

        f.seek(0)
        f.truncate()
        yaml.dump(project.model_dump(), f, allow_unicode=True, sort_keys=False)
    
    return [
        c.FireEvent(event=PageEvent(name="add-intent-modal", clear=True)),
        c.FireEvent(event=PageEvent(name="add-entity-modal", clear=True))
    ]


@app.get("/message/{userID}/{project}", tags=["api"])
def classificate_hand(userID, project, question:str = Query("Что такое AI-classifier", alias="q")):
    if resp := validate_request_get(userID):
        return resp
    
    if not os.path.exists(projects_dir+"/"+str(userID)+"/"+str(project)):
        return {"error": "no such project exists"}

    intent = classificate(f"{projects_dir}/{userID}/{project}", question)
    return {"intent": intent}

#WEB INTERFACE
def template_edit_page(*components: AnyComponent, name: Optional[str] = None) -> List[AnyComponent]:
    return [
        c.PageTitle(text= f"Edit {name}" if name else "classifier"),
        c.Navbar(
            title="Classifier Interface",
            title_event=GoToEvent(url="/web/"),
            start_links=[
                c.Link(
                    components=[c.Text(text="General")],
                    on_click=GoToEvent(url=f"/web/project/{name}/edit"),
                    active="startswith:/edit"
                ),
                c.Link(
                    components=[c.Text(text="Intents")],
                    on_click=GoToEvent(url=f"/web/project/{name}/edit/intents"),
                    active="startswith:/intents"
                ),
                c.Link(
                    components=[c.Text(text="Entities")],
                    on_click=GoToEvent(url=f"/web/project/{name}/edit/entities"),
                    active="startswith:/entities"
                ),
                c.Link(
                    components=[c.Text(text="Dataset")],
                    on_click=GoToEvent(url=f"/web/project/{name}/edit/dataset"),
                    active="startswith:/dataset"
                )
            ]
        ),
        c.Page(components=[*components]),
        c.Footer(
            extra_text="AI phrase classifier by kretoffer",
            links=[
                c.Link(components=[c.Text(text="GitHub")], on_click=GoToEvent(url="https://github.com/kretoffer/ai-phrase-classifier"))
            ]
        )
    ] # type: ignore


@app.get("/", tags=["fast ui interface"])
def main_rout():
    return RedirectResponse(url="/web/")

@app.get("/api/web/", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui interface"])
def main_web():
    projects = [f for f in os.listdir(f"{projects_dir}/admin") if os.path.isdir(os.path.join(f"{projects_dir}/admin", f))]
    projects = [Project.model_validate(yaml.load(open(f"{projects_dir}/admin/{el}/config.yaml", "r"), Loader=yaml.SafeLoader)) for el in projects]

    return [
        c.Page(
            components=[ # type: ignore
                c.Heading(text="Projects", level=1),    # type: ignore
                c.Table(
                    data=projects,
                    columns=[
                        DisplayLookup(field="name", on_click=GoToEvent(url="/web/project/{name}")),
                        DisplayLookup(field="status")
                    ]
                ),
                c.Button(text="New project", on_click=PageEvent(name="new-project-modal")),
                c.Modal(
                    title="New project",
                    body=[
                        c.Form(
                            submit_url="/api/new-project",
                            form_fields=[
                                c.FormFieldInput(name="project-name", title="Name of new project", required=True)
                            ]
                        ) # type: ignore
                    ],
                    open_trigger=PageEvent(name="new-project-modal")
                )
            ]
        )
    ]


@app.get("/api/web/project/{name}/edit", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui interface"])
def edit_page(name: str):
    if not os.path.exists(f"{projects_dir}/admin/{name}"):
        return c.Page(
            components=[ # type: ignore
                c.Link(components=[c.Text(text='Back')], on_click=GoToEvent(url="/web/")),
                c.Heading(text="Project not exists", level=2)
            ]
        )

    project = Project.model_validate(yaml.load(open(f"{projects_dir}/admin/{name}/config.yaml", "r"), Loader=yaml.SafeLoader))
    
    class EditForm(BaseModel):
        #name: Optional[str] = Field(project.name, description="name of the project", title="Project name")
        hidden_layer: int = Field(project.hidden_layer, gt=0, title="hidden neurouns", description="the count of neurons in hidden layer")
        epochs: int = Field(project.epochs, title="epochs", description="try 0 to auto set")
        learning_rate: float = Field(project.learning_rate, gt=0)
        embedding_dim: int = Field(project.embedding_dim)
        activation_method: Literal["sigmoid"] = project.activation_method

    return template_edit_page(
        c.Page(
            components=[ # type: ignore
                c.Heading(text=project.name, level=1),
                c.ModelForm(model=EditForm, submit_url=f"/api/update-project/{project.name}", submit_trigger=PageEvent(name="submit-edits"), footer=[]),
                c.Paragraph(text=""),
                c.Button(text="Cancel", named_style="secondary", on_click=GoToEvent(url=f"/web/project/{project.name}")),
                c.Text(text=" "),
                c.Button(text="Save", on_click=PageEvent(name="submit-edits")),
                c.Paragraph(text=""),
                c.Button(text="Delete", named_style="warning", on_click=PageEvent(name="delete-project-modal")),
                c.Modal(
                    title = "Delete project",
                    body = [
                        c.Form(
                            form_fields=[
                                c.FormFieldInput(name="project-name", title="Project name", required=True, description=f"to delete this project print project name ({project.name})")
                            ],
                            footer = [],
                            submit_url=f"/api/delete-project/{project.name}",
                            submit_trigger=PageEvent(name='delete-project-modal-submit')
                        )
                    ],
                    footer = [
                        c.Button(text='Cancel', named_style='secondary', on_click=PageEvent(name='delete-project-modal', clear=True)),
                        c.Button(text='Delete', on_click=PageEvent(name='delete-project-modal-submit'), named_style="warning")
                    ],
                    open_trigger = PageEvent(name="delete-project-modal")
                )
            ]
        ),
        name=project.name
    )

class SomeEntity(BaseModel):
    name: str

@app.get("/api/web/project/{name}/edit/intents", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui interface"])
def edit_intents_page(name):
    if not os.path.exists(f"{projects_dir}/admin/{name}"):
        return c.Page(
            components=[ # type: ignore
                c.Link(components=[c.Text(text='Back')], on_click=GoToEvent(url="/web/")),
                c.Heading(text="Project not exists", level=2)
            ]
        )

    project = Project.model_validate(yaml.load(open(f"{projects_dir}/admin/{name}/config.yaml", "r"), Loader=yaml.SafeLoader))
    intents = [SomeEntity(name=el) for el in project.intents]

    table = c.Heading(text="So far, not one intent", level=2) if not intents else c.Table(
            data=intents,
            columns=[
                DisplayLookup(field="name")
            ]
        )

    return template_edit_page(
        table,
        c.Button(text="add intent", on_click=PageEvent(name="add-intent-modal")),
        c.Modal(
            title = "Create a new intent",
            body = [
                c.Paragraph(text="Create a new intent or import prepared"),
                c.Form(
                    form_fields=[
                        c.FormFieldInput(name="intent-name", title="Name of intent", required=True)
                    ],
                    footer = [],
                    submit_url=f"/api/add-intent-entity/{project.name}",
                    submit_trigger=PageEvent(name='add-intent-modal-submit')
                )
            ],
            footer = [
                c.Button(text='Cancel', named_style='secondary', on_click=PageEvent(name='add-intent-modal', clear=True)),
                #c.Button(text="Import prepared", named_style='secondary'),
                c.Button(text='Submit', on_click=PageEvent(name='add-intent-modal-submit'))
            ],
            open_trigger = PageEvent(name="add-intent-modal")
        ),
        name=project.name
    )


@app.get("/api/web/project/{name}/edit/entities", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui interface"])
def edit_entities_page(name):
    if not os.path.exists(f"{projects_dir}/admin/{name}"):
        return c.Page(
            components=[ # type: ignore
                c.Link(components=[c.Text(text='Back')], on_click=GoToEvent(url="/web/")),
                c.Heading(text="Project not exists", level=2)
            ]
        )

    project = Project.model_validate(yaml.load(open(f"{projects_dir}/admin/{name}/config.yaml", "r"), Loader=yaml.SafeLoader))
    entities = [SomeEntity(name=el) for el in project.entities]

    table = c.Heading(text="So far, not one entity", level=2) if not entities else c.Table(
            data=entities,
            columns=[
                DisplayLookup(field="name")
            ]
        )

    return template_edit_page(
        table,
        c.Button(text="add entity", on_click=PageEvent(name="add-entity-modal")),
        c.Modal(
            title = "Create a new entity",
            body = [
                c.Form(
                    form_fields=[
                        c.FormFieldInput(name="entity-name", title="Name of entity", required=True)
                    ],
                    footer = [],
                    submit_url=f"/api/add-intent-entity/{project.name}",
                    submit_trigger=PageEvent(name='add-entity-modal-submit')
                )
            ],
            footer = [
                c.Button(text='Cancel', named_style='secondary', on_click=PageEvent(name='add-entity-modal', clear=True)),
                c.Button(text='Submit', on_click=PageEvent(name='add-entity-modal-submit'))
            ],
            open_trigger = PageEvent(name="add-entity-modal")
        ),
        name=project.name
    )


@app.get("/api/web/project/{name}/edit/dataset", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui interface"])
def edit_dataset_page(name:str):
    if not os.path.exists(f"{projects_dir}/admin/{name}"):
        return c.Page(
            components=[ # type: ignore
                c.Heading(text="Project not exists", level=2)
            ]
        )
    project = Project.model_validate(yaml.load(open(f"{projects_dir}/admin/{name}/config.yaml", "r"), Loader=yaml.SafeLoader))

    class FormAddToDatasetHand(BaseModel):
        text: str = Field(title="Phrase")
        classification: Enum("Intent", {v: v for v in project.intents}) # type: ignore

    FormAddToDatasetHandFull = create_model(
        "FormAddToDatasetHandFull",
        __base__=FormAddToDatasetHand,
        **{el: (Optional[str], Field(description=f"If your phrase does not contain an {el}, leave the field blank. Otherwise, enter the name of the entity")) for el in project.entities} # type: ignore
    )
            

    return template_edit_page(
        c.Heading(text="Add to dataset", level=2),
        c.ModelForm(
            submit_url="",
            model=FormAddToDatasetHandFull
        ),
        c.Paragraph(text=""),
        c.Heading(text="Add to dataset template", level=2),
        c.Paragraph(text="You can only add template phrases through a file"),
        c.Paragraph(text=""),
        c.Heading(text="Add to dataset with file", level=2),
        c.Form(
            submit_url="",
            form_fields=[
                c.FormFieldFile(name="dataset", title="Upload dataset", required=True, multiple=True)
            ]
        ),
        name=project.name
    )

@app.get("/api/web/project/{name}", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui interface"])
def project_page(name: str):
    if not os.path.exists(f"{projects_dir}/admin/{name}"):
        return c.Page(
            components=[ # type: ignore
                c.Heading(text="Project not exists", level=2)
            ]
        )
    project = Project.model_validate(yaml.load(open(f"{projects_dir}/admin/{name}/config.yaml", "r"), Loader=yaml.SafeLoader))

    return [
        c.Page(
            components=[ # type: ignore
                c.Heading(text=project.name, level=1),
                c.Link(components=[c.Text(text='Back')], on_click=GoToEvent(url="/web/")),
                c.Details(data=project),
                c.Button(text="Edit", on_click=GoToEvent(url=f"/web/project/{project.name}/edit")),
                c.Paragraph(text=" "),
                c.Button(text="educate", named_style="warning", on_click=PageEvent(name="educate")),
                c.Form(
                    form_fields= [],
                    submit_url=f"/api/start_education/{name}",
                    footer=[],
                    method="GET",
                    submit_trigger=PageEvent(name="educate")
                )
            ]
        ),
    ]

#END OF FILE

@app.get('/web/{path:path}', tags=["fast ui interface"])
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title='classifier web'))
