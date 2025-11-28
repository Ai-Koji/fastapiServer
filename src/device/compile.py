import os
import sys
import PyInstaller.__main__

##################
# start script

PyInstaller.__main__.run([
    "start.py",
    '--onefile',
    '--noconsole',
    '--name=autostart',
    '--clean',
    '--noconfirm',
    '--distpath=build/'
])

##################
# program script

current_dir = os.path.dirname(os.path.abspath(__file__))
start_script = os.path.join(current_dir, "start.py")

PyInstaller.__main__.run([
    "program/program.py",
    '--noconsole',
    '--onefile',
    '--name=program',
    '--clean',
    '--noconfirm',
    '--distpath=build/'
])
