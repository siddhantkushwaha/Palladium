import json
import os
import platform
import shutil
import stat
import zipfile
from datetime import datetime

import pandas as pd
import requests
from dateutil.parser import parse
from viper.common import chmod
from viper.download import download


def read_state(dirpath):
    try:
        with open(os.path.join(dirpath, 'state.json'), 'r') as config_fp:
            config = json.load(config_fp)
    except:
        config = {}

    return config


def write_state(dirpath, binary_path, driver_path):
    config = {'modified_time': datetime.now().isoformat(), 'chromium': binary_path, 'chromedriver': driver_path}
    with open(os.path.join(dirpath, 'state.json'), 'w') as config_fp:
        json.dump(config, config_fp)


def setup(path, start_over=False):
    dirpath = os.path.join(path, 'assets')
    if start_over and os.path.exists(dirpath):
        shutil.rmtree(dirpath)

    state = read_state(dirpath)

    modified_time = state.get('modified_time', None)
    if modified_time is not None:
        modified_time = parse(modified_time)

    current_time = datetime.now()

    if modified_time is not None and (current_time - modified_time).days < 30:
        return

    binary_pt, driver_pt = shell(dirpath)

    write_state(dirpath, binary_pt, driver_pt)


def shell(dir_path):
    """ ------ Harcoded values for different formats :/ ------------------------------------------------------------ """

    prefix_by_platform = {
        'Darwin': 'Mac',
        'Linux': 'Linux_x64',
        'Windows': 'Win',
    }

    platform_info = platform.uname()
    platform_name = platform_info.system

    prefix = prefix_by_platform[platform_name]

    # web api - do not delete
    # index_url = f'http://commondatastorage.googleapis.com/' \
    #             f'chromium-browser-snapshots/index.html?prefix={prefix}/{revision}/'

    last_change = f'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/{prefix}%2FLAST_CHANGE?alt=media'
    revision = int(requests.get(last_change).content)

    storage_api_url = f'https://www.googleapis.com/' \
                      f'storage/v1/b/chromium-browser-snapshots/o?delimiter=/&prefix={prefix}/{revision}/' \
                      f'&fields=items(kind,mediaLink,metadata,name,size,updated),kind,prefixes,nextPageToken'

    storage_api_data = requests.get(storage_api_url).content
    storage_api_data = json.loads(storage_api_data.decode())
    storage_api_data = storage_api_data.get('items')

    if storage_api_data is None:
        raise Exception('No information found from storage api location.')

    storage_api_info = pd.DataFrame(storage_api_data)

    # filter out useless binaries
    storage_api_info = storage_api_info[(storage_api_info['name'].str.contains('chrome'))
                                        & (~storage_api_info['name'].str.contains('sym'))]

    chromium_binaries = storage_api_info[~storage_api_info['name'].str.contains('driver')]
    if len(chromium_binaries) < 1:
        raise Exception(f'No binaries found for revision {revision}.')

    chromedriver_binaries = storage_api_info[storage_api_info['name'].str.contains('driver')]
    if len(chromedriver_binaries) < 1:
        raise Exception(f'No chromedriver found for revision {revision}.')

    chromium_download_link = list(chromium_binaries['mediaLink'])[0]
    chromedriver_download_link = list(chromedriver_binaries['mediaLink'])[0]

    """ ------------------------------------------ Begin download and extraction ----------------------------------- """
    zipdir = os.path.join(dir_path, 'chromium')

    chromebinary_zipname = 'chromium.zip'
    chromebinary_zippath = os.path.join(zipdir, chromebinary_zipname)
    chromebinary_dir = os.path.join(zipdir, 'chromium')

    download(link=chromium_download_link, path=zipdir, filename=chromebinary_zipname)
    with zipfile.ZipFile(chromebinary_zippath, 'r') as zip_ref:
        zip_ref.extractall(chromebinary_dir)

    chromedriver_zipname = f'chromedriver.zip'
    chromedriver_zippath = os.path.join(zipdir, chromedriver_zipname)
    chromedriver_dir = os.path.join(zipdir, 'chromedriver')

    download(link=chromedriver_download_link, path=zipdir, filename=chromedriver_zipname)
    with zipfile.ZipFile(chromedriver_zippath, 'r') as zip_ref:
        zip_ref.extractall(chromedriver_dir)

    chmod(zipdir, stat.S_IRWXU)

    os.remove(chromebinary_zippath)
    os.remove(chromedriver_zippath)

    """ -------------------------------------------- Return paths -------------------------------------------------- """
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

    binary_path = os.path.join(zipdir, 'chromium', binary_path_by_platform[platform_name])
    driver_path = os.path.join(zipdir, 'chromedriver', driver_path_by_platform[platform_name])

    return os.path.abspath(binary_path), os.path.abspath(driver_path)


if __name__ == '__main__':
    setup('.', start_over=True)
