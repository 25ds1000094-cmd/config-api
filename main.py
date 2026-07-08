from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import yaml
from typing import Optional, List


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def to_bool(v):
    return str(v).lower() in ["true", "1", "yes", "on"]


def cast(key, value):
    if key in ["port", "workers"]:
        return int(value)

    if key == "debug":
        return to_bool(value)

    return str(value)


def get_yaml():
    try:
        with open("config.development.yaml") as f:
            return yaml.safe_load(f) or {}
    except:
        return {}


def get_dotenv():
    load_dotenv(override=True)

    result = {}

    if os.getenv("NUM_WORKERS"):
        result["workers"] = os.getenv("NUM_WORKERS")

    if os.getenv("APP_DEBUG"):
        result["debug"] = os.getenv("APP_DEBUG")

    if os.getenv("APP_LOG_LEVEL"):
        result["log_level"] = os.getenv("APP_LOG_LEVEL")

    return result


def get_os_env():
    result = {}

    mapping = {
        "APP_PORT": "port",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
    }

    for env_name, key in mapping.items():
        if env_name in os.environ:
            result[key] = os.environ[env_name]

    return result


@app.get("/effective-config")
def effective_config(
    set: Optional[List[str]] = Query(None)
):

    config = {}

    # Lowest → highest precedence
    config.update(DEFAULTS)
    config.update(get_yaml())
    config.update(get_dotenv())
    config.update(get_os_env())

    # CLI overrides everything
    if set:
        for item in set:
            if "=" in item:
                key, value = item.split("=", 1)
                config[key] = value

    for key in ["port", "workers", "debug"]:
        config[key] = cast(key, config[key])

    config["api_key"] = "****"

    return {
        "port": config["port"],
        "workers": config["workers"],
        "debug": config["debug"],
        "log_level": config["log_level"],
        "api_key": config["api_key"],
    }
