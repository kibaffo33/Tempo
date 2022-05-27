from setuptools import setup

NAME = "Tempo"
APP = ["tempo.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": True,
    "iconfile": "clock.png",
    "plist": {
        "CFBundleShortVersionString": "0.2.0",
        "LSUIElement": True,
    },
    "packages": ["rumps"],
}

setup(app=APP, name=NAME, data_files=DATA_FILES, options={"py2app": OPTIONS}, setup_requires=["py2app"], install_requires=["rumps"], version="0.0.1")
