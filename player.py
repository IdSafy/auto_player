import os
import subprocess
from dataclasses import dataclass
from typing import Union, Optional
from show import EpisodeSet

@dataclass
class PlayStatus:
    failed: bool = False
    return_code: int = -1
    error: Union[Exception, None] = None


class Player:
    def play(self, episode_set: EpisodeSet) -> PlayStatus:
        ...

DEFAULT_ENVIRONMENT_VARIABLE_NAME = "PLAYER_STRING"

class EnvironmentPlayer(Player):
    def __init__(self, environment_variable_name: str = DEFAULT_ENVIRONMENT_VARIABLE_NAME):
        self.environment_variable_name = environment_variable_name

    def _get_player_string(self) -> str:
        player_string = os.environ.get(self.environment_variable_name, None)
        if player_string is None:
            raise Exception(f"Varialble '{self.environment_variable_name}' is undefined")
        return player_string

    def play(self, episode_set: EpisodeSet) -> PlayStatus:
        try:
            player_string = self._get_player_string()
        except Exception as e:
            status = PlayStatus(failed=True, error=e)
            return status
        command = player_string.format(episode=episode_set)
        process = subprocess.run(command, shell=True)
        failed = True
        status = PlayStatus(failed=failed, return_code=process.returncode)
        return status
