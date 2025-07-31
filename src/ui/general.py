import os

import yaml
from fastapi import APIRouter
from fastui import FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup
from fastui.events import GoToEvent, PageEvent

from config import projects_dir
from src.shemes import Project

router = APIRouter()


@router.get(
    "/",
    response_model=FastUI,
    response_model_exclude_none=True,
    tags=["fast ui interface"],
)
def main_web():
    projects = [
        f
        for f in os.listdir(projects_dir)
        if os.path.isdir(os.path.join(projects_dir, f))
    ]
    projects = [
        Project.model_validate(
            yaml.load(
                open(f"{projects_dir}/{el}/config.yaml", "r"), Loader=yaml.SafeLoader
            )
        )
        for el in projects
    ]

    table = (
        c.Table(
            data=projects,
            columns=[
                DisplayLookup(
                    field="name", on_click=GoToEvent(url="/web/project/{name}")
                ),
                DisplayLookup(field="status"),
            ],
        )
        if projects
        else c.Heading(text="So far, not one project", level=3)
    )

    return [
        c.Page(
            components=[  # type: ignore
                c.Heading(text="Projects", level=1),  # type: ignore
                table,
                c.Button(
                    text="New project", on_click=PageEvent(name="new-project-modal")
                ),
                c.Modal(
                    title="New project",
                    body=[
                        c.Form(
                            submit_url="/api/new-project",
                            form_fields=[
                                c.FormFieldInput(
                                    name="project-name",
                                    title="Name of new project",
                                    required=True,
                                )
                            ],
                        )  # type: ignore
                    ],
                    open_trigger=PageEvent(name="new-project-modal"),
                ),
            ]
        )
    ]


@router.get(
    "/project/{name}",
    response_model=FastUI,
    response_model_exclude_none=True,
    tags=["fast ui interface"],
)
def project_page(name: str):
    if not os.path.exists(f"{projects_dir}/{name}"):
        return c.Page(
            components=[  # type: ignore
                c.Heading(text="Project not exists", level=2)
            ]
        )
    project = Project.model_validate(
        yaml.load(
            open(f"{projects_dir}/{name}/config.yaml", "r"), Loader=yaml.SafeLoader
        )
    )

    return [
        c.Page(
            components=[  # type: ignore
                c.Heading(text=project.name, level=1),
                c.Link(
                    components=[c.Text(text="Back")], on_click=GoToEvent(url="/web/")
                ),
                c.Details(data=project),
                c.Button(
                    text="Edit",
                    on_click=GoToEvent(url=f"/web/project/{project.name}/edit"),
                ),
                c.Paragraph(text=" "),
                c.Button(
                    text="educate",
                    named_style="warning",
                    on_click=PageEvent(name="educate"),
                ),
                c.Form(
                    form_fields=[],
                    submit_url=f"/api/start_education/{name}",
                    footer=[],
                    method="GET",
                    submit_trigger=PageEvent(name="educate"),
                ),
            ]
        ),
    ]
