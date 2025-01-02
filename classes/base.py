# file: classes/base.py
from typing import Optional, Callable, Dict, List, Any

from . import logger


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
    def __init__(self, states: Optional[List[ItemState]] = None):
        self.states: List[ItemState] = states or []


    def add_state(self, state: ItemState):
        self.states.append(state)

class InteractableItem:
    """
    Base class for interactive elements that can cycle states
    and call an async callback when triggered.
    """
    def __init__(self,position,page):
        self.super = page
        self.position = position
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

class VisibleItem(InteractableItem):
        """
        A base class for items with visible feedback and rendering capabilities.
        """

        def __init__(self, position, page, item_states: List[ItemState]):
            super().__init__(position, page)
            self.states = ItemStates()
            for state in item_states:
                self.states.add_state(state)


        async def on_trigger(self):
            """
            This is called when the user interacts with this item (e.g., button press).
            1) Cycle states
            2) Await the assigned async function
            """
            logger.debug(f"Triggered: {self.title} | State: {self.current_state_index}")
            await self._cycle_states()
            if self._async_function:
                if self._async_function_input:
                    await self._async_function(**self._async_function_input)
                else:
                    await self._async_function()

        async def _cycle_states(self):
            if not self.states.states or len(self.states.states) == 1:
                return
            logger.debug(f"Cycle states: {self.states}")
            self.current_state_index = (self.current_state_index + 1) % len(self.states.states)
            await self.render()

        def render(self):
            raise NotImplementedError("You must implement render() in your subclass.")

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