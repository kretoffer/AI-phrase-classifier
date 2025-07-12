from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

from fastui import prebuilt_html, AnyComponent
from fastui import components as c
import uvicorn

from src.api import router as api_router
from src.ui import router as web_router


c.Page.model_rebuild()
c.ModelForm.model_rebuild()
c.Form.model_rebuild()

app = FastAPI()
app.include_router(api_router, prefix="/api")
app.include_router(web_router, prefix="/api/web")


@app.get("/", tags=["fast ui interface"])
def main_rout():
    return RedirectResponse(url="/web/")

@app.get('/web/{path:path}', tags=["fast ui interface"])
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title='classifier web'))


if __name__ == "__main__":
    uvicorn.run("main:app", port=8585, reload=True)
