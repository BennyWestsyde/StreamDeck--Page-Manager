# file: classes/led.py
from typing import Callable, Optional, Dict, Any
from .base import InteractableItem

class Led(InteractableItem):
    """
    LED-based item for taps/swipes.
    """
    def __init__(self,position: tuple[int,int],page, image=None, title=None):
        self.super = page
        super().__init__(position,page,image=image, title=title)
        self.super.buttons[position] = self
        self._tap_function: Optional[Callable[..., Any]] = None
        self._tap_input: Optional[Dict] = None
        self._swipe_function: Optional[Callable[..., Any]] = None
        self._swipe_input: Optional[Dict] = None

    def set_tap_function(self, func: Callable[..., Any], func_input: Optional[Dict] = None):
        self._tap_function = func
        self._tap_input = func_input

    def set_swipe_function(self, func: Callable[..., Any], func_input: Optional[Dict] = None):
        self._swipe_function = func
        self._swipe_input = func_input

    async def on_tap(self, x=None, y=None):
        # If tapping triggers a state change:
        await self.on_trigger()

        # Then do the dedicated tap function
        if self._tap_function:
            if self._tap_input:
                await self._tap_function(x=x, y=y, **self._tap_input)
            else:
                await self._tap_function(x=x, y=y)

    async def on_swipe(self, direction: str):
        # Optionally cycle states on swipe
        # await self.on_trigger()

        if self._swipe_function:
            if self._swipe_input:
                await self._swipe_function(direction=direction, **self._swipe_input)
            else:
                await self._swipe_function(direction=direction)