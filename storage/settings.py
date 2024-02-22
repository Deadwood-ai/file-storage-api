from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path

# load an .env file if it exists
load_dotenv()


BASE = str(Path(__file__).parent.parent / "data")


# load the settings from environment variables
class Settings(BaseSettings):
    # base directory for the storage app
    base_dir: str = BASE

    # location for raw file uploads
    raw_upload_dir: str = "raw_uploads"

    # supabase settings for supabase authentication
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # some basic settings for the UVICORN server
    uvicorn_host: str = "127.0.0.1"
    uvicorn_port: int = 8000
    uvicorn_root_path: str = "/"
    uvicorn_proxy_headers: bool = True

    # supabase settings
    metadata_table: str = 'metadata'

    @property
    def base_path(self) -> Path:
        path = Path(self.base_dir)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        
        return path
    
    @property
    def raw_upload_path(self) -> Path:
        path = self.base_path / self.raw_upload_dir
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        
        return path


# implement singleton pattern for settings
__SINGLETON_SETTINGS = None


def get_settings() -> Settings:
    global __SINGLETON_SETTINGS
    if __SINGLETON_SETTINGS is None:
        __SINGLETON_SETTINGS = Settings()
    return __SINGLETON_SETTINGS


settings = get_settings()
