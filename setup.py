"""
py2app setup voor Jennifer Eye.

Gebruik:
    pip3 install py2app
    python3 setup.py py2app

De .app verschijnt in dist/Jennifer Eye.app
"""
from setuptools import setup

APP = ["jennifer_eye.py"]
OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "CFBundleName": "Jennifer Eye",
        "CFBundleDisplayName": "Jennifer Eye",
        "CFBundleIdentifier": "nl.webwerf.jennifer-eye",
        "CFBundleVersion": "1.0.0",
        "LSUIElement": True,  # Geen dock icon, alleen menubar
        "NSScreenCaptureUsageDescription": "Jennifer Eye heeft schermopname nodig om screenshots te maken.",
    },
    "packages": ["requests"],
}

setup(
    app=APP,
    name="Jennifer Eye",
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
