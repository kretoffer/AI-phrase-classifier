import os


projects_dir = "AI-phrase-classifier-data"

projects_dir_without_system_dir = True


if projects_dir_without_system_dir:
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
    projects_dir = f"{parent_dir}/{projects_dir}"
else:
    projects_dir = os.path.abspath(projects_dir)