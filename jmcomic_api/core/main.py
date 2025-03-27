from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from jmcomic_api._utils.env import dev_mode
from jmcomic_api._utils.exception import add_exception_handler

app = FastAPI(debug=dev_mode)

app = add_exception_handler(app=app)

async def root():
    return RedirectResponse(url="/docs")

app.add_api_route("/", root)
