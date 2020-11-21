import subprocess
from dataclasses import dataclass
from typing import Union
from show import EpisodeSet

@dataclass
class PlayStatus:
    return_code: int
    error: Union[Exception, None] = None

class Player:
    def __init__(self):
        self.run_string = "echo '{episode_set}'"

    def play(self, episode_set: EpisodeSet) -> PlayStatus:
        try:
            p = subprocess.run(self.run_string.format(episode_set=episode_set), shell=True)
            return PlayStatus(return_code=p.returncode)
        except Exception as e:
            return PlayStatus(return_code=p.returncode, error=e)