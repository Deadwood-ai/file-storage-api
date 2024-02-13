# file-storage-api
FastAPI backend for the Deadwood-AI file storage server

To test it locally, install all dependencies and run it locally

```bash
pip install -r requirements.txt
uvicorn storage.app:app --reload
```

Then, open the swagger-ui docs at `http://localhost:8000/docs` (or alternatively ReDoc at `http://localhost:8000/redoc`).

