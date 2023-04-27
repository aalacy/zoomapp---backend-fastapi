from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "NoteAI API"
    zoom_account_id: str
    zoom_client_id:  str
    zoom_client_secret:  str
    zoom_api_key: str
    zoom_api_secret: str

    class Config:
        env_file = ".env"