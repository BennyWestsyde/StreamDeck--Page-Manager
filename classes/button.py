# file: classes/button.py
from .base import InteractableItem

class Button(InteractableItem):
    """
    A button that calls 'await on_trigger()' when pressed.
    """
    def __init__(self, image=None, title=None):
        super().__init__(image=image, title=title)

    async def press(self):
        await self.on_trigger()
