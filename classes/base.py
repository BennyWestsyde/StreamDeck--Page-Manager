# file: classes/base.py
import asyncio
from typing import Optional, Callable, Dict, List, Any

from StreamDeck.Devices.StreamDeck import StreamDeck

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
    def __init__(self):
        self.states: List[ItemState] = []

    def add_state(self, image: Optional[str] = None, title: Optional[str] = None):
        self.states.append(ItemState(image, title))

class InteractableItem:
    """
    Base class for interactive elements that can cycle states
    and call an async callback when triggered.
    """
    def __init__(self,position: tuple[int,int],page, image: Optional[str] = None, title: Optional[str] = None):
        self.super = page
        self.position: tuple[int, int] = position
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
        logger.debug(f"Triggered: {self.title} | State: {self.current_state_index}")
        await self._cycle_states()
        if self._async_function:
            if self._async_function_input:
                await self._async_function(**self._async_function_input)
            else:
                await self._async_function()

    async def _cycle_states(self):
        logger.debug(f"Cycle states: {self.states}")
        if not self.states.states:
            return
        self.current_state_index = (self.current_state_index + 1) % len(self.states.states)
        await self.render()

    async def render(self):
        """
        This reuses your 'set_key_image' logic on a per-(row,col) basis.
        """
        if not self.states.states[self.current_state_index].image:
            return
        else:
            svg_path = self.states.states[self.current_state_index].image
        import os, io
        import cairosvg
        from PIL import Image, ImageChops
        row,col = self.position

        key_index = row * 4 + col
        if not os.path.exists(svg_path):
            print(f"[WARN] Missing icon: {svg_path}")
            return

        # Convert SVG -> PNG
        png_data = cairosvg.svg2png(url=svg_path)

        # Query size
        key_w, key_h = self.super.super.deck.key_image_format()["size"]
        with Image.open(io.BytesIO(png_data)).convert("RGBA") as icon:
            icon = icon.resize((key_w, key_h), Image.LANCZOS)

            # Do your partial invert logic
            r, g, b, alpha = icon.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb_inverted = ImageChops.invert(rgb)
            icon_inverted = Image.merge("RGBA", (*rgb_inverted.split(), alpha))

            final_img = Image.new("RGB", (key_w, key_h), color="black")
            final_img.paste(icon_inverted, mask=icon_inverted.split()[3])

            final_bytes = io.BytesIO()
            final_img.save(final_bytes, format="JPEG")
            if self.super is not None:
                self.super.super.deck.set_key_image(key_index, final_bytes.getvalue())

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