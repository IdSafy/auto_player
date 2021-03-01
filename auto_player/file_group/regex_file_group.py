from typing import Pattern, Iterator
from pathlib import Path

from . import FilesGroup, FilesGroupType

class RegexFileGroup(FilesGroup):
    def __init__(self, group_type: FilesGroupType, directory: Path, regex = Pattern[str]):
        super().__init__(group_type=group_type)
        self._directory = directory
        self.regex = regex

    @property
    def directory(self) -> Path:
        return self._directory

    def __getitem__(self, key: int) -> Path:
        iterator = iter(self)
        for _ in range(key + 1):
            item = next(iterator)
        return item

    def __iter__(self) -> Iterator[Path]:
        files = self.directory.iterdir()
        return (x for x in files if x.is_file() and self.regex.match(x.name))

    def __len__(self) -> int:
        return len([*iter(self)])

    def __str__(self):
        return str([*iter(self)])
