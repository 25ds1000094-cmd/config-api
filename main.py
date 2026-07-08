from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


# Layer 1: defaults
DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


# Layer 2: config.development.yaml
YAML_CONFIG = {
    "port": 8522,
    "workers": 15,
    "debug": False,
    "log_level": "warning",
    "api_key": "key-zijl9ts246",
}


# Layer 3: .env
# NUM_WORKERS -> workers alias
DOTENV_CONFIG = {
    "workers": 9,
    "debug": True,
    "log_level": "error",
}


# Layer 4: OS environment variables
OS_ENV_CONFIG = {
    "port": 8768,
    "debug": False,
}


def cast_value(key, value):
    if key in ["port", "workers"]:
        return int(value)

    if key == "debug":
        return str(value).lower() in [
            "true",
            "1",
            "yes",
            "on"
        ]

    return str(value)


@app.get("/effective-config")
def effective_config(
    set: Optional[List[str]] = Query(default=None)
):

    config = {}

    # Low -> high precedence
    config.update(DEFAULTS)
    config.update(YAML_CONFIG)
    config.update(DOTENV_CONFIG)
    config.update(OS_ENV_CONFIG)

    # Highest precedence: CLI query params
    if set:
        for item in set:
            if "=" in item:
                key, value = item.split("=", 1)
                config[key] = value

    config["port"] = cast_value("port", config["port"])
    config["workers"] = cast_value("workers", config["workers"])
    config["debug"] = cast_value("debug", config["debug"])

    return {
        "port": config["port"],
        "workers": config["workers"],
        "debug": config["debug"],
        "log_level": config["log_level"],
        "api_key": "****"
    }
