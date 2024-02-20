import os

import httpx
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

URL = 'http://localhost:8000/upload'


def upload_file(filename: str, platform: str):
    """
    Upload a file to the server using the `httpx` library and display a progress bar using the `tqdm` library.
    :param filename: the name of the file to upload
    :param platform: the platform that took the image. Has to be one of ['drone', 'airborne', 'sattelite']
    """
    # get the file size in bytes
    file_size = os.path.getsize(filename)

    with open(filename, 'rb') as f:
        with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
            wrapped_file = CallbackIOWrapper(bar.update, f, 'read')
            httpx.post(URL, files={'file': wrapped_file}, data={'platform': platform})


if __name__ == '__main__':
    try:
        import fire
        fire.Fire(upload_file)
    except ImportError:
        import sys
        upload_file(*sys.argv[1:])
