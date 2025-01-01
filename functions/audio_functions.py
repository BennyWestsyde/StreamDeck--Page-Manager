# file: functions/audio_functions.py
import subprocess

def volume_up(step=5):
    cmd = f"pactl set-sink-volume @DEFAULT_SINK@ +{step}%"
    print(cmd)
    subprocess.run(cmd, shell=True)

def volume_down(step=5):
    cmd = f"pactl set-sink-volume @DEFAULT_SINK@ -{step}%"
    print(cmd)
    subprocess.run(cmd, shell=True)

def toggle_mic():
    cmd = "pactl set-source-mute @DEFAULT_SOURCE@ toggle"
    print(cmd)
    subprocess.run(cmd, shell=True)
