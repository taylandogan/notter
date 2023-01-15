from notter.notter import Notter
from notter.controller import NoteController


class NotterContext:
    def __init__(self, notter: Notter, controller: NoteController):
        self.notter = notter
        self.controller = controller
