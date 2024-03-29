import os
from pathlib import Path
from pprint import pprint

from ..authentication import PlexAuthentication
from ..logging import setup_logger
from ..plex_data import PlexData
from ..redis_db import RedisPlexDB

logger = setup_logger()
setup_logger(level="INFO")

media_conveyor_root = Path.home() / ".media_conveyor"
project_root = Path(__file__).resolve().parent.parent.parent.parent
os.environ["MEDIA_CONVEYOR"] = str(project_root / "tests/.media_conveyor")
print(os.getenv("MEDIA_CONVEYOR"))


def main():
    plex_auth = PlexAuthentication()
    plex_data = PlexData(plex_auth.baseurl, plex_auth.token)
    plex_db = plex_data.compile_libraries(movies=True, db_slice=slice(100, 105))
    pprint(plex_db)


def ping():
    redis_client = RedisPlexDB()
    redis_client.ping()


def write():
    plex_auth = PlexAuthentication()
    plex_data = PlexData(plex_auth.baseurl, plex_auth.token)
    plex_db = plex_data.compile_libraries(movies=True, db_slice=slice(100, 105))
    redis_client = RedisPlexDB(plex_db=plex_db)
    redis_client.make_db()


def read():
    redis_client = RedisPlexDB()
    keys = redis_client.keys()
    for key in keys:
        print(f"Key: {key}")
        print(f"Type: {type(key)}")
        print(redis_client.hgetall(key))
