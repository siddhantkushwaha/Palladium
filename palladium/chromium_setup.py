import os
import json
import zipfile
import platform

from dateutil.parser import parse
from datetime import datetime

import requests
from viper.download import download


def setup(dirpath):
    """ ------ Read config/state ----------------------------------------------------------------------------------- """

    try:
        with open(os.path.join(dirpath, 'config.json'), 'r') as config_fp:
            config = json.load(config_fp)
    except:
        config = {}

    modified_time = config.get('modified_time', None)
    if modified_time is not None:
        modified_time = parse(modified_time)

    current_time = datetime.now()

    if modified_time is not None and (current_time - modified_time).days < 30:
        print('Skipping setup.')
        return

    config['modified_time'] = current_time.isoformat()

    """ ------ Harcoded values for different formats :/ ------------------------------------------------------------ """

    binary_id_by_platform = {
        'Darwin': 'mac',
        'Linux': 'linux',
        'Windows': 'win',
    }

    driver_id_by_platform = {
        'Darwin': 'mac64',
        'Linux': 'linux64',
        'Windows': 'win32',
    }

    prefix_by_platform = {
        'Darwin': 'Mac',
        'Linux': 'Linux_x64',
        'Windows': 'Win',
    }

    binary_path_by_platform = {
        'Windows': os.path.join('chrome-win', 'chrome.exe'),
        'Linux': os.path.join('chrome-linux', 'chrome'),
        'Darwin': os.path.join('chrome-mac', 'Chromium.app', 'Contents', 'MacOS', 'Chromium')
    }

    driver_path_by_platform = {
        'Windows': os.path.join('chromedriver_win32', 'chromedriver.exe'),
        'Linux': os.path.join('chromedriver_linux64', 'chromedriver'),
        'Darwin': os.path.join('chromedriver_mac64', 'chromedriver'),
    }

    """ ------ Begin download and extraction ----------------------------------------------------------------------- """

    zipdir = os.path.join(dirpath, 'chromium')
    platform_name = platform.system()

    """ ------ Get revision ---------------------------------------------------------------------------------------- """

    revision = requests.get(f'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/'
                            f'{prefix_by_platform[platform_name]}%2FLAST_CHANGE?alt=media').content.decode()

    """ ------ Get binary -------------------------------------------------------------------------------------------"""

    chromebinary_link = f'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/' \
                        f'{prefix_by_platform[platform_name]}%2F{revision}' \
                        f'%2Fchrome-{binary_id_by_platform[platform_name]}.zip?alt=media'

    chromebinary_zipname = f'chromium_{platform_name}.zip'
    chromebinary_zippath = os.path.join(zipdir, chromebinary_zipname)
    chromebinary_dir = os.path.join(zipdir, 'chromebinary')

    download(link=chromebinary_link, path=zipdir, filename=chromebinary_zipname)
    with zipfile.ZipFile(chromebinary_zippath, 'r') as zip_ref:
        zip_ref.extractall(chromebinary_dir)

    """ ------ Get driver ------------------------------------------------------------------------------------------ """

    chromedriver_version = requests.get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE').content.decode()
    chromedriver_link = f'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/' \
                        f'{prefix_by_platform[platform_name]}%2F{revision}' \
                        f'%2Fchromedriver_{driver_id_by_platform[platform_name]}.zip?alt=media'

    chromedriver_zipname = f'chromedriver_{platform_name}.zip'
    chromedriver_zippath = os.path.join(zipdir, chromedriver_zipname)
    chromedriver_dir = os.path.join(zipdir, 'chromedriver')

    download(link=chromedriver_link, path=zipdir, filename=chromedriver_zipname)
    with zipfile.ZipFile(chromedriver_zippath, 'r') as zip_ref:
        zip_ref.extractall(chromedriver_dir)

    """ ------ Output and add to config ---------------------------------------------------------------------------- """

    binary_path = os.path.join(zipdir, 'chromebinary', binary_path_by_platform[platform_name])
    driver_path = os.path.join(zipdir, 'chromedriver', driver_path_by_platform[platform_name])

    print(f'Binary path => {binary_path}')
    print(f'Driver path => {driver_path}')

    config['chromebinary'] = binary_path
    config['chromedriver'] = driver_path

    with open(os.path.join(dirpath, 'config.json'), 'w') as config_fp:
        json.dump(config, config_fp)


if __name__ == '__main__':
    setup('.')
