import os
import pickle
from . import Backend
from state import State

class LocalfileBackend(Backend):
    NAME = "localfile"

    def __init__(self, session: str):
        super().__init__(session)

    def _get_filename(self) -> str:
        directory = os.getcwd()
        filename = f"{directory}//.autoplayer_{self.session}"
        return filename

    def save(self, state: State) -> None:
        filename = self._get_filename()
        with open(filename, "wb") as file:
            pickle.dump(state, file)

    def load(self) -> State:
        filename = self._get_filename()
        if not os.path.exists(filename):
            return State()
        with open(filename, "rb") as file:
            state = pickle.load(file)
        return state