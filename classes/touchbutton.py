from typing import List, Callable, Optional, Dict, Any, Tuple
from .base import InteractableItem, ItemState, VisibleItem
from logger import logger


class TouchButton(VisibleItem):
    """
    Represents a segment of the LED that manages its state and interactions independently.
    """

    def __init__(self,led, position: Tuple[int, int], size: Tuple[int, int], page, item_states: List[ItemState]):
        """
        :param position: (x, y) position of the TouchButton within the LED.
        :param size: (width, height) of the TouchButton's interactive region.
        :param page: Parent page or container.
        :param item_states: States for the TouchButton.
        """
        self.led = led
        super().__init__(position, page, item_states)
        self.size = size
        self._tap_function: Optional[Callable[..., Any]] = None

    def set_tap_function(self, func: Callable[..., Any], func_input: Optional[Dict] = None):
        self._tap_function = func
        self._async_function_input = func_input

    async def on_tap(self, x=None, y=None):
        if x is not None and y is not None:
            local_x = x - self.position[0]
            local_y = y - self.position[1]
            logger.info(f"Tapped TouchButton at local coordinates ({local_x}, {local_y})")
        else:
            logger.info(f"Tapped TouchButton at {self.position} with size {self.size}")

        await self.on_trigger()
        if self._tap_function:
            if self._async_function_input:
                await self._tap_function(x=x, y=y, **self._async_function_input)
            else:
                await self._tap_function(x=x, y=y)

    async def render(self):
        """
        Renders this TouchButton into its section of the LED.
        """
        current_state_image_path = self.states.states[self.current_state_index].image
        if not current_state_image_path:
            return

        from PIL import Image
        import os

        if not os.path.exists(current_state_image_path):
            logger.error(f"Missing image for TouchButton: {current_state_image_path}")
            return

        button_image = Image.open(current_state_image_path).resize(self.size, Image.LANCZOS)
        self.led.image.paste(button_image, self.position)
