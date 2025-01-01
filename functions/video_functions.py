# file: functions/video_functions.py
import subprocess

def open_obs():
    cmd = "obs --start"
    print(cmd)
    subprocess.Popen(cmd, shell=True)

def toggle_recording():
    print("Toggling recording in OBS")

def change_scene(scene_name="Scene"):
    print(f"Changing scene to {scene_name}")
