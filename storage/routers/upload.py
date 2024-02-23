from typing import Annotated
from enum import Enum
import uuid
import hashlib
import time
from datetime import datetime

from pydantic import BaseModel, computed_field, field_serializer
from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer

from ..utils.settings import settings
from ..supabase_client import verify_token, use_client

# build a router for the upload endpoint
router = APIRouter()


class PlatformEnum(str, Enum):
    drone = "drone"
    airborne = "airborne"
    sattelite = "sattelite"


class LicenseEnum(str, Enum):
    cc_by = "cc-by"
    cc_by_sa = "cc-by-sa"


class StatusEnum(str, Enum):
    pending = "pending"
    processing = "processing"
    errored = "errored"
    processed = "processed"
    audited = "audited"
    audit_failed = "audit_failed"


class FileUploadMetadata(BaseModel):
    user_id: str
    aquisition_date: datetime
    upload_date: datetime
    file_name: str
    content_type: str
    file_size: int
    target_path: str
    copy_time: float
    uuid: str
    sha256: str
    platform: PlatformEnum
    license: LicenseEnum
    status: StatusEnum = StatusEnum.pending

    @computed_field
    @property
    def file_id(self) -> str:
        return f"{self.uuid}_{self.file_name}"
    
    @field_serializer('aquisition_date', 'upload_date', mode='plain')
    def datetime_to_isoformat(field: datetime) -> str:
        return field.isoformat()


# create the OAuth2 password scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/upload", status_code=201, response_model=FileUploadMetadata)
async def upload_file(
    file: UploadFile, 
    platform: Annotated[PlatformEnum, Form()],
    license: Annotated[LicenseEnum, Form()],
    aquisition_date: Annotated[datetime, Form()],
    token: Annotated[str, Depends(oauth2_scheme)]
) -> FileUploadMetadata:
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
    - platform: the platform from which the file was uploaded


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
    # first thing we do is verify the token
    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

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
        user_id=user_id,
        file_name=file.filename,
        content_type=file.content_type,
        file_size=file.size,
        target_path=str(target_path),
        copy_time=t2 - t1,
        uuid=uid,
        sha256=sha256,
        platform=platform,
        license=license,
        upload_date=datetime.utcnow(),
        aquisition_date=aquisition_date,
        status=StatusEnum.pending
    )

    # upload the metadata to supabase
    with use_client(token) as client:
        try:
            client.table(settings.metadata_table).insert(metadata.model_dump()).execute()
        except Exception as e:
            print(str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    # save the metadata to a json file of same name
    # metadata_path = settings.raw_upload_path / f"{uid}_{file.filename}.json"
    # with metadata_path.open("w") as f:
    #     f.write(metadata.model_dump_json(indent=4))

    # return the metadata
    return metadata
