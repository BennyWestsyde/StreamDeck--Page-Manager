# file: classes/led.py
import io
from typing import Callable, Optional, Dict, Any, List, Tuple

from PIL import Image

from logger import logger
from .base import InteractableItem, ItemState, VisibleItem
from .touchbutton import TouchButton


class Led(VisibleItem):
    """
    Represents the LED screen as a 4x1 grid with dynamic TouchButton regions.
    """
    def __init__(self, page, dimensions: Tuple[int, int]):
        self._swipe_input = None
        self._swipe_function = None
        self.super = page
        super().__init__((0, 0), page, [])
        self.dimensions = dimensions
        self.image = Image.new("RGBA", self.dimensions, "black")  # Create a blank LED image
        self.touch_buttons: List[Optional[TouchButton]] = [None] * 4  # 4x1 grid

    def add_touch_button(self, index: int, item_states: List[ItemState], tap_function: Callable[..., Any]):
        """
        Add a TouchButton to a specific region of the LED.
        :param index: The index (0-3) of the button within the 4x1 grid.
        :param item_states: The states of the TouchButton.
        :param tap_function: The function to call when the button is tapped.
        """
        if not (0 <= index < len(self.touch_buttons)):
            logger.error(f"Index {index} out of bounds for LED touch buttons.")
            return
        if self.touch_buttons[index] is not None:
            logger.error(f"TouchButton already exists at index {index}")
            return

        # Calculate position of the TouchButton within the LED
        button_width = self.dimensions[0] // 4
        button_position = (index * button_width, 0)

        button = TouchButton(position=button_position, size=(button_width, self.dimensions[1]), page=self.super, item_states=item_states)
        button.set_tap_function(tap_function)
        self.touch_buttons[index] = button

    async def render(self):
        """
        Combine all TouchButton images into the LED display.
        """
        from PIL import Image

        led_image = Image.new("RGBA", self.dimensions, "black")
        for idx, button in enumerate(self.touch_buttons):
            if button:
                await button.render()

        # Render the final image to the LED
        led_image_bytes = io.BytesIO()
        led_image.save(led_image_bytes, format="JPEG")
        self.super.super.deck.set_led_image(led_image_bytes.getvalue())

    async def on_tap(self, x=None, y=None):
        """
        Determine which button was tapped and delegate the tap event.
        """
        if x is None:
            logger.error("Tap event missing x-coordinate")
            return

        # Determine which button in the 4x1 grid was tapped
        button_width = self.dimensions[0] // 4
        button_index = x // button_width

        if 0 <= button_index < len(self.touch_buttons):
            button = self.touch_buttons[button_index]
            if button:
                await button.on_tap()
            else:
                logger.warning(f"No button defined at index {button_index}")

    def set_swipe_function(self, func: Callable[..., Any], func_input: Optional[Dict] = None):
        self._swipe_function = func
        self._swipe_input = func_input

    async def on_swipe(self, direction: str):
        # Optionally cycle states on swipe
        # await self.on_trigger()

        if self._swipe_function:
            if self._swipe_input:
                await self._swipe_function(direction=direction, **self._swipe_input)
            else:
                await self._swipe_function(direction=direction)