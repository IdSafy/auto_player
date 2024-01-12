from enum import Enum
from pathlib import Path
from typing import Iterator


class FilesGroupType(Enum):
    VIDEO = 1
    AUDIO = 2
    SUBTITLES = 3


class FilesGroup:
    def __init__(self, group_type: FilesGroupType):
        self.group_type = group_type

    @property
    def directory(self) -> Path:
        raise Exception("Not implemeted")

    def __getitem__(self, key: int) -> Path:
        raise Exception("Not implemeted")

    def __iter__(self) -> Iterator[Path]:
        raise Exception("Not implemeted")

    def __len__(self) -> int:
        raise Exception("Not implemeted")
