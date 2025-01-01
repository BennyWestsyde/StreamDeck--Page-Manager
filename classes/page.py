# file: classes/page.py

from typing import List, Optional, Tuple, Any

from .base import InteractableItem
from .button import Button
from .dial import Dial
from .led import Led
from StreamDeck.Devices.StreamDeck import StreamDeck



class Page:
    """
    A single "screen" or layout of Buttons, Dials, and LEDs.
    """
    def __init__(self, page_manager, name: str, parent: Optional['Page'] = None):
        self.super = page_manager
        self.name = name
        self.parent = parent
        self.children: List[Page] = []
        self.siblings: List[Page] = []
        num_button_rows: int = self.super.deck.KEY_ROWS
        num_button_cols: int = self.super.deck.KEY_COLS
        self.buttons: List[List[Optional[Button]]] = [[None] * num_button_cols for _ in range(num_button_rows)]
        num_dials = self.super.deck.DIAL_COUNT
        self.dials: List[Optional[Dial]] = [None] * num_dials
        num_led_keys = self.super.deck.TOUCH_KEY_COUNT
        self.leds: List[Led] = [None] * num_led_keys

    def create_child(self, name: str, icon: Optional[str], coordinates: tuple[int,int]) -> Optional['Page']:
        x,y = coordinates
        max_y, max_x = ((self.super.deck.KEY_COUNT // self.super.deck.KEY_ROWS), self.super.deck.KEY_ROWS)
        if x >= max_x or y >= max_y:
            print("Your coordinates exceeds the screen's maximum possible size.")
            print(x, ">=", self.super.deck.KEY_COLS, " or ", y, ">=", self.super.deck.KEY_ROWS)
            return None
        elif self.buttons[x][y] is not None:
            return None
        new_page = Page(self.super, name, self)
        self.children.append(new_page)
        back_button = Button((0,0),new_page, "Icons/arrow-left-top.svg", self.name)
        back_button.set_async_function(lambda: self.super.go_to_page(self))
        new_page.buttons[0][0] = back_button
        new_page_button = Button((x,y),self, icon,name)
        new_page_button.set_async_function(lambda: self.super.go_to_page(new_page))
        return new_page

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
