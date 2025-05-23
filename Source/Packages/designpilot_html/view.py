from rxprop import computed
from designpilot.ui import ViewModel

from .html_elements import render_html


class View():
    def __init__(self, root_vm: ViewModel):
        self.root_vm = root_vm
    
    @computed
    def html(self) -> str:
        return render_html(self.root_vm).getvalue()
