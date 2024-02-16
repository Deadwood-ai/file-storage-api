import os

import httpx
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

URL = 'http://localhost:8000/upload'


def upload_file(filename: str, platform: str):
    # get the file size in bytes
    file_size = os.path.getsize(filename)

    with open(filename, 'rb') as f:
        with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
            wrapped_file = CallbackIOWrapper(bar.update, f, 'read')
            httpx.post(URL, files={'file': wrapped_file}, data={'platform': platform})

