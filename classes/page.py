# file: classes/page.py

from typing import List, Optional, Tuple
from .button import Button  # or your new AsyncButton, if you rename the file
from .dial import Dial
from .led import Led

class Page:
    """
    A single "screen" or layout of Buttons, Dials, and LEDs.
    """
    def __init__(self, name: str, parent: Optional['Page'] = None):
        self.name = name
        self.parent = parent
        self.children: List[Page] = []
        self.buttons: List[List[Optional[Button]]] = [[], []]
        self.dials: List[Dial] = []
        self.leds: List[Led] = []

    def add_child(self, child_page: 'Page'):
        self.children.append(child_page)

    def display(self):
        print(f"Displaying page: {self.name}")

    async def handle_input_async(self, event: Tuple):
        """
        ASYNC version of handle_input.
        event can be: ("button_press", row, col), ("dial_press", idx), etc.
        """
        etype = event[0]
        if etype == "button_press":
            row = event[1]
            col = event[2]
            if 0 <= row < len(self.buttons) and 0 <= col < len(self.buttons[row]):
                btn = self.buttons[row][col]
                if btn is not None:
                    # We assume 'btn' is an AsyncButton with async .press()
                    await btn.press()

        elif etype == "dial_press":
            dial_idx = event[1]
            if 0 <= dial_idx < len(self.dials):
                await self.dials[dial_idx].press()

        elif etype == "dial_rotate":
            dial_idx = event[1]
            direction = event[2]
            steps = event[3]
            if 0 <= dial_idx < len(self.dials):
                await self.dials[dial_idx].on_rotate(direction, steps)

        elif etype == "led_swipe":
            direction = event[1]
            if self.leds:
                await self.leds[0].on_swipe(direction)

        elif etype == "led_tap":
            x = event[1]
            y = event[2]
            if self.leds:
                await self.leds[0].on_tap(x, y)



    def handle_input(self, event: Tuple):
        """
        event can be:
          ("button_press", row, col)
          ("dial_press", dial_idx)
          ("dial_rotate", dial_idx, direction, steps)
          ("led_swipe", direction)
          ("led_tap", x, y)
        """
        etype = event[0]
        if etype == "button_press":
            row = event[1]
            col = event[2]
            if 0 <= row < len(self.buttons) and 0 <= col < len(self.buttons[row]):
                btn = self.buttons[row][col]
                if btn is not None:
                    btn.press()

        elif etype == "dial_press":
            dial_idx = event[1]
            if 0 <= dial_idx < len(self.dials):
                self.dials[dial_idx].press()

        elif etype == "dial_rotate":
            dial_idx = event[1]
            direction = event[2]
            steps = event[3]
            if 0 <= dial_idx < len(self.dials):
                self.dials[dial_idx].on_rotate(direction, steps)

        elif etype == "led_swipe":
            direction = event[1]
            if self.leds:
                self.leds[0].on_swipe(direction)

        elif etype == "led_tap":
            x = event[1]
            y = event[2]
            if self.leds:
                self.leds[0].on_tap(x, y)
