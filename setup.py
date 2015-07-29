import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "rgb",
        version = "0.1",
        description = "The rgb game!",
        options = {},
        executables = [Executable("src/main.py")])