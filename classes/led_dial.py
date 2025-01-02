# file: classes/lcd_dial.py
from typing import List, Callable, Tuple, Any

from logger import logger
from .base import ItemState
from .dial import Dial
from .led import Led

class LCDDial:
    """
    Combines a Dial with a 4x1 Led for interactive control and display.
    """
    def __init__(self, led , dial_index: int, page):
        # TODO: This thing is a mess. I need to rework it to make it so that
        # the led is its own thing and we are just adding on top of it
        # or maybe we should just make this function a part of the led class
        # idk, I need to think about it
        self.dial = Dial(dial_index, page, [])
        self.led = led
        self.current_led_screen = 0  # Default to the first screen
        self.dial.set_rotation_function(self.handle_rotation)

    def add_led_button(self, index: int, item_states: List[ItemState], tap_function: Callable[...,Any]):
        """
        Add a TouchButton to the LED managed by this LCDDial.
        :param index: The index (0-3) of the button within the LED.
        :param item_states: The states for the button.
        :param tap_function: The function to call when the button is tapped.
        """
        self.led.add_touch_button(
            index=index,
            item_states=item_states,
            tap_function=tap_function)

    async def handle_rotation(self, direction: str, step: int = 1):
        """
        Handles dial rotation and updates the associated LED screen.
        """
        if direction == "left":
            self.current_led_screen = max(0, self.current_led_screen - step)
        elif direction == "right":
            self.current_led_screen = min(len(self.led.touch_buttons) - 1, self.current_led_screen + step)
        logger.info(f"LCDDial {self.dial.position}: Changed to screen {self.current_led_screen}")
        await self.led.render()

    async def handle_tap(self, x=None, y=None):
        logger.info(f"Tapped on LCDDial {self.dial.position} at {x},{y}")
        # Handle tap logic specific to this LED screen
        await self.led.on_tap(x, y)

    async def handle_swipe(self, direction: str):
        logger.info(f"Swiped {direction} on LCDDial {self.dial.position}")
        # Handle swipe logic (e.g., cycling screens or invoking actions)
        await self.led.on_swipe(direction)

    async def render(self):
        await self.led.render()

    def set_rotation_function(self, func):
        # TODO: Implement
        pass
