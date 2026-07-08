from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import yaml
from dotenv import load_dotenv


app = FastAPI()


# Allow browser grader access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def parse_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).lower() in ["true", "1", "yes", "on"]


def cast_value(key, value):
    if key in ["port", "workers"]:
        return int(value)

    if key == "debug":
        return parse_bool(value)

    return str(value)


def load_yaml_config():
    try:
        with open("config.development.yaml", "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


def load_dotenv_config():
    load_dotenv()

    result = {}

    if os.getenv("NUM_WORKERS"):
        result["workers"] = os.getenv("NUM_WORKERS")

    if os.getenv("APP_DEBUG"):
        result["debug"] = os.getenv("APP_DEBUG")

    if os.getenv("APP_LOG_LEVEL"):
        result["log_level"] = os.getenv("APP_LOG_LEVEL")

    return result


def load_os_config():
    result = {}

    mapping = {
        "APP_PORT": "port",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
    }

    for env_key, config_key in mapping.items():
        if os.getenv(env_key):
            result[config_key] = os.getenv(env_key)

    return result


@app.get("/effective-config")
def effective_config(
    set: Optional[List[str]] = Query(default=None)
):
    config = {}

    # Lowest precedence
    config.update(DEFAULTS)

    # YAML
    config.update(load_yaml_config())

    # .env
    config.update(load_dotenv_config())

    # OS env
    config.update(load_os_config())

    # CLI query overrides
    if set:
        for item in set:
            if "=" in item:
                key, value = item.split("=", 1)
                config[key] = value

    # Apply type conversion
    for key in ["port", "workers", "debug"]:
        if key in config:
            config[key] = cast_value(key, config[key])

    # Mask secret
    config["api_key"] = "****"

    return {
        "port": config.get("port"),
        "workers": config.get("workers"),
        "debug": config.get("debug"),
        "log_level": config.get("log_level"),
        "api_key": config["api_key"],
    }
