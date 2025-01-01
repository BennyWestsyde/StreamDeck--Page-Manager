import os
import sys
import io
import asyncio
from logger import logger

import cairosvg
from PIL import Image, ImageChops
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import TouchscreenEventType, DialEventType

from classes.button import Button
from classes.page import Page
from classes.page_manager import PageManager
from functions.audio_functions import volume_up, volume_down, toggle_mic
from functions.system_functions import open_terminal, run_python_code
from functions.video_functions import open_obs, toggle_recording
import pyautogui



manager = PageManager()

def set_key_image(deck, row, col, svg_path):
    """
    Helper to load an SVG, invert if needed, and set it on the specified key (row,col).
    We'll do row*4+col to get key_index for a 4x2 deck. If your device is 4x2, that means 8 keys total.
    """
    if not os.path.exists(svg_path):
        logger.warning(f"Missing icon file: {svg_path}")
        return

    key_index = row * 4 + col
    # Convert SVG to PNG
    png_data = cairosvg.svg2png(url=svg_path)

    # Query the key dimensions
    key_w, key_h = deck.key_image_format()["size"]
    with Image.open(io.BytesIO(png_data)).convert("RGBA") as icon:
        icon = icon.resize((key_w, key_h), Image.LANCZOS)
        # Split into RGBA channels
        r, g, b, alpha = icon.split()

        # Invert ONLY the RGB channels
        rgb = Image.merge("RGB", (r, g, b))
        rgb_inverted = ImageChops.invert(rgb)

        # Merge back with original alpha
        icon_inverted = Image.merge("RGBA", (*rgb_inverted.split(), alpha))

        # Now create a new black background
        # and paste the inverted icon onto it using the alpha mask
        final_img = Image.new("RGB", (key_w, key_h), color="black")
        final_img.paste(icon_inverted, mask=icon_inverted.split()[3])
        final_bytes = io.BytesIO()
        final_img.save(final_bytes, format="JPEG")
        deck.set_key_image(key_index, final_bytes.getvalue())

async def on_key_change(deck, key_index, pressed):
    """
    Convert (key_index) => (row, col), then forward to manager.
    """
    logger.debug(f"Key change: key_index={key_index}, pressed={pressed}")
    # Only handle press down
    if pressed:
        row = key_index // 4
        col = key_index % 4
        await manager.handle_event(("button_press", row, col))
        await manager.render_current_page()

async def on_dial_callback(deck, dial_index, dial_event_type, data):
    logger.debug(f"Dial event: dial_index={dial_index}, event_type={dial_event_type}, data={data}")
    if dial_event_type == DialEventType.PUSH:
        if data:  # pressed
            await manager.handle_event(("dial_press", dial_index))
    elif dial_event_type == DialEventType.TURN:
        steps = data  # + or - int
        direction = "right" if steps > 0 else "left"
        await manager.handle_event(("dial_rotate", dial_index, direction, abs(steps)))

async def on_touch_event(deck, event_type, value):
    """
    event_type = SHORT, LONG, DRAG
    value = { 'x':..., 'y':..., 'x_out':..., 'y_out':...}
    """
    logger.debug(f"Touch event: event_type={event_type}, value={value}")
    if event_type == TouchscreenEventType.DRAG:
        x_in, y_in = value["x"], value["y"]
        x_out, y_out = value["x_out"], value["y_out"]
        if abs(x_in - x_out) > abs(y_in - y_out):
            direction = "left" if x_in > x_out else "right"
            await manager.handle_event(("led_swipe", direction))
        # else maybe up/down
    elif event_type == TouchscreenEventType.SHORT:
        await manager.handle_event(("led_tap", value["x"], value["y"]))
    elif event_type == TouchscreenEventType.LONG:
        logger.info(f"Long press at x={value['x']}, y={value['y']}")

