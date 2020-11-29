import os
import json
import importlib
from pathlib import Path
from typing import Dict, Any

from .base import AutoPlayer, Error, Rezult
from ..backend import Backend
from ..player import Player

DEFAULT_CONFIG_PATH = f"{Path.home()}/.autoplayer"

DEFAULT_CONFIG = {
    "backend": {
        "class": "backend.localfile.LocalfileBackend",
        "params": {},
    },
    # "player": {
    #     "class": "player.CunstuctorPlayer",
    #     "params": {
    #         "base": ["echo"],
    #         "video_file_wrapper": ["{episode.video_file}"],
    #         "audio_file_wrapper": ["{episode.audio_file}"],
    #         "subtitles_file_wrapper": ["{episode.subtitles_file}"],
    #         "appendix": [],
    #     },
    # },
}

def read_config(config_path: str) -> Dict[str, Any]:
    if not os.path.exists(config_path):
        raise Exception("No config file exist. Please create it first")
    with open(config_path, "r") as file:
        user_config = json.load(file)
    config = DEFAULT_CONFIG.copy()
    config.update(user_config)
    return config

def get_class(class_path: str) -> type:
    class_name = class_path.split(".")[-1]
    class_module = ".".join(class_path.split(".")[:-1])
    module = importlib.import_module(class_module)
    class_object = getattr(module, class_name)
    return class_object
    
def create_backend(config: Dict[str, Any], session: str) -> Backend:
    backend_config = config["backend"]
    class_path = backend_config["class"]
    params = backend_config["params"]
    backend = get_class(class_path)(session=session, **params)
    if isinstance(backend, Backend):
        return backend
    raise Exception("Provided backend class is not a Backend")

def create_player(config: Dict[str, Any]) -> Player:
    backend_config = config["player"]
    class_path = backend_config["class"]
    params = backend_config["params"]
    player = get_class(class_path)(**params)
    if isinstance(player, Player):
        return player
    raise Exception("Provided player class is not a Player")

def create_auto_player(config_path: str = DEFAULT_CONFIG_PATH, session: str = "default") -> AutoPlayer:
    config = read_config(config_path)
    backend = create_backend(config, session)
    player = create_player(config)
    return AutoPlayer(backend, player)
