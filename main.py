from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

from fastapi.staticfiles import StaticFiles
from fastui import prebuilt_html, AnyComponent
from fastui import components as c
import uvicorn

from src.api import router as api_router
from src.ui import web_router, fastui_router as fastui_web_router


c.Page.model_rebuild()
c.ModelForm.model_rebuild()
c.Form.model_rebuild()

app = FastAPI()
app.include_router(api_router, prefix="/api")
app.include_router(fastui_web_router, prefix="/api/web")
app.include_router(web_router)

app.mount("/static", StaticFiles(directory="www/static"), name="static")


@app.get("/", tags=["fast ui interface"])
def main_rout():
    return RedirectResponse(url="/web/")

@app.get('/web/{path:path}', tags=["fast ui interface"])
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title='classifier web'))


if __name__ == "__main__":
    uvicorn.run("main:app", port=8585, reload=True)