def initialize_and_wire_buttons(deck):
    """
    Initializes the pages and buttons, and attaches the logic for navigation and actions.
    """
    deck.open()
    deck.reset()
    deck.set_brightness(50)

    # 1) Let manager know about the deck
    manager.set_deck(deck)

    # 2) Register callbacks
    deck.set_key_callback_async(on_key_change)
    deck.set_dial_callback_async(on_dial_callback)
    deck.set_touchscreen_callback_async(on_touch_event)

    # Build pages


    ###
    # MAIN PAGE
    ###
    main_page = Page(manager,"Main")

    content_page = main_page.create_child(
        "Content",
        "Icons/movie-open-outline.svg",
        (0,3))
    settings_page = main_page.create_child(
        "Settings",
        "Icons/cog.svg",
        (1,3))

    sound_page = settings_page.create_child(
        "Sound",
        "Icons/speaker-multiple.svg",
        (0,3)
    )

    mute_button = Button(
        (0,3),
        sound_page,
        "Icons/volume-high.svg",
        "Mute"
    )
    mute_button.states.add_state(
        "Icons/volume-mute.svg",
        "Unmute"
    )
    mute_button.set_async_function(toggle_mic)
    sound_page.buttons[0][3] = mute_button

    video_page = settings_page.create_child(
         "Video",
        "Icons/camera.svg",
        (1,3)
        )

    display_page = settings_page.create_child(
        "Display",
        "Icons/monitor.svg",
        (1,2)
    )


    '''
    content_btn = Button(main_page,title="Content")
    content_btn.image = "Icons/movie-open-outline.svg"
    main_page.buttons[0][3] = content_btn

    settings_btn = Button(main_page,title="Settings")
    settings_btn.image = "Icons/cog.svg"
    main_page.buttons[1][3] = settings_btn


    ###
    # CONTENT PAGE
    ###
    content_page = Page("Content", parent=main_page)
    content_page.buttons = [
        [None, None, None, None],
        [None, None, None, None]
    ]

    
    ########
    # Back #
    ########
    back_main = Button(title="Main")
    back_main.image = "Icons/arrow-left-top.svg"
    content_page.buttons[0][0] = back_main
    

    ###########
    # YouTube #
    ###########
    youtube_btn = Button(title="YouTube", image="Icons/youtube.svg")
    content_page.buttons[0][3] = youtube_btn

    ###
    # YOUTUBE PAGE
    ###
    youtube_page = Page("YouTube", parent=content_page)
    youtube_page.buttons = [
        [None, None, None, None],
        [None, None, None, None]
    ]

    ########
    # Back #
    ########
    back_content = Button(title="Content")
    back_content.image = "Icons/arrow-left-top.svg"
    back_content.set_async_function(lambda: manager.go_to_page(content_page))
    youtube_page.buttons[0][0] = back_content


    ########
    # Play #
    ########
    play_btn = Button(title="Play", image="Icons/play.svg")
    play_btn.states.add_state("Icons/pause.svg", "Pause")
    play_btn.set_async_function(lambda: pyautogui.press("space"))
    youtube_page.buttons[0][3] = play_btn

    ########
    # Stop #
    ########
    stop_btn = Button(title="Pause")
    stop_btn.image = "Icons/stop.svg"
    youtube_page.buttons[1][3] = stop_btn

    twitch_btn = Button(title="Twitch")
    content_page.buttons[1][3] = twitch_btn

    settings_page = Page("Settings", parent=main_page)
    settings_page.buttons = [
        [None, None, None, None],
        [None, None, None, None]
    ]

    back_main2 = Button(title="Main")
    back_main2.image = "Icons/arrow-left-top.svg"
    settings_page.buttons[0][0] = back_main2
    sound_btn = Button(title="Sound")
    sound_btn.image = "Icons/speaker-multiple.svg"
    settings_page.buttons[0][3] = sound_btn

    video_btn = Button(title="Video")
    video_btn.image = "Icons/camera.svg"
    settings_page.buttons[1][3] = video_btn

    display_btn = Button(title="Display")
    display_btn.image = "Icons/monitor.svg"
    settings_page.buttons[1][2] = display_btn

    sound_page = Page("Sound", parent=settings_page)
    sound_page.buttons = [
        [None, None, None, None],
        [None, None, None, None]
    ]

    back_settings = Button(title="Settings")
    back_settings.image = "Icons/arrow-left-top.svg"
    sound_page.buttons[0][0] = back_settings

    toggle_state = Button(title="Local/Broadcast")
    sound_page.buttons[0][3] = toggle_state

    toggle_output = Button(title="Toggle Output")
    sound_page.buttons[1][3] = toggle_output

    video_page = Page("Video", parent=settings_page)
    video_page.buttons = [
        [None, None, None, None],
        [None, None, None, None]
    ]

    back_settings2 = Button(title="Settings")
    back_settings2.image = "Icons/arrow-left-top.svg"
    video_page.buttons[0][0] = back_settings2

    obs_btn = Button(title="Open OBS")
    video_page.buttons[0][3] = obs_btn

    toggle_cam = Button(title="Virtual Cam")
    video_page.buttons[1][3] = toggle_cam

    display_page = Page("Display", parent=settings_page)
    display_page.buttons = [
        [None, None, None, None],
        [None, None, None, None]
    ]

    back_settings3 = Button(title="Settings")
    back_settings3.image = "Icons/arrow-left-top.svg"
    display_page.buttons[0][0] = back_settings3

    # Link pages
    main_page.add_child(content_page)
    main_page.add_child(settings_page)
    settings_page.add_child(sound_page)
    settings_page.add_child(video_page)
    settings_page.add_child(display_page)

    # Wire up button actions
    content_btn.set_async_function(lambda: manager.go_to_page(content_page))
    settings_btn.set_async_function(lambda: manager.go_to_page(settings_page))
    back_main.set_async_function(lambda: manager.go_to_page(main_page))
    youtube_btn.set_async_function(lambda: manager.go_to_page(youtube_page))
    twitch_btn.set_async_function(lambda: print("Twitch logic here."))
    back_main2.set_async_function(lambda: manager.go_to_page(main_page))
    sound_btn.set_async_function(lambda: manager.go_to_page(sound_page))
    video_btn.set_async_function(lambda: manager.go_to_page(video_page))
    display_btn.set_async_function(lambda: manager.go_to_page(display_page))
    back_settings.set_async_function(lambda: manager.go_to_page(settings_page))
    toggle_state.set_async_function(lambda: print("Toggle local/broadcast."))
    toggle_output.set_async_function(lambda: print("Toggle output."))
    back_settings2.set_async_function(lambda: manager.go_to_page(settings_page))
    obs_btn.set_async_function(lambda: print("Open OBS or call open_obs() here."))
    toggle_cam.set_async_function(lambda: print("Toggle Virtual Camera."))
    back_settings3.set_async_function(lambda: manager.go_to_page(settings_page))
    '''

    return {
        "main": main_page,
        "content": content_page,
        "settings": settings_page,
        "sound": sound_page,
        "video": video_page,
        "display": display_page,
    }


async def main():
    logger.info("Starting application...")

    decks = DeviceManager().enumerate()
    if not decks:
        logger.error("No StreamDeck found.")
        sys.exit(0)

    deck = decks[0]
    deck.open()
    deck.reset()
    deck.set_brightness(50)

    # 1) Let manager know about the deck
    manager.set_deck(deck)

    # 2) Register callbacks
    deck.set_key_callback_async(on_key_change)
    deck.set_dial_callback_async(on_dial_callback)
    deck.set_touchscreen_callback_async(on_touch_event)

    # Build pages
    pages_dict = initialize_and_wire_buttons(deck)
    # The 'main' page
    main_page = pages_dict["main"]
    await manager.set_current_page(main_page)

    logger.info("Ready. Press Ctrl+C to exit.")
    try:
        while True:
            await asyncio.sleep(0.1)  # keep the event loop alive
    except KeyboardInterrupt:
        pass
    finally:
        deck.reset()
        deck.close()


if __name__ == "__main__":
    asyncio.run(main())
