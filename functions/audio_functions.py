# file: functions/audio_functions.py
import subprocess

from logger import logger


def volume_up(step=5):
    cmd = f"pactl set-sink-volume @DEFAULT_SINK@ +{step}%"
    print(cmd)
    subprocess.run(cmd, shell=True)

def volume_down(step=5):
    cmd = f"pactl set-sink-volume @DEFAULT_SINK@ -{step}%"
    print(cmd)
    subprocess.run(cmd, shell=True)

def control_volume(direction, step=5):
    logger.info(f"Changing volume: {direction} {step}")
    if direction == "left":
        volume_down(step)
    elif direction == "right":
        volume_up(step)

def toggle_mic():
    cmd = "pactl set-source-mute @DEFAULT_SOURCE@ toggle"
    print(cmd)
    subprocess.run(cmd, shell=True)
