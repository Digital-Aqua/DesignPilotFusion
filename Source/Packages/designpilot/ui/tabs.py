from typing import Any

import rxprop as rx

from .base import ViewModel, empty_vm


class TabVm(ViewModel):
    def __init__(self,
        title: ViewModel,
        content: ViewModel,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.title = title
        self.content = content

    @rx.value
    def title(self) -> ViewModel:
        """ The title of the tab. """
        ...
    
    @rx.value
    def content(self) -> ViewModel:
        """ The content of the tab. """
        ...

empty_tab = TabVm(empty_vm, empty_vm)


class TabContainerVm(ViewModel):
    def __init__(self, tab: TabVm, *tabs: TabVm, **kwargs: Any):
        super().__init__(**kwargs)
        self.tabs = [tab, *tabs]

    @rx.value
    def tabs(self) -> list[TabVm]:
        ...

    @rx.value
    def selected_tab_index(self) -> int:
        return 0
    
    @rx.computed
    def selected_tab(self) -> TabVm:
        try:
            return self.tabs[self.selected_tab_index]
        except IndexError:
            return empty_tab
