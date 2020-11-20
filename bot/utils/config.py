import json
import os

default_config = {"prefix": ";", "token": "", "database": "postgresql://localhost/maki"}
DEFAULT_PREFIX = ";"


class Config:
    def __init__(self):
        # self.filename = filename
        # self.config = {}
        # if not os.path.isfile(filename):
        #     with open(filename, "w") as file:
        #         json.dump(default_config, file)
        # with open(filename) as file:
        #     self.config = json.load(file)
        self.prefix = os.getenv("PREFIX", DEFAULT_PREFIX)
        self.token = os.getenv("TOKEN")
        self.database = os.getenv("DB_DSN", "postgresql://postgres:postgres@localhost/postgres")
        self.owm_key = os.getenv("OWM_KEY")
        self.omdb_key = os.getenv("OMDB_KEY")
        # self.prefix = self.config.get("prefix", default_config.get("prefix"))
        # self.token = self.config.get("token", default_config.get("token"))
        # self.database = self.config.get("database", default_config.get("database"))
        # self.owm_key = self.config.get("owmKey")
        # self.omdb_key = self.config.get("omdbKey")