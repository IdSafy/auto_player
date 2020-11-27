import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from file_group import FilesGroupType, FilesGroup
from file_group.RegexFileGroup import RegexFileGroup
from show import Show
from show.statefull import StatefullShowWrapper
from backend import Backend
from player import Player

FILE_GROUP_TYPES_PREFIXES = {
    FilesGroupType.VIDEO: "video_",
    FilesGroupType.AUDIO: "audio_",
    FilesGroupType.SUBTITLES: "subtitles_",
}

class FileGroupFactory:
    @property
    def mandatory_options(self) -> List[str]:
        return ["group_type"]

    def create(self, options: Dict[str, Any]) -> FilesGroup:
        ...

class RegexFileGroupFactory(FileGroupFactory):
    @property
    def mandatory_options(self) -> List[str]:
        return super().mandatory_options + ["regex", "dir"]

    def create(self, options: Dict[str, Any]) -> RegexFileGroup:
        group_type = options["group_type"]
        directory = Path(options["dir"])
        regex = re.compile(options["regex"])

        regex_file_group = RegexFileGroup(
            group_type=group_type,
            directory=directory,
            regex=regex,
        )
        return regex_file_group

FILES_GROUPS_FACTORIES: List[FileGroupFactory] = [
    RegexFileGroupFactory(),
]

def try_files_factories(options: Dict[str, Any]) -> Optional[FilesGroup]:
    for factory in FILES_GROUPS_FACTORIES:
        mandatory_options = factory.mandatory_options
        fit = set(mandatory_options).issubset(set(options.keys()))
        if fit:
            files_group = factory.create(options)
            return files_group
    return None

def filter_options(option: Dict[str, Any], files_type: FilesGroupType) -> Dict[str, Any]:
    prefix = FILE_GROUP_TYPES_PREFIXES[files_type]
    prefix_len = len(prefix)
    filtered_options = dict((key[prefix_len:], value)
        for key, value in option.items()
        if key.startswith(prefix))
    return filtered_options

def make_files_group(group_type: FilesGroupType, **kwargs) -> Optional[FilesGroup]:
    video_options = filter_options(kwargs, group_type)
    video_options["group_type"] = group_type
    video_group = try_files_factories(video_options)
    return video_group

class AutoPlayer:
    def __init__(self, backend: Backend, player: Player):
        self.backend = backend
        self.player = player
        self.state = backend.load()

    def play(self, name_or_number: str, episode_number: int = -1, correct_zero: bool = True) -> None:
        if correct_zero:
            corrected_episode_number = episode_number - 1
        show = self.get_show(name_or_number)
        if show is None:
            raise Exception("Unknown show")
        episode_set = show.next_episode() if episode_number == -1 else show[corrected_episode_number]
        status = self.player.play(episode_set)
        if not status.failed:
            self.backend.save(self.state)
        else:
            if status.error is not None:
                raise status.error
            else:
                raise Exception("Failed to play episode")

    def list_shows(self) -> List[StatefullShowWrapper]:
        return self.state.shows

    def get_show(self, name_or_number: str) -> Optional[StatefullShowWrapper]:
        try:
            number = int(name_or_number)
        except Exception as e:
            number = -1
        if number > 0:
            return self.state.get_show_by_number(number)
        name = name_or_number
        return self.state.get_show_by_name(name)

    def add_show(self, name: str, test: bool = False, **kwargs) -> StatefullShowWrapper:

        video_group = make_files_group(group_type=FilesGroupType.VIDEO, **kwargs)
        audio_group = make_files_group(group_type=FilesGroupType.AUDIO, **kwargs)
        subtitles_group = make_files_group(group_type=FilesGroupType.SUBTITLES, **kwargs)
        if video_group is None:
            raise Exception("Please specify video files")
        show = Show(name=name, video_group=video_group, audio_group=audio_group, subtitles_group=subtitles_group)

        counter = kwargs["watched"]
        statefull_show = StatefullShowWrapper(show=show, counter=counter)

        if not test:
            self.state.shows.append(statefull_show)
            self.backend.save(self.state)
        return statefull_show

    def modify_show(self, name_or_number: str, **kwargs) -> None:
        pass

    def delete_show(self, name_or_number: str) -> None:
        show = self.get_show(name_or_number)
        if show is None:
            raise Exception("Unknown show")
        self.state.shows.remove(show)
        self.backend.save(self.state)

    def get_show_info(self, name_or_number: str) -> Dict[str, Any]:
        pass
