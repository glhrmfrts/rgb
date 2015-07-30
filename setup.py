import sys, os, shutil
from cx_Freeze import setup, Executable

include_files = [("./src/"+f) for f in os.listdir('./src') if not f == "main.py"]

build_exe_options = {
	"packages": ["os"], 
	"excludes": ["tkinter"],
	"includes": ["pygame.locals", "json", "copy"],
	"include_files": include_files
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "rgb",
        version = "0.1",
        description = "The rgb game!",
        options = {"build_exe": build_exe_options},
        executables = [Executable("src/main.py", base=base, targetName="rgb.exe")])

print('copying assets')
shutil.copytree('./assets', './build/assets')