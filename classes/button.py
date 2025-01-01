# file: classes/button.py
from .base import InteractableItem

class Button(InteractableItem):
    """
    A button that calls 'await on_trigger()' when pressed.
    """
    def __init__(self,position: tuple[int,int],page, image=None, title=None):
        self.super = page
        super().__init__(position,page,image=image, title=title)
        x,y = position
        page.buttons[x][y] = self

    async def press(self):
        await self.on_trigger()
