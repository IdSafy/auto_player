from dataclasses import dataclass, field
from typing import Union, List, Optional
from show.statefull import StatefullShowWrapper

@dataclass
class State:
    shows: List[StatefullShowWrapper] = field(default_factory=list)

    def get_show_by_number(self, number: int, correct_zero: bool = True) -> Optional[StatefullShowWrapper]:
        if correct_zero:
            number = number - 1
        show = self.shows[number] if number < len(self.shows) else None
        return show

    def get_show_by_name(self, name: str) -> Optional[StatefullShowWrapper]:
        show = next((show for show in self.shows if show.name == name), None)
        return show

    def is_empty(self) -> bool:
    	return len(self.shows) == 0
