import importlib
import os
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from wrap.core import config, logger

db = config.db
DB_URL = f"{db.driver}://{db.user}:{db.password}@{db.host}:{db.port}/{db.database}"


def configure_db(app: FastAPI):
    """
    Generates a list of paths to the models, includes aerich, then registers Tortoise

    :param app: Instance of FastAPI class
    :return:
    """
    models = [
        f'wrap.applications.{app_dir}.models'
        for app_dir in os.listdir(Path("wrap") / "applications")
        if not app_dir.startswith("_")
    ]
    logger.debug(f"Found models: {models}")

    register_tortoise(
        app,
        db_url=DB_URL,
        modules={'models': models},
        generate_schemas=True,
        add_exception_handlers=True,
    )
    logger.debug("Tortoise initialized and schemas generated")


def include_routers(app: FastAPI):
    """
    Routers must contain the variables **__tags__** and **__prefix__** \n
    If router's name starts with "_" it won't be included

    :param app: Instance of FastAPI class
    :return: None
    """
    for module_name in os.listdir(Path("wrap") / "routers"):
        if module_name.startswith("_") or not module_name.endswith(".py"):
            continue

        module = importlib.import_module(f"wrap.routers.{module_name.removesuffix('.py')}")

        app.include_router(
            module.router, tags=module.__tags__, prefix="/api" + module.__prefix__
        )


def configure_middlewares(app: FastAPI):
    origins = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
