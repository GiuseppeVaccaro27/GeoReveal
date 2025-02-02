from cx_Freeze import setup, Executable
import sys
sys.setrecursionlimit(5000)


setup(
    name="GeoReveal",
    version="1.0",
    description="My Application",
    options={
        "build_exe": {
            "excludes": ["PyQt5", "PySide2"],  # Escludi moduli non necessari
        }
    },
    executables=[Executable("Main.py")],
)
