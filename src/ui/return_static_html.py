def get_static_html(name: str):
    with open(f"www/static/{name}.html", "r", encoding="utf-8") as f:
        content = f.read()
    return content
