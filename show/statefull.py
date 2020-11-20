from dataclasses import dataclass

from . import Show, EpisodeSet

@dataclass
class StatefullShowWrapper:
    show: Show
    counter: int = 0

    def _increase_counter(self, increment_value: int = 1) -> None:
        self.counter += increment_value

    def next_episode(self) -> EpisodeSet:
        if self.counter >= len(self.show):
            raise Exception("No more video files in that show")
        self._increase_counter()
        return self.show[self.counter - 1]

    def set_counter(self, counter: int = 0) -> None:
        self.counter = counter

    def __getitem__(self, key: int) -> EpisodeSet:
        return self.show[key]

    def __len__(self) -> int:
        return len(self.show)
