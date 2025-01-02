# file: classes/button.py
from typing import List

from logger import logger
from .base import InteractableItem, ItemState, VisibleItem


class Button(VisibleItem):
    """
    A button that calls 'await on_trigger()' when pressed.
    """
    def __init__(self,position: tuple[int,int],page, itemstates: List[ItemState]):
        self.super = page
        super().__init__(position,page,itemstates)
        x,y = position
        page.buttons[x][y] = self

    async def press(self):
        await self.on_trigger()

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
        row, col = self.position

        key_index = row * 4 + col
        if not os.path.exists(svg_path):
            logger.error(f"[ERROR] Missing icon: {svg_path}")
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
