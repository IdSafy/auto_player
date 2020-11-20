from typing import Union
from pathlib import Path
from dataclasses import dataclass

from file_group import FilesGroup

MaybePath = Union[Path, None]
MaybeFilesGroup = Union[FilesGroup, None]

@dataclass
class EpisodeSet:
    video_file: Path
    audio_file: MaybePath = None
    subtitles_file: MaybePath = None

@dataclass
class Show:
    name: str
    video_group: FilesGroup
    audio_group: MaybeFilesGroup = None
    subtitles_group: MaybeFilesGroup = None

    def __getitem__(self, key: int) -> EpisodeSet:
        episode_set = EpisodeSet(
            video_file = self.video_group[key],
            audio_file = self.audio_group[key] if self.audio_group else None,
            subtitles_file = self.subtitles_group[key] if self.subtitles_group else None,
        )
        return episode_set

    def __len__(self) -> int:
        return len(self.video_group)
