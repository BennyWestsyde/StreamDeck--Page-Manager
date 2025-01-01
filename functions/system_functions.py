# file: functions/system_functions.py
import subprocess

def open_terminal():
    cmd = "gnome-terminal"
    print(cmd)
    subprocess.Popen(cmd, shell=True)

def run_python_code(code="print('Hello')"):
    cmd = f"python3 -c \"{code}\""
    print(cmd)
    subprocess.run(cmd, shell=True)
