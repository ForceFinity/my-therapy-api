from pydantic import BaseModel


# class DB(BaseSettings):
#     driver: str
#     user: str
#     password: str
#     host: str
#     port: int
#     database: str


class Config(BaseModel):
    title: str
    version: int
    build: int
    # db: DB


config = Config(
    title="MyTherapy",
    version=1,
    build=0
)
