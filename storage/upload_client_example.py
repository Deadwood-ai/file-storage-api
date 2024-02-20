import os

import httpx
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

URL = 'http://127.0.0.1:8000/'

# This access token is only valid for a short time. If you get token expired errors,
# use the login function to get (and set) a new access token
ACCESS_TOKEN = ""

def login(user: str, password: str) -> str:
    """
    Get an access_token to the File Server
    """
    global ACCESS_TOKEN
    
    # send a post request
    response = httpx.post(f"{URL}token", data={'username': user, 'password': password})
    
    # get the response as JSON
    auth_data = response.json()
    ACCESS_TOKEN = auth_data['access_token']

    return auth_data


def upload_file(filename: str, platform: str, license: str, aquisition_date: str):
    """
    Upload a file to the server using the `httpx` library and display a progress bar using the `tqdm` library.
    :param filename: the name of the file to upload
    :param platform: the platform that took the image. Has to be one of ['drone', 'airborne', 'sattelite']
    """
    global ACCESS_TOKEN
    if ACCESS_TOKEN is None or ACCESS_TOKEN == "":
        raise RuntimeError("You need to login first: upload_client.login(user='your_user', password='your_password')")
    
    # get the file size in bytes
    file_size = os.path.getsize(filename)

    # authorize with your deadwood-ai account
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}

    with open(filename, 'rb') as f:
        with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
            wrapped_file = CallbackIOWrapper(bar.update, f, 'read')
            httpx.post(
                f"{URL}upload",
                files={'file': wrapped_file},
                data={'platform': platform, 'license': license, 'aquisition_date': aquisition_date},
                headers=headers
            )


if __name__ == '__main__':
    try:
        import fire
        fire.Fire(upload_file)
    except ImportError:
        import sys
        upload_file(*sys.argv[1:])
