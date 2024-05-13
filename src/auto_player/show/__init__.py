from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..file_group import FilesGroup

# class PShow(Protocol):
#     name: str
#     video_group: FilesGroup
#     audio_group: Optional[FilesGroup] = None
#     subtitles_group: Optional[FilesGroup] = None

#     def __getitem__(self, key: int) -> EpisodeSet:
#         episode_set = EpisodeSet(
#             video_file = self.video_group[key],
#             audio_file = self.audio_group[key] if self.audio_group else None,
#             subtitles_file = self.subtitles_group[key] if self.subtitles_group else None,
#         )
#         return episode_set

#     def __len__(self) -> int:
#         return len(self.video_group)


@dataclass
class EpisodeSet:
    video_file: Path
    audio_file: Optional[Path] = None
    subtitles_file: Optional[Path] = None

    @staticmethod
    def _fix_simlink_for_path(path: Path) -> Path:
        return path.resolve().relative_to(Path(".").resolve())

    def fix_simlinks(self) -> "EpisodeSet":
        return EpisodeSet(
            video_file=self._fix_simlink_for_path(self.video_file),
            audio_file=self._fix_simlink_for_path(self.audio_file)
            if self.audio_file
            else None,
            subtitles_file=self._fix_simlink_for_path(self.subtitles_file)
            if self.subtitles_file
            else None,
        )


@dataclass
class Show:
    name: str
    video_group: FilesGroup
    audio_group: Optional[FilesGroup] = None
    subtitles_group: Optional[FilesGroup] = None

    def __getitem__(self, key: int) -> EpisodeSet:
        episode_set = EpisodeSet(
            video_file=self.video_group[key],
            audio_file=self.audio_group[key] if self.audio_group else None,
            subtitles_file=self.subtitles_group[key] if self.subtitles_group else None,
        )
        return episode_set

    def __len__(self) -> int:
        return len(self.video_group)
