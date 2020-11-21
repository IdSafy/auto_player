from state import State

class Backend:
    NAME = "undefined"

    def __init__(self, session: str):
        self.session = session

    def save(self, state: State) -> None:
        pass

    def load(self) -> State:
        pass

