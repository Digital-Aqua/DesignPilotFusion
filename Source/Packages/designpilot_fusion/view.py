from typing import Any

import rxprop as rx
from designpilot.ui import ViewModel
from designpilot_html import View


class FusionView(View):
    def __init__(self, root_vm: ViewModel):
        super().__init__(root_vm)

    async def run(self) -> None:
        changes = rx.watchp(self, FusionView.html)
        async for _ in changes:
            self.on_send(self.html)

    def on_send(self, html: str) -> None:
        # Send data to the page
        ...
    
    def on_receive(self, data: Any) -> None:
        # Handle data received from the page
        ...
