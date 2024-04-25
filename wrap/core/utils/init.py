import importlib
import os
from pathlib import Path
from ssl import SSLContext

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from tortoise import BaseDBAsyncClient
from tortoise.contrib.fastapi import register_tortoise

from wrap.core import config, logger
from wrap.core.utils.google import conn_cloud_sql


def configure_db(app: FastAPI):
    """
    Generates a list of paths to the models, includes aerich, then registers Tortoise

    :param app: Instance of FastAPI class
    :return:
    """
    conn = conn_cloud_sql()

    models = [
        f'wrap.applications.{app_dir}.models'
        for app_dir in os.listdir(Path("wrap") / "applications")
        if not app_dir.startswith("_")
    ]
    logger.debug(f"Found models: {models}")

    register_tortoise(
        app,
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database": conn._params.database,
                        "host": conn._addr[0],
                        "password": conn._params.password,
                        "port": conn._addr[1],
                        "user": conn._params.user,
                        "ssl": conn._params.ssl,  # Here we pass in the SSL context
                        "direct_tls": True
                    }
                }
            },
            "apps": {
                "models": {
                    "models": models,
                    "default_connection": "default",
                }
            },
        },
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
        # "http://localhost:5173",
        # "http://localhost:3000",
        "*"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
