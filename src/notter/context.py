from notter.controller import NoteController
from notter.notter import Notter


class NotterContext:
    def __init__(self, notter: Notter, controller: NoteController):
        self.notter = notter
        self.controller = controller
