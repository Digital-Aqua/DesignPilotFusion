from rxprop import computed
from designpilot.ui import ViewModel

from .registry import default_registry


class View():
    def __init__(self, root_vm: ViewModel):
        self.root_vm = root_vm
    
    @computed
    def html(self) -> str:
        return ''.join(
            default_registry.render(self.root_vm)
        )
