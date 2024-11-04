import PyInstaller.__main__
import sys
from pathlib import Path

def build():
    PyInstaller.__main__.run([
        'timetrack/cli.py',               # your main script
        '--name=timetrack',               # name of the executable
        '--onefile',                      # create a single executable
        '--clean',                        # clean cache before building
        '--add-data=README.md:.',         # include README
        '--hidden-import=click',          # ensure click is included
    ])

if __name__ == "__main__":
    build()
