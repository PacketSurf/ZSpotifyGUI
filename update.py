import time
import requests
import os
import subprocess
from source.const import REPO, REPO_API, UPDATED_AT
from source.config import Config, LAST_UPDATED

def update_zspotify(restart_gui=False):
    temp = "Temp"
    readme = "README.md"
    reqs = "requirements.txt"
    changes = "CHANGELOG.md"
    os.mkdir(temp)
    os.system(f"cd {temp}")
    os.system(f"git clone {REPO}")
    os.system(f'rm ../{reqs}')
    os.system(f'rm ../{readme}')
    os.system(f'rm ../{changes}')
    os.system(f'cp ../{reqs}')
    os.system(f'cp ../{readme}')
    os.system(f'cp ../{changes}')
    if os.name == "nt":
        print('nice')
    else:
        os.system(f'rsync -arv {temp}/ZSpotifyGUI/source ../')
    os.system('cd ../')
    os.rmdir(f'rm -rf {temp}')
    #if restart_gui:
     #   subprocess.Popen()



def is_up_to_date():
    last_updated = Config.get_last_updated()
    result = requests.get(REPO_API)
    data = result.json()
    new_last_updated = data[UPDATED_AT]
    if last_updated == "-":
        Config.set(LAST_UPDATED, new_last_updated)
        return True
    up_date, up_time = parse_updated_str(last_updated)
    new_up_date, new_up_time = parse_updated_str(new_last_updated)
    if new_up_date < up_date:
        return True
    elif new_up_date == up_date:
        if new_up_time >= up_time:
            return True
    return False


def parse_updated_str(updated_str: str):
    if "T" not in updated_str:
        return None, None
    split = updated_str.split("T")
    if len(split) < 1:
        return None, None
    up_date = time.strptime(split[0], '%Y-%m-%d')
    time_str = split[1].replace("Z", "")
    up_info = time.strptime(time_str, '%I:%M:%S')
    return up_date, up_info


if __name__ == "__main__":
    update_zspotify()