import joblib


def classificate(project_path: str, message: str):
    model = joblib.load(f"{project_path}/classifier")

    return model.predict([message])[0]
