# file: classes/page_manager.py
from typing import Optional, Tuple
from .page import Page

class PageManager:
    """
    Tracks the active Page. Forwards events to the current page.
    Also stores a reference to the 'deck' so we can re-render icons on page switch.
    """
    def __init__(self):
        self.current_page: Optional[Page] = None
        self.deck = None  # We'll set this later with set_deck()

    def set_deck(self, deck):
        self.deck = deck

    def set_current_page(self, page: Page):
        self.current_page = page
        # Instead of just printing, we call a new method that updates the device icons
        self.render_page(page)

    def go_to_page(self, page: Page):
        self.set_current_page(page)

    def go_back(self):
        if self.current_page and self.current_page.parent:
            self.set_current_page(self.current_page.parent)

    async def handle_event(self, event: Tuple):
        if self.current_page is not None:
            await self.current_page.handle_input_async(event)

    def render_page(self, page: Page):
        """Clear all keys, then set icons only for the new page's buttons."""
        if not self.deck:
            # If we have no deck, we can't render. Just do a fallback print.
            print(f"Displaying page: {page.name} (no deck connected)")
            return

        # 1) Clear all keys (in a 4x2 device, that's 8 keys).
        #    We'll set a plain black image on each key.
        key_w, key_h = self.deck.key_image_format()["size"]
        # Create a minimal black image for clearing
        from PIL import Image
        import io

        blank_img = Image.new("RGB", (key_w, key_h), "black")
        blank_bytes_io = io.BytesIO()
        blank_img.save(blank_bytes_io, format="JPEG")
        blank_raw = blank_bytes_io.getvalue()

        for key_index in range(8):
            self.deck.set_key_image(key_index, blank_raw)

        # 2) Now render only the relevant button icons for 'page'
        #    We'll do something similar to your set_key_image function, but we
        #    only do it if the button has an image path, etc.
        #    For each row, col in page.buttons, set that key's image if any.
        print(f"Displaying page: {page.name}")

        for row_idx, row_of_buttons in enumerate(page.buttons):
            for col_idx, button in enumerate(row_of_buttons):
                if button and button.image:
                    # We'll reuse your logic to set an icon. Let's call
                    # a helper function "render_key_icon" that sets the icon 
                    # at (row_idx, col_idx).
                    self.render_key_icon(row_idx, col_idx, button.image)

    def render_key_icon(self, row, col, svg_path):
        """
        This reuses your 'set_key_image' logic on a per-(row,col) basis.
        """
        if not svg_path:
            return
        import os, io
        import cairosvg
        from PIL import Image, ImageChops

        key_index = row * 4 + col
        if not os.path.exists(svg_path):
            print(f"[WARN] Missing icon: {svg_path}")
            return

        # Convert SVG -> PNG
        png_data = cairosvg.svg2png(url=svg_path)

        # Query size
        key_w, key_h = self.deck.key_image_format()["size"]
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
            self.deck.set_key_image(key_index, final_bytes.getvalue())
