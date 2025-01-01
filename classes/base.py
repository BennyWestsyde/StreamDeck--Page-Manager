# file: classes/base.py
import asyncio
from typing import Optional, Callable, Dict, List, Any

class ItemState:
    """
    Represents one visible/configurable state (image, title) of an InteractableItem.
    """
    def __init__(self, image: Optional[str] = None, title: Optional[str] = None):
        self.image = image
        self.title = title

class ItemStates:
    """
    Manages multiple states for a single InteractableItem.
    """
    def __init__(self):
        self.states: List[ItemState] = []

    def add_state(self, image: Optional[str] = None, title: Optional[str] = None):
        self.states.append(ItemState(image, title))

class InteractableItem:
    """
    Base class for interactive elements that can cycle states
    and call an async callback when triggered.
    """
    def __init__(self, image: Optional[str] = None, title: Optional[str] = None):
        self.states = ItemStates()
        # Add an initial state from the constructor args
        self.states.add_state(image, title)
        self.current_state_index = 0

        # An async function to call when the item is triggered
        self._async_function: Optional[Callable[..., Any]] = None
        self._async_function_input: Optional[Dict] = None

    def set_async_function(self, func: Callable[..., Any], func_input: Optional[Dict] = None):
        """
        Attach an async function that will be awaited inside on_trigger().
        If you only have a sync function, you can wrap it with asyncio.to_thread().
        """
        self._async_function = func
        self._async_function_input = func_input

    async def on_trigger(self):
        """
        This is called when the user interacts with this item (e.g., button press).
        1) Cycle states
        2) Await the assigned async function
        """
        self._cycle_states()
        if self._async_function:
            if self._async_function_input:
                await self._async_function(**self._async_function_input)
            else:
                await self._async_function()

    def _cycle_states(self):
        if not self.states.states:
            return
        self.current_state_index = (self.current_state_index + 1) % len(self.states.states)

    @property
    def image(self) -> Optional[str]:
        if not self.states.states:
            return None
        return self.states.states[self.current_state_index].image

    @image.setter
    def image(self, new_image: Optional[str]):
        if self.states.states:
            self.states.states[self.current_state_index].image = new_image

    @property
    def title(self) -> Optional[str]:
        if not self.states.states:
            return None
        return self.states.states[self.current_state_index].title

    @title.setter
    def title(self, new_title: Optional[str]):
        if self.states.states:
            self.states.states[self.current_state_index].title = new_title