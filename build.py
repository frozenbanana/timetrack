import PyInstaller.__main__
import sys
from pathlib import Path

def build():
    PyInstaller.__main__.run([
        'timetrack/cli.py',
        '--name=timetrack',
        '--onefile',
        # Optimeringar för snabbare uppstart
        '--hidden-import=click',
        '--hidden-import=json',
        '--hidden-import=pathlib',
        '--hidden-import=datetime',
        # Viktiga flaggor för macOS
        '--noconsole',  # Minskar uppstartstiden på macOS
        '--noconfirm',
        '--clean',
        # Avaktivera komprimering för snabbare uppstart
        '--noupx',
        # macOS-specifika optimeringar
        '--target-arch=arm64',  # eller 'arm64' för M1/M2
])

if __name__ == "__main__":
    build()
