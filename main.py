from ssl import SSLError

import uvicorn as uvicorn
from asyncpg import ConnectionDoesNotExistError
from fastapi import FastAPI

from wrap.core import config
from wrap.core.utils.init import configure_db, include_routers, configure_middlewares

application = FastAPI(
    title=config.title,
    version=f"{config.version}.{config.build}"
)

configure_db(application)
include_routers(application)
configure_middlewares(application)


@application.exception_handler(ConnectionDoesNotExistError)
async def my_exception_handler(request, exc: ConnectionDoesNotExistError):
    configure_db(application)


@application.exception_handler(SSLError)
async def my_exception_handler(request, exc: SSLError):
    configure_db(application)

if __name__ == "__main__":
    uvicorn.run("main:application", port=8000, reload=True)
