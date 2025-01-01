# file: classes/dial.py
from typing import Callable, Optional, Dict, Any
from .base import InteractableItem

class Dial(InteractableItem):
    """
    A dial that might be pressed or rotated.
    """
    def __init__(self, image=None, title=None):
        super().__init__(image=image, title=title)
        self._rotation_function: Optional[Callable[..., Any]] = None
        self._rotation_input: Optional[Dict] = None

    def set_rotation_function(self, func: Callable[..., Any], func_input: Optional[Dict] = None):
        self._rotation_function = func
        self._rotation_input = func_input

    async def press(self):
        # If pressing also cycles states:
        await self.on_trigger()

    async def on_rotate(self, direction: str, steps: int = 1):
        # If rotating should cycle states, do: await self.on_trigger()
        if self._rotation_function:
            if self._rotation_input:
                await self._rotation_function(direction=direction, steps=steps, **self._rotation_input)
            else:
                await self._rotation_function(direction=direction, steps=steps)
