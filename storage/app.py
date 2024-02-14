from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
import hashlib
from pydantic import BaseModel

from .settings import settings
from .__version__ import __version__

app = FastAPI(
    title="Deadwood-AI Storage API",
    description="This is the Deadwood-AI Storage API. It is used to manage files uploads for the Deadwood-AI backend.",
    version=__version__,
)

# add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InfoResponse(BaseModel):
    name: str
    description: str


@app.get("/")
def info() -> InfoResponse:
    """
    Get information about the storage API.
    """
    info = InfoResponse(
        name="Deadwood-AI Storage API.",
        description="This is the Deadwood-AI Storage API. It is used to manage files uploads for the Deadwood-AI backend. If you are not a developer, you may be searching for https://deadtrees.earth",
    )

    return info


class FileUploadMetadata(BaseModel):
    filename: str
    content_type: str
    file_size: int
    target_path: str
    copy_time: float
    uuid: str
    sha256: str


@app.post("/upload")
async def upload_file(file: UploadFile) -> FileUploadMetadata:
    """
    Upload a file to the server.

    This endpoint expects a single file to be uploaded. The file will be saved to the raw upload directory and
    the following information about the file will be returned:

    - filename: the name of the file
    - content_type: the MIME type of the file
    - file_size: the size of the file in bytes
    - target_path: the path where the file was saved
    - copy_time: the time it took to save the file in seconds
    - uuid: the UUID of the file
    - sha256: the SHA256 hash of the file

    To send the file use the `multipart/form-data` content type. The file should be sent as the value of a field
    named `file`. For example, using HTML forms like this:

    ```html
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit">
    </form>
    ```

    Or using the `requests` library in Python like this:

    ```python
    import requests
    url = "http://localhost:8000/upload"
    files = {"file": open("example.txt", "rb")}
    response = requests.post(url, files=files)
    print(response.json())
    ```

    """
    # create a UUID for this file
    uid = str(uuid.uuid4())
    # save the file to the raw upload directory - add a UUID to the filename
    target_path = settings.raw_upload_path / f"{uid}_{file.filename}"

    # check if the file already exists
    if target_path.exists():
        raise ValueError(f"file already exists: {file.filename}")

    # # write the file to the target path
    t1 = time.time()
    with target_path.open("wb") as buffer:
        buffer.write(await file.read())

    # calculate the SHA256 hash of the file
    with target_path.open("rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    t2 = time.time()

    # finally return some info about the uploaded file
    metadata = FileUploadMetadata(
        filename=file.filename,
        content_type=file.content_type,
        file_size=file.size,
        target_path=str(target_path),
        copy_time=t2 - t1,
        uuid=uid,
        sha256=sha256,
    )

    # save the metadata to a json file of same name
    metadata_path = settings.raw_upload_path / f"{uid}_{file.filename}.json"
    with metadata_path.open("w") as f:
        f.write(metadata.model_dump_json(indent=4))

    # return the metadata
    return metadata
