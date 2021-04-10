from collections import OrderedDict
from typing import List, Dict, Any, Optional, TypeVar, Union
from dataclasses import dataclass

from ..file_group import FilesGroupType, FilesGroup
from ..show import Show
from ..show.statefull import StatefullShowWrapper
from ..backend import Backend
from ..player import Player
from .file_group_factory import make_files_group, make_counter

T = TypeVar('T')

@dataclass
class Error:
    msg: Optional[str] = None

Rezult = Union[Error, T]

@dataclass
class ShowCommandWrapper:
    show: StatefullShowWrapper
    app: 'AutoPlayer'

    def play(self, episode_number: int = -1, correct_zero: bool = True) -> Rezult[None]:
        return self.app.play(show=self.show, episode_number=episode_number, correct_zero=correct_zero)

    def info(self) -> Rezult[Dict[str, Any]]:
        info = OrderedDict()
        info["name"] = self.show.name
        info["length"] = len(self.show)
        info["watched"] = self.show.counter
        directory = self.show.video_group.directory
        def files_group_info(files_group: Optional[FilesGroup]) -> Dict[str, Any]:
            group_info: Dict[str, Any] = OrderedDict()
            if files_group is None:
                return group_info
            group_info["class"] = type(files_group)
            group_info["files"] = []
            for path in files_group:
                relative_path = path.relative_to(directory)
                file_info = OrderedDict()
                file_info["path"] = str(path)
                file_info["relative_path"] = str(relative_path)
                group_info["files"].append(file_info)
            return group_info
        info["video_group"] = files_group_info(self.show.video_group)
        info["audio_group"] = files_group_info(self.show.audio_group)
        info["subtitles_group"] = files_group_info(self.show.subtitles_group)
        return info

    def delete(self) -> Rezult[None]:
        return self.app.delete_show(show=self.show)

    def edit(self, test: bool = False, **kwargs) -> Rezult[None]:
        video_group = make_files_group(group_type=FilesGroupType.VIDEO, **kwargs)
        audio_group = make_files_group(group_type=FilesGroupType.AUDIO, **kwargs)
        subtitles_group = make_files_group(group_type=FilesGroupType.SUBTITLES, **kwargs)
        counter = make_counter(**kwargs)

        if video_group is not None:
            self.show.show.video_group = video_group
        if audio_group is not None:
            self.show.show.audio_group = audio_group
        if subtitles_group is not None:
            self.show.show.subtitles_group = subtitles_group
        if counter is not None:
            self.show.counter = counter

        if not test:
            self.app.save_state()

        return None

class AutoPlayer:
    def __init__(self, backend: Backend, player: Player):
        self.backend = backend
        self.player = player
        self.state = backend.load()

    def play(self, show: StatefullShowWrapper, episode_number: int = -1, correct_zero: bool = True) -> Rezult[None]:
        if correct_zero:
            corrected_episode_number = episode_number - 1
        try:
            episode_set = show.next_episode() if episode_number == -1 else show[corrected_episode_number]
        except Exception as e:
            return Error(str(e))
        status = self.player.play(episode_set)
        if not status.failed:
            self.save_state()
            return None
        if status.error is not None:
            return Error(str(status.error))
        return Error("Failed to play episode")

    def list_shows(self) -> List[StatefullShowWrapper]:
        return self.state.shows

    def get_show(self, name_or_number: str) -> Rezult[ShowCommandWrapper]:
        try:
            number = int(name_or_number)
        except Exception as e:
            number = -1
        if number > 0:
            show = self.state.get_show_by_number(number)
        else:
            name = name_or_number
            show = self.state.get_show_by_name(name)
        if show is None:
            return Error("No such show")
        show_wrapper = ShowCommandWrapper(app=self, show=show)
        return show_wrapper

    def add_show(self, name: str, test: bool = False, **kwargs) -> Rezult[ShowCommandWrapper]:
        video_group = make_files_group(group_type=FilesGroupType.VIDEO, **kwargs)
        audio_group = make_files_group(group_type=FilesGroupType.AUDIO, **kwargs)
        subtitles_group = make_files_group(group_type=FilesGroupType.SUBTITLES, **kwargs)
        counter = make_counter(**kwargs)

        if video_group is None:
            return Error("Video files not specified")
        if counter is None:
            counter = 0
   
        show = Show(name=name, video_group=video_group, audio_group=audio_group, subtitles_group=subtitles_group)
        statefull_show = StatefullShowWrapper(show=show, counter=counter)

        if not test:
            self.state.shows.append(statefull_show)
            self.backend.save(self.state)
        show_wrapper = ShowCommandWrapper(app=self, show=statefull_show)
        return show_wrapper

    def delete_show(self, show: StatefullShowWrapper) -> Rezult[None]:
        self.state.shows.remove(show)
        self.backend.save(self.state)
        return None

    def save_state(self) -> None:
        self.backend.save(self.state)
