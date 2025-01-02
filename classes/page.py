# file: classes/page.py

from typing import List, Optional, Tuple, Any, Callable

from logger import logger
from .base import ItemState
from .button import Button
from .dial import Dial
from .led import Led
from .led_dial import LCDDial


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
        num_led_keys = self.super.deck.KEY_COLS
        # TODO: Add touchbuttons instead of/alongside LEDs
        self.leds: List[Led] = [None] * num_led_keys
        logger.debug(f"Created Page: {name} with {num_button_rows}x{num_button_cols} buttons, {num_dials} dials, and {num_led_keys} LEDs.")

    def create_child(self, name: str, icon: Optional[str], coordinates: tuple[int,int]) -> Optional['Page']:
        x,y = coordinates
        max_y, max_x = ((self.super.deck.KEY_COUNT // self.super.deck.KEY_ROWS), self.super.deck.KEY_ROWS)
        if x >= max_x or y >= max_y:
            logger.error("Your coordinates exceeds the screen's maximum possible size.")
            logger.error(f"({x},{y}) >= ({max_x},{max_y})")
            return None
        elif self.buttons[x][y] is not None:
            return None
        new_page = Page(self.super, name, self)
        self.children.append(new_page)
        back_button = Button((0,0),new_page, [ItemState("Icons/arrow-left-top.svg", self.name)])
        back_button.set_async_function(lambda: self.super.go_to_page(self))
        new_page.buttons[0][0] = back_button
        new_page_button = Button((x,y),self, [ItemState(icon,name)])
        new_page_button.set_async_function(lambda: self.super.go_to_page(new_page))
        return new_page

    def create_button(self, coordinates: Tuple[int, int], visible: List[ItemState], function: Callable[..., Any]):
        x, y = coordinates
        if self.buttons[x][y] is not None:
            logger.error("Button already exists at this location.")
            return
        new_button = Button(coordinates, self, visible)
        new_button.set_async_function(function)
        self.buttons[x][y] = new_button
        return new_button

    def create_dial(self, idx: int, visible: List[ItemState], function: Callable[..., Any]):
        if self.dials[idx] is not None:
            logger.error("Dial already exists at this location.")
            return
        new_dial = LCDDial(self.leds[0],idx,  visible)
        new_dial.set_rotation_function(func=function)
        # TODO:
        return new_dial

    def add_child(self, child_page: 'Page'):
        self.children.append(child_page)


    async def handle_input_async(self, event: Tuple):
        """
        ASYNC version of handle_input.
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
                    # We assume 'btn' is an AsyncButton with async .press()
                    logger.debug(f"Pressing button {row},{col}")
                    await btn.press()
                else:
                    logger.warning(f"No button at {row},{col}")
            else:
                logger.warning(f"Invalid button coordinates: {row},{col}")

        elif etype == "dial_press":
            dial_idx = event[1]
            if 0 <= dial_idx < len(self.dials):
                logger.debug(f"Pressing dial {dial_idx}")
                await self.dials[dial_idx].press()
            else:
                logger.warning(f"Invalid dial index: {dial_idx}")

        elif etype == "dial_rotate":
            dial_idx = event[1]
            direction = event[2]
            steps = event[3]
            if 0 <= dial_idx < len(self.dials):
                logger.debug(f"Rotating dial {dial_idx} {steps} steps {direction}")
                await self.dials[dial_idx].on_rotate(direction, steps)
            else:
                logger.warning(f"Invalid dial index: {dial_idx}")

        elif etype == "led_swipe":
            direction = event[1]
            if self.leds:
                logger.debug(f"Swiping LED {direction}")
                await self.leds[0].on_swipe(direction)
            else:
                logger.warning("No LEDs on this page.")

        elif etype == "led_tap":
            x = event[1]
            y = event[2]
            if self.leds:
                logger.debug(f"Tapping LED {x},{y}")
                await self.leds[0].on_tap(x, y)
            else:
                logger.warning("No LEDs on this page.")

