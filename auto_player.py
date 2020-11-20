import re
from typing import Union, Pattern, Iterator
from enum import Enum
from pathlib import Path
from dataclasses import dataclass

from file_group import FilesGroupType
from file_group.RegexFileGroup import RegexFileGroup
from show import Show, EpisodeSet
from show.statefull import StatefullShowWrapper

class Player:
    def play(self, episode_set: EpisodeSet) -> None:
        raise Exception("Not implemeted")

def regex_show_factory(
        name: str,
        video_directory: str,
        video_regex: str,
        audio_directory: Union[str, None] = None,
        audio_regex: Union[str, None] = None,
        subtitles_directory: Union[str, None] = None,
        subtitles_regex: Union[str, None] = None
    ) -> StatefullShowWrapper:
    video_group = RegexFileGroup(
        group_type=FilesGroupType.VIDEO,
        directory=Path(video_directory),
        regex=re.compile(video_regex)
    )
    audio_group = None
    if audio_regex is not None:
        audio_directory = audio_directory if audio_directory is not None else video_directory
        audio_group = RegexFileGroup(
            group_type=FilesGroupType.AUDIO,
            directory=Path(audio_directory),
            regex=re.compile(audio_regex)
        )
    subtitles_group = None
    if subtitles_regex is not None:
        subtitles_directory = subtitles_directory if subtitles_directory is not None else video_directory
        subtitles_group = RegexFileGroup(
            group_type=FilesGroupType.SUBTITLES,
            directory=Path(subtitles_directory),
            regex=re.compile(subtitles_regex)
        )
    sf_show = StatefullShowWrapper(Show(name=name, video_group=video_group, audio_group=audio_group, subtitles_group=subtitles_group))
    return sf_show

def main():
    pass

if __name__ == "__main__":
    main()
