import os
import sys
import shutil
from distutils.dir_util import copy_tree

REPO = "https://github.com/PacketSurf/ZSpotifyGUI.git"
RUN_MAC = "ZSpotify.command"
RUN_WIN = "zspot-run.bat"

def update_zspotify(restart_gui=False):
    temp = "Temp"
    readme = "README.md"
    reqs = "requirements.txt"
    changes = "CHANGELOG.md"
    if os.path.isdir(temp):
        os.system(f'rm -rf {temp}')
    os.mkdir(temp)
    os.chdir(temp)
    os.system(f"git clone {REPO}")
    os.chdir("ZSpotifyGUI/")
    copy_tree("source", "../../source")
    shutil.copy(reqs, "../../")
    shutil.copy(readme, "../../")
    shutil.copy(changes, "../../")
    os.chdir("../../")
    shutil.rmtree(temp)
    os.system(f"pip3 install -r {reqs}")
    if restart_gui:
        if os.name == "nt":
            if os.path.isfile(RUN_WIN):
                os.system(RUN_WIN)
        elif os.name == "posix":
            if os.path.isfile(RUN_MAC):
                os.system(f"sh {RUN_MAC}")


if __name__ == "__main__":
    if len(sys.argv) > 0 and sys.argv[0] == "-r":
        update_zspotify(True)
    else:
        update_zspotify()