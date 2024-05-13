import os
import subprocess
from dataclasses import dataclass
from typing import List, Union

from .show import EpisodeSet


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
    def __init__(
        self, environment_variable_name: str = DEFAULT_ENVIRONMENT_VARIABLE_NAME
    ):
        self.environment_variable_name = environment_variable_name

    def _get_player_string(self) -> str:
        player_string = os.environ.get(self.environment_variable_name, None)
        if player_string is None:
            raise Exception(
                f"Varialble '{self.environment_variable_name}' is undefined"
            )
        return player_string

    def play(self, episode_set: EpisodeSet) -> PlayStatus:
        try:
            player_string = self._get_player_string()
        except Exception as e:
            status = PlayStatus(failed=True, error=e)
            return status
        command = player_string.format(episode=episode_set)
        process = subprocess.run(command, shell=True)
        failed = process.returncode != 0
        status = PlayStatus(failed=failed, return_code=process.returncode)
        return status


class CunstuctorPlayer(Player):
    def __init__(
        self,
        base: List[str],
        video_file_wrapper: List[str],
        audio_file_wrapper: List[str],
        subtitles_file_wrapper: List[str],
        appendix: List[str] = list(),
    ):
        self.base = base
        self.video_file_wrapper = video_file_wrapper
        self.audio_file_wrapper = audio_file_wrapper
        self.subtitles_file_wrapper = subtitles_file_wrapper
        self.appendix = appendix

    def _construct_command(self, episode_set: EpisodeSet) -> List[str]:
        command = []

        def list_format(templates: list[str]) -> list[str]:
            return list(
                map(lambda x: x.format(episode=episode_set.fix_simlinks()), templates)
            )

        command += list_format(self.base)
        command += list_format(self.video_file_wrapper)
        if episode_set.audio_file is not None:
            command += list_format(self.audio_file_wrapper)
        if episode_set.subtitles_file is not None:
            command += list_format(self.subtitles_file_wrapper)
        command += list_format(self.appendix)
        return command

    def play(self, episode_set: EpisodeSet) -> PlayStatus:
        command = self._construct_command(episode_set)
        process = subprocess.run(command)
        failed = process.returncode != 0
        status = PlayStatus(failed=failed, return_code=process.returncode)
        return status
