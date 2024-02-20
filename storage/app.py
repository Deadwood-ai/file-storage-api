from fastapi import FastAPI,  Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .__version__ import __version__
from .routers import upload, info, auth

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

# add the info route to the app
app.include_router(info.router)

# add the upload route to the app
app.include_router(upload.router)

# add the auth rout to the app
app.include_router(auth.router)

# TODO: not yet sure where to put this route
@app.get(
    "/upload_code.py",
    responses={200: {"content": {"text/x-python": {}}}},
    response_class=Response,
)
def get_code(request: Request):
    """
    Get the code for the upload client. You can request a working Python script, that can be
    used to upload files to the server. The script uses the `httpx` library to send the file
    and the `tqdm` library to display a progress bar.
    You need to make sure that you have the `httpx` and `tqdm` libraries installed to use the script.

    ```bash
    pip install httpx tqdm
    ```

    """
    # get the url of the server
    scheme = request.scope.get("scheme")
    host = request.headers.get("host")
    root_path = request.scope.get("root_path")
    url = f"{scheme}://{host}{root_path}"

    # try to read it first
    with open(Path(__file__).parent / "upload_client_example.py", "r") as f:
        code = f.read()

    # replace the localhost url with the actual server url
    code = code.replace("http://127.0.0.1:8000/", url)

    # create headers for attachement disposition and filename
    headers = {"Content-Disposition": "attachment; filename=upload_client.py"}

    # create a FastAPI response with content type of Python files
    return Response(content=code, media_type="text/x-python", headers=headers)
