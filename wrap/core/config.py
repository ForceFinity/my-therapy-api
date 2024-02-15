from pydantic import BaseModel
from pydantic_settings import BaseSettings


class DB(BaseSettings):
    driver: str
    user: str
    password: str
    host: str
    port: int
    database: str


class Config(BaseModel):
    title: str
    version: int
    build: int
    db: DB


config = Config(
    title="MyTherapy",
    version=1,
    build=0,
    db=DB().dict()
)
