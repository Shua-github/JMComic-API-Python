from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from jmcomic_api._utils.env import dev_mode

app = FastAPI(debug=dev_mode)

async def root():
    return RedirectResponse(url="/docs")

app.add_api_route("/", root)