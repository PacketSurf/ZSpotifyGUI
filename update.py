import os
import sys
import shutil
from distutils.dir_util import copy_tree
import subprocess
import logging
import filecmp

logging.basicConfig(level=logging.INFO, filename="../update.log",
                        format='%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s')

REPO = "-b dev https://github.com/PacketSurf/ZSpotifyGUI.git"
RUN_MAC = "ZSpotify.command"
RUN_WIN = "RunZSpotify.bat"


def update_zspotify():
    try:
        logging.info("Starting update...")
        os.chdir('../')
        os.system('ls')
        temp = "Temp"
        reqs = "requirements.txt"
        files = [
            "README.md",
            reqs,
            "CHANGELOG.md"
        ]

        if os.path.isdir(temp):
            os.system(f'rm -rf {temp}')
        os.mkdir(temp)
        os.chdir(temp)

        logging.info(f"Cloning repository: {REPO}")
        os.system(f"git clone {REPO}")
        os.chdir("ZSpotifyGUI/")

        logging.info("Importing necessary files from repo.")
        copy_tree("source", "../../source")
        logging.info("Merged source tree.")
        can_restart = False
        if os.path.isfile(reqs) and os.path.isfile(f'../../{reqs}'):
            can_restart = filecmp.cmp(reqs, f"../../{reqs}")
            logging.info(f'Requirements identical: {can_restart}')
        for file in files:
            shutil.copy(file, "../../")
            logging.info(f"Copied {file}")
        os.chdir("../../")
        shutil.rmtree(temp)
        logging.info("Update successful!")

        if not can_restart:
            return
        if os.name == "nt":
            if os.path.isfile(RUN_WIN):
                logging.info("Restarting ZSpotifyGUI.")
                subprocess.Popen(RUN_WIN)
        elif os.name == "posix":
            if os.path.isfile(RUN_MAC):
                logging.info("Restarting ZSpotifyGUI.")
                os.system(f'sh {RUN_MAC}')
    except Exception as e:
        logging.critical(e)


if __name__ == "__main__":
    update_zspotify()
