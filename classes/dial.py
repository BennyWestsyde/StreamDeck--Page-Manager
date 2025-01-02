# file: classes/dial.py
import asyncio
from typing import Callable, Optional, Dict, Any, List

from logger import logger
from .base import InteractableItem, ItemState


class Dial(InteractableItem):
    """
    A dial that might be pressed or rotated.
    """
    def __init__(self,position: int,page, itemstates: List[ItemState]):
        self.super = page
        super().__init__(position,page, itemstates)
        self.current_state_index += 1
        self.super.buttons[position] = self
        self._rotation_function: Optional[Callable[..., Any]] = None
        self._rotation_input: Optional[Dict] = None

    def set_rotation_function(self, func: Callable[..., Any], func_input: Optional[Dict] = None):
        self._rotation_function = func
        self._rotation_input = func_input

    async def press(self):
        # If pressing also cycles states:
        await self.on_trigger()

    async def render(self):
        logger.debug(f"Rendering dial {self.position} with state {self.current_state_index}")
        pass

    async def on_rotate(self, direction: str, step: int = 5):
        # If rotating should cycle states, do: await self.on_trigger()
        if direction == "left":
            self.current_state_index -= 1
            await self.render()
            self.current_state_index += 1
        elif direction == "right":
            self.current_state_index += 1
            await self.render()
            self.current_state_index -= 1

        if self._rotation_function:
            if self._rotation_input:
                await self._rotation_function(direction=direction, step=step*5, **self._rotation_input)
            else:
                await self._rotation_function(direction=direction, step=step*5)


    async def _cycle_states(self):
        await self.render()
        await asyncio.sleep(0.5)
        self.current_state_index += 1
        await self.render()