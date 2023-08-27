from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from ecom_API import api as newapiRoute
from ecom_API import routes as apiRoute
from ecom_admin import routes as adminRoute
from fastapi.staticfiles import StaticFiles
from configs.connection import DATABASE_URL
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
import os

db_url = DATABASE_URL()

middleware = [
    Middleware(SessionMiddleware, secret_key='super-secret')
]
app = FastAPI(middleware=middleware)


app.include_router(newapiRoute.router, prefix="/ecom_API", tags=["ecom_API"]),
app.include_router(apiRoute.router,),

app.include_router(adminRoute.router,),

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")
app.mount("/static", StaticFiles(directory="static"), name="static"),


register_tortoise(
    app,
    db_url=db_url,
    modules={'models': ['ecom_API.models',
                        'aerich.models', 'ecom_admin.models']},
    generate_schemas=True,
    add_exception_handlers=True
)