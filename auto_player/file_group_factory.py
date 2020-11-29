import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Generic, TypeVar, Union

from file_group import FilesGroupType, FilesGroup
from file_group.RegexFileGroup import RegexFileGroup

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

def make_counter(**kwargs) -> Optional[int]:
    return kwargs.get("watched", None)