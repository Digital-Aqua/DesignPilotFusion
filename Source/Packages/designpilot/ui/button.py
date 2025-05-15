from ..rx.base import ViewModel



class ButtonVM(ViewModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content = Rx("")

    def click(self):
        print("Button clicked")



