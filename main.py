import uvicorn as uvicorn
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

if __name__ == "__main__":
    uvicorn.run("main:application", port=8000, reload=True)
