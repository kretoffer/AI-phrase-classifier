import json
import os
from typing import List, Literal, Optional
from fastapi import APIRouter, Request
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.events import GoToEvent, PageEvent
from fastui.components.display import DisplayLookup
from pydantic import BaseModel, Field, create_model
import yaml
from enum import Enum

from config import projects_dir
from src.logic.template_to_hand import template2hand
from src.shemes import Project, DeletebleEntity
from src.logic.sinanimizator import sinanimizate

router = APIRouter()

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
                    active="endswith:/edit"
                ),
                c.Link(
                    components=[c.Text(text="Intents")],
                    on_click=GoToEvent(url=f"/web/project/{name}/edit/intents"),
                    active="endswith:/intents"
                ),
                c.Link(
                    components=[c.Text(text="Entities")],
                    on_click=GoToEvent(url=f"/web/project/{name}/edit/entities"),
                    active="endswith:/entities"
                ),
                c.Link(
                    components=[c.Text(text="Dataset")],
                    on_click=GoToEvent(url=f"/web/project/{name}/edit/dataset"),
                    active="endswith:/dataset"
                ),
                c.Link(
                    components=[c.Text(text="View dataset")],
                    on_click=GoToEvent(url=f"/web/project/{name}/edit/dataset/view"),
                    active="endswith:/dataset/view"
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

@router.get("/project/{name}/edit", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui interface"])
def edit_page(name: str):
    if not os.path.exists(f"{projects_dir}/{name}"):
        return c.Page(
            components=[ # type: ignore
                c.Link(components=[c.Text(text='Back')], on_click=GoToEvent(url="/web/")),
                c.Heading(text="Project not exists", level=2)
            ]
        )

    project = Project.model_validate(yaml.load(open(f"{projects_dir}/{name}/config.yaml", "r"), Loader=yaml.SafeLoader))

    return template_edit_page(
        c.Page(
            components=[ # type: ignore
                c.Heading(text=project.name, level=1),
                c.Button(text="Download dataset", on_click=GoToEvent(url=f"/api/download-dataset/{project.name}", target="_blank")),
                c.Paragraph(text=""),
                c.Form(
                    submit_url=f"/api/open-project-dir/{project.name}",
                    form_fields=[],
                    footer=[],
                    submit_trigger=PageEvent(name="open-project-dir"),
                    method="GET"
                ),
                c.Button(text="Open project folder", on_click=PageEvent(name="open-project-dir")),
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


@router.get("/project/{name}/edit/dataset/view", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui interface"])
def view_dataset_page(name:str, request: Request):
    if not os.path.exists(f"{projects_dir}/{name}"):
        return c.Page(
            components=[ # type: ignore
                c.Heading(text="Project not exists", level=2)
            ]
        )
    project = Project.model_validate(yaml.load(open(f"{projects_dir}/{name}/config.yaml", "r"), Loader=yaml.SafeLoader))

    class DatasetHand(BaseModel):
        text: str = Field(title="Phrase")
        classification: Enum("Intent", {v: v for v in project.intents}) # type: ignore
        edit: Literal["Edit"] = Field("Edit")
        id: int

    DatasetHandFull = create_model(
        "DatasetHandFull",
        __base__= DatasetHand,
        **{el: (Optional[str], Field(None)) for el in project.entities} # type: ignore
    )

    with open(f"{projects_dir}/{name}/dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)

    with open(f"{projects_dir}/{name}/sinonimz.json", "r", encoding="utf-8") as f:
        sinonimz = json.load(f)

    hand_data = []    
    for id, el in enumerate(dataset["hand-data"]):
        text = el["text"]
        text_split = text.split()
        hand_data.append(DatasetHandFull(
            text=text,
            classification=el["classification"],
            id = id,
            **{slot["entity"]: sinanimizate(sinonimz, text[slot["start"]:slot["end"]]) for slot in el["slots"]}
        ))

    columns = [
        DisplayLookup(field="id"),
        DisplayLookup(field="text"),
        DisplayLookup(field="classification")
    ]

    columns.extend([DisplayLookup(field=entity) for entity in project.entities])
    columns.append(DisplayLookup(field="edit", on_click=GoToEvent(url="$2$1/edit-hand-element/{id}".replace("$1", project.name).replace("$2", str(request.base_url)))))
    hand_data_table = c.Table(data=hand_data, columns=columns) if hand_data else c.Heading(text="So far, not one phrase", level=3)

    class DatasetTemplate(BaseModel):
        text: str = Field(title="Phrase")
        classification: Enum("Intent", {v: v for v in project.intents}) # type: ignore

    DatasetTemplateFull = create_model(
        "DatasetTemplateFull",
        __base__= DatasetTemplate,
        **{el: (Optional[str], Field(None)) for el in project.entities} # type: ignore
    )

    template_dataset_hand = [template2hand(el) for el in dataset["template-data"]]
    template_dataset=[]
    for dataset in template_dataset_hand:
        data = []
        for el in dataset:
            text = el["text"]
            text_split = text.split()
            data.append(DatasetTemplateFull(
                text=text,
                classification=el["classification"],
                **{slot["entity"]: sinanimizate(sinonimz, text[slot["start"]:slot["end"]]) for slot in el["slots"]}
            ))
        template_dataset.append(data)

    columns = [
        DisplayLookup(field="text")
    ]
    columns.extend([DisplayLookup(field=entity) for entity in project.entities])

    template_data_tabels = []
    for template_id, data in enumerate(template_dataset):
        content = [
            c.Markdown(text=f"Template {template_id}    **{data[0].classification.value}**  "  \
                       f"[Edit template]({request.base_url}{project.name}/edit-template-element/{template_id})")
        ]
        template_data_tabels.extend(content)
        template_data_tabels.append(c.Table(data=data, columns=columns))

    if not template_data_tabels:
        template_data_tabels = [c.Heading(text="You haven't added any phrase templates yet.", level=3)]

    return template_edit_page(
        c.Heading(text="Hand data in dataset"),
        hand_data_table,
        c.Heading(text="Template data in dataset"),
        *template_data_tabels,
        name=project.name
    )


@router.get("/project/{name}/edit/intents", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui interface"])
def edit_intents_page(name: str, request: Request):
    if not os.path.exists(f"{projects_dir}/{name}"):
        return c.Page(
            components=[ # type: ignore
                c.Link(components=[c.Text(text='Back')], on_click=GoToEvent(url="/web/")),
                c.Heading(text="Project not exists", level=2)
            ]
        )

    project = Project.model_validate(yaml.load(open(f"{projects_dir}/{name}/config.yaml", "r"), Loader=yaml.SafeLoader))
    intents = [DeletebleEntity(name=el) for el in project.intents] # pyright: ignore[reportCallIssue]

    table = c.Heading(text="So far, not one intent", level=2) if not intents else c.Table(
            data=intents,
            columns=[
                DisplayLookup(field="name"),
                DisplayLookup(field='delete', on_click=GoToEvent(url="$2api/$1/delete-intent/{name}".replace("$1", project.name).replace("$2", str(request.base_url))))
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


@router.get("/project/{name}/edit/entities", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui interface"])
def edit_entities_page(name:str, request: Request):
    if not os.path.exists(f"{projects_dir}/{name}"):
        return c.Page(
            components=[ # type: ignore
                c.Link(components=[c.Text(text='Back')], on_click=GoToEvent(url="/web/")),
                c.Heading(text="Project not exists", level=2)
            ]
        )

    project = Project.model_validate(yaml.load(open(f"{projects_dir}/{name}/config.yaml", "r"), Loader=yaml.SafeLoader))
    entities = [DeletebleEntity(name=el) for el in project.entities] # pyright: ignore[reportCallIssue]

    table = c.Heading(text="So far, not one entity", level=2) if not entities else c.Table(
            data=entities,
            columns=[
                DisplayLookup(field="name"),
                DisplayLookup(field='delete', on_click=GoToEvent(url="$2api/$1/delete-entity/{name}".replace("$1", project.name).replace("$2", str(request.base_url))))
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


@router.get("/project/{name}/edit/dataset", response_model=FastUI, response_model_exclude_none=True, tags=["fast ui interface"])
def edit_dataset_page(name:str, request: Request):
    if not os.path.exists(f"{projects_dir}/{name}"):
        return c.Page(
            components=[ # type: ignore
                c.Heading(text="Project not exists", level=2)
            ]
        )
    project = Project.model_validate(yaml.load(open(f"{projects_dir}/{name}/config.yaml", "r"), Loader=yaml.SafeLoader))

    return template_edit_page(
        c.Heading(text="Add to dataset", level=2),
        c.Iframe(
            src=f"{request.base_url}add_to_dataset/{name}", # type: ignore
            width="100%",
            height=450
        ), 
        c.Paragraph(text=""),
        c.Heading(text="Add to dataset template", level=2),
        c.Iframe(
            src=f"{request.base_url}add_template_to_dataset/{name}", # type: ignore
            width="100%",
            height=800
        ), 
        c.Paragraph(text=""),
        c.Heading(text="Add to dataset with file", level=2),
        c.Form(
            submit_url=f"/api/update-dataset-file/{project.name}",
            form_fields=[
                c.FormFieldFile(name="dataset", title="Upload dataset", required=True, multiple=True, description="Uplad file in json format")
            ]
        ),
        c.Paragraph(text=""),
        c.Heading(text="Replace existing dataset with file", level=2),
        c.Form(
            submit_url=f"/api/replace-dataset-file/{project.name}",
            form_fields=[
                c.FormFieldFile(name="dataset", title="Upload dataset", required=True, multiple=False, description="Uplad file in json format")
            ]
        ),
        name=project.name
    )

