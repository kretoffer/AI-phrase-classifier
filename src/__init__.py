import os
from config import projects_dir

if not os.path.exists(projects_dir):
    os.makedirs(projects_dir)